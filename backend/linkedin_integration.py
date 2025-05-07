import os
from linkedin_api import Linkedin
from dotenv import load_dotenv
import time
import pickle
from pathlib import Path
import urllib.parse
import json

# Load environment variables
load_dotenv()

class LinkedInJobSearch:
    def __init__(self):
        self.api = None
        self.cookie_file = Path('linkedin_cookies.pkl')
        self.authenticate()

    def authenticate(self):
        """Authenticate with LinkedIn API with challenge handling"""
        try:
            # Try to load existing cookies
            if self.cookie_file.exists():
                with open(self.cookie_file, 'rb') as f:
                    cookies = pickle.load(f)
                    self.api = Linkedin(
                        os.getenv('LINKEDIN_EMAIL'),
                        os.getenv('LINKEDIN_PASSWORD'),
                        cookies=cookies
                    )
                    return

            # If no cookies exist, perform fresh authentication
            self.api = Linkedin(
                os.getenv('LINKEDIN_EMAIL'),
                os.getenv('LINKEDIN_PASSWORD'),
                debug=True  # Enable debug mode to see authentication process
            )
            
            # Save cookies for future use
            with open(self.cookie_file, 'wb') as f:
                pickle.dump(self.api.client.cookies, f)
                
        except Exception as e:
            print(f"LinkedIn authentication failed: {str(e)}")
            print("\nTo resolve this issue:")
            print("1. Make sure your LinkedIn credentials in .env are correct")
            print("2. Try logging into LinkedIn in your browser first")
            print("3. If you're using 2FA, you may need to generate an app password")
            print("4. Delete linkedin_cookies.pkl if it exists and try again")
            raise

    def construct_job_url(self, job):
        """Construct a valid LinkedIn job URL"""
        try:
            # Get the job ID from the correct location in the response
            job_id = job.get('entityUrn', '').split(':')[-1] if 'entityUrn' in job else job.get('id', '')
            if not job_id:
                print("No job ID found in:", job)
                return None

            # Construct the URL in the format: https://www.linkedin.com/jobs/view/{job_id}/
            url = f"https://www.linkedin.com/jobs/view/{job_id}/"
            return url
            
        except Exception as e:
            print(f"Error constructing job URL: {str(e)}")
            return None

    def search_jobs(self, keywords, location=None, experience_level=None, limit=50):
        """
        Search for jobs on LinkedIn
        
        Args:
            keywords (str): Job search keywords
            location (str, optional): Location to search in
            experience_level (str, optional): Experience level (ENTRY_LEVEL, MID_SENIOR, SENIOR, etc.)
            limit (int): Maximum number of jobs to return
            
        Returns:
            list: List of job dictionaries with title, company, description, and URL
        """
        try:
            # Add delay to avoid rate limiting
            time.sleep(2)
            
            # Construct search parameters
            search_params = {
                'keywords': keywords,
                'location': location,
                'experience_level': experience_level,
                'limit': limit
            }
            
            print(f"\nSearching LinkedIn with parameters: {search_params}")
            
            # Search for jobs
            jobs = self.api.search_jobs(**search_params)
            print(f"\nFound {len(jobs) if jobs else 0} jobs from LinkedIn API")
            
            # Print raw data of first job for debugging
            if jobs:
                print("\nDEBUG: Raw data of first job:")
                print(json.dumps(jobs[0], indent=2))
            
            # Format job results
            formatted_jobs = []
            for job in jobs:
                try:
                    # Extract job details with improved company name extraction
                    job_title = job.get('title', {}).get('text', '') if isinstance(job.get('title'), dict) else job.get('title', '')
                    
                    # Improved company name extraction with detailed debugging
                    company_name = ''
                    print("\nDEBUG: Attempting to extract company name...")
                    
                    # Try all possible company name fields
                    company_fields = [
                        'companyName',
                        'company',
                        'formattedCompanyName',
                        'primaryDescription',
                        'companyDetails',
                        'companyInfo'
                    ]
                    
                    for field in company_fields:
                        if field in job:
                            print(f"Found field '{field}': {job[field]}")
                            if isinstance(job[field], dict):
                                if 'text' in job[field]:
                                    company_name = job[field]['text'].split('·')[0].strip()
                                elif 'name' in job[field]:
                                    company_name = job[field]['name']
                            elif isinstance(job[field], str):
                                company_name = job[field].split('·')[0].strip()
                            if company_name:
                                print(f"Extracted company name from {field}: {company_name}")
                                break
                    
                    # If still no company name, try primaryDescription as last resort
                    if not company_name and 'primaryDescription' in job:
                        print("Trying primaryDescription as last resort...")
                        if isinstance(job['primaryDescription'], dict):
                            company_text = job['primaryDescription'].get('text', '')
                            if company_text:
                                company_name = company_text.split('·')[0].strip()
                        elif isinstance(job['primaryDescription'], str):
                            company_text = job['primaryDescription']
                            if company_text:
                                company_name = company_text.split('·')[0].strip()
                    
                    # Clean up company name
                    if company_name:
                        company_name = company_name.strip()
                        company_name = company_name.replace('·', '').strip()
                        print(f"Final cleaned company name: {company_name}")
                    else:
                        print("WARNING: Could not extract company name from any field")
                    
                    location = job.get('secondaryDescription', {}).get('text', '') if isinstance(job.get('secondaryDescription'), dict) else job.get('secondaryDescription', '')
                    description = job.get('description', {}).get('text', '') if isinstance(job.get('description'), dict) else job.get('description', '')
                    
                    # Extract posted date
                    posted_date = None
                    if 'listedAt' in job and job['listedAt']:
                        try:
                            posted_date = time.strftime('%Y-%m-%d', time.localtime(job['listedAt']/1000))
                        except:
                            posted_date = time.strftime('%Y-%m-%d')
                    
                    # Extract experience level
                    experience_level = job.get('experienceLevel', '')
                    if not experience_level:
                        for field in ['formattedExperienceLevel', 'experienceLevel']:
                            if field in job:
                                experience_level = job[field]
                                break
                    
                    # Get job ID
                    job_id = job.get('entityUrn', '').split(':')[-1] if 'entityUrn' in job else job.get('id', '')
                    
                    # Construct the job URL
                    job_url = self.construct_job_url(job)
                    if not job_url:
                        continue

                    formatted_job = {
                        'title': job_title or 'Unknown Title',
                        'company': company_name or 'Unknown Company',
                        'description': description or 'Description not available',
                        'url': job_url,
                        'job_id': job_id,
                        'location': location or 'Location not specified',
                        'posted_date': posted_date or time.strftime('%Y-%m-%d'),
                        'experience_level': experience_level or 'Experience level not specified'
                    }
                    
                    # Print job details for debugging
                    print(f"\nFound job:")
                    print(f"Title: {formatted_job['title']}")
                    print(f"Company: {formatted_job['company']}")
                    print(f"Location: {formatted_job['location']}")
                    print(f"Posted: {formatted_job['posted_date']}")
                    print(f"Experience: {formatted_job['experience_level']}")
                    print(f"URL: {formatted_job['url']}")
                    
                    formatted_jobs.append(formatted_job)
                    
                except Exception as e:
                    print(f"Error formatting job: {str(e)}")
                    print("Job data:", json.dumps(job, indent=2))
                    continue
            
            return formatted_jobs
            
        except Exception as e:
            print(f"Error searching LinkedIn jobs: {str(e)}")
            # If we get an authentication error, try to re-authenticate
            if "CHALLENGE" in str(e) or "authentication" in str(e).lower():
                print("Attempting to re-authenticate...")
                if self.cookie_file.exists():
                    self.cookie_file.unlink()  # Delete the cookie file
                self.authenticate()
                return self.search_jobs(keywords, location, experience_level, limit)
            return []

    def _extract_nested_value(self, data, key, nested_key=None, default=''):
        """
        Safely extract a value from nested dictionary structure
        
        Args:
            data (dict): The dictionary to extract from
            key (str): The main key to look for
            nested_key (str, optional): The nested key to look for
            default (str): Default value if key is not found
            
        Returns:
            str: The extracted value or default
        """
        try:
            if nested_key:
                return data.get(key, {}).get(nested_key, default)
            return data.get(key, default)
        except Exception:
            return default

    def get_job_details(self, job_id):
        """
        Get detailed information about a specific job
        
        Args:
            job_id (str): LinkedIn job ID
            
        Returns:
            dict: Detailed job information
        """
        try:
            time.sleep(1)  # Add delay to avoid rate limiting
            job_details = self.api.get_job(job_id)
            print(f"Job details: {job_details}")
            return job_details
        except Exception as e:
            print(f"Error getting job details: {str(e)}")
            return None 