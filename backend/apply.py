import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from datetime import datetime
from pathlib import Path
import urllib.parse
import re
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

class JobApplicator:
    def __init__(self, profile):
        self.profile = profile
        self.driver = None
        self.setup_driver()
        self.applications_log = Path('applications_log.csv')
        self.initialize_log()
        self.linkedin_logged_in = False
        self.api_base_url = os.getenv('API_BASE_URL', 'http://localhost:5000/api')

    def setup_driver(self):
        """Initialize the web driver with appropriate options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        # Uncomment the line below if you want to run in headless mode
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def initialize_log(self):
        """Initialize or load the applications log"""
        if not self.applications_log.exists():
            df = pd.DataFrame(columns=[
                'date', 'job_title', 'company', 'url', 'status',
                'application_type', 'notes'
            ])
            df.to_csv(self.applications_log, index=False)

    def log_application(self, job, status, application_type, notes=''):
        """Log the application details"""
        df = pd.read_csv(self.applications_log)
        new_row = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'job_title': job['title'],
            'company': job['company'],
            'url': job['url'],
            'status': status,
            'application_type': application_type,
            'notes': notes
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.applications_log, index=False)

    def login_to_linkedin(self):
        """Check LinkedIn authentication status"""
        if self.linkedin_logged_in:
            return True

        try:
            print("Checking LinkedIn authentication...")
            
            # Check if user is authenticated by getting their profile
            response = requests.get(f"{self.api_base_url}/auth/linkedin/profile")
            
            if response.status_code == 200:
                print("Successfully authenticated with LinkedIn")
                self.linkedin_logged_in = True
                return True
            else:
                print("Not authenticated with LinkedIn. Please authenticate through the frontend.")
                return False

        except Exception as e:
            print(f"Error checking LinkedIn authentication: {str(e)}")
            return False

    def get_job_details(self, job_url):
        """Extract job details from the LinkedIn job page"""
        try:
            self.driver.get(job_url)
            time.sleep(3)

            # Wait for the job details to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-unified-top-card"))
            )

            # Get job title
            title = self._safe_get_text("h1.job-details-jobs-unified-top-card__job-title", "Unknown Title")

            # Get company name
            company = self._safe_get_text("span.job-details-jobs-unified-top-card__company-name", "Unknown Company")

            # Get location
            location = self._safe_get_text("span.job-details-jobs-unified-top-card__bullet", "Location not specified")

            # Get posted date
            posted_date = self._safe_get_text("span.job-details-jobs-unified-top-card__posted-date", "Date not specified")

            # Get experience level
            experience_level = "Experience level not specified"
            try:
                criteria_list = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "li.job-details-jobs-unified-top-card__job-insight"
                )
                for criteria in criteria_list:
                    if "experience" in criteria.text.lower():
                        experience_level = criteria.text
                        break
            except NoSuchElementException:
                pass

            # Get job description
            description = self._safe_get_text(
                "div.job-details-jobs-unified-top-card__job-description",
                "Description not available"
            )

            return {
                'title': title,
                'company': company,
                'location': location,
                'posted_date': posted_date,
                'experience_level': experience_level,
                'description': description
            }
        except Exception as e:
            print(f"Error getting job details: {str(e)}")
            return None

    def _safe_get_text(self, selector, default="Not specified"):
        """Safely get text from an element"""
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element.text.strip()
        except (TimeoutException, NoSuchElementException):
            return default

    def apply_to_job(self, job):
        """
        Apply to a job using the appropriate method
        
        Args:
            job (dict): Job details including title, company, and URL
        """
        try:
            # Ensure we're logged into LinkedIn
            if not self.login_to_linkedin():
                raise Exception("Failed to login to LinkedIn")

            # Get updated job details from the page
            job_details = self.get_job_details(job['url'])
            if job_details:
                job.update(job_details)
            
            # Print complete job details
            print("\nJob Details:")
            print(f"Title: {job.get('title', 'Unknown Title')}")
            print(f"Company: {job.get('company', 'Unknown Company')}")
            print(f"Location: {job.get('location', 'Location not specified')}")
            print(f"Posted: {job.get('posted_date', 'Date not specified')}")
            print(f"Experience Level: {job.get('experience_level', 'Experience level not specified')}")
            print(f"URL: {job.get('url', 'URL not available')}")
            
            if job.get('description'):
                print("\nJob Description:")
                print(job['description'][:500] + "..." if len(job['description']) > 500 else job['description'])
            print("\n")

            # Try Easy Apply first
            if self.try_easy_apply(job):
                return

            # If Easy Apply is not available, try normal application
            self.apply_normal(job)

        except Exception as e:
            print(f"Error applying to {job.get('title', 'Unknown')} at {job.get('company', 'Unknown Company')}: {str(e)}")
            self.log_application(job, 'Failed', 'Unknown', str(e))

    def try_easy_apply(self, job):
        """Attempt to use LinkedIn Easy Apply"""
        try:
            print(f"Attempting Easy Apply for: {job['title']} at {job['company']}")
            
            # Wait for the page to load completely
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-unified-top-card"))
            )
            
            # Look for Easy Apply button
            try:
                # First try the main Easy Apply button
                easy_apply_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jobs-apply-button"))
                )
                print("Found Easy Apply button, clicking...")
                easy_apply_button.click()
                time.sleep(2)

                # Wait for the application form to appear
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-easy-apply-content"))
                )
                
                # Fill out the application form
                if self.fill_linkedin_form():
                    # Submit the application
                    submit_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-control-name='submit_unify']"))
                    )
                    submit_button.click()
                    time.sleep(2)
                    
                    # Check for success message
                    try:
                        success_message = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-easy-apply-success"))
                        )
                        print("Application submitted successfully!")
                        self.log_application(job, 'Applied', 'LinkedIn Easy Apply')
                        return True
                    except TimeoutException:
                        print("Application might have been submitted, but no success message found")
                        self.log_application(job, 'Applied', 'LinkedIn Easy Apply', 'No success message')
                        return True
                
            except TimeoutException:
                print(f"LinkedIn Easy Apply not available for {job['title']} at {job['company']}")
                return False
                
        except Exception as e:
            print(f"Error in Easy Apply attempt: {str(e)}")
            return False

    def apply_normal(self, job):
        """Handle normal LinkedIn application process"""
        try:
            print(f"Attempting normal application for: {job['title']} at {job['company']}")
            
            # Look for "Apply" button
            try:
                apply_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-control-name='jobdetails_topcard_applybutton']"))
                )
                apply_button.click()
                time.sleep(2)

                # Get the external application URL
                external_url = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-control-name='jobdetails_topcard_applybutton']"))
                ).get_attribute('href')

                print(f"External application URL: {external_url}")
                self.log_application(job, 'External Link', 'Normal Application', f'Apply at: {external_url}')
                
                # Open the external application page
                self.driver.get(external_url)
                time.sleep(3)
                
                print("Please complete the application manually on the external website.")
                
            except TimeoutException:
                print(f"Could not find application button for {job['title']} at {job['company']}")
                self.log_application(job, 'Not Applied', 'Normal Application', 'Application button not found')
                
        except Exception as e:
            print(f"Error in normal application attempt: {str(e)}")
            self.log_application(job, 'Failed', 'Normal Application', str(e))

    def fill_linkedin_form(self):
        """Fill out the LinkedIn Easy Apply form"""
        try:
            print("Filling out application form...")
            
            # Wait for the form to be fully loaded
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-easy-apply-content"))
            )

            # Handle phone number
            try:
                phone_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='phoneNumber']"))
                )
                phone_field.clear()
                phone_field.send_keys(self.profile.get('phone', ''))
                print("Phone number entered")
            except TimeoutException:
                print("Phone field not found or not required")

            # Handle resume upload
            try:
                resume_upload = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                resume_path = os.path.join(os.getcwd(), 'resume.pdf')
                if os.path.exists(resume_path):
                    resume_upload.send_keys(resume_path)
                    print("Resume uploaded")
                else:
                    print("Resume file not found at:", resume_path)
            except TimeoutException:
                print("Resume upload not required or already uploaded")

            # Handle additional questions
            if self.handle_additional_questions():
                print("Additional questions handled successfully")
            else:
                print("Some questions might not have been answered")

            return True

        except Exception as e:
            print(f"Error filling LinkedIn form: {str(e)}")
            return False

    def handle_additional_questions(self):
        """Handle additional questions in the application form"""
        try:
            # Look for all question elements
            questions = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".jobs-easy-apply-form-element"))
            )
            
            for question in questions:
                try:
                    # Get question text
                    question_text = question.find_element(By.CSS_SELECTOR, "label").text.lower()
                    print(f"Handling question: {question_text}")
                    
                    # Handle different question types
                    if "years of experience" in question_text:
                        self.handle_experience_question(question)
                    elif "salary" in question_text:
                        self.handle_salary_question(question)
                    elif "visa" in question_text or "sponsorship" in question_text:
                        self.handle_visa_question(question)
                    elif "relocation" in question_text:
                        self.handle_relocation_question(question)
                    else:
                        # Default handling for other questions
                        self.handle_generic_question(question)
                        
                except Exception as e:
                    print(f"Error handling question: {str(e)}")
                    continue
            
            return True
                    
        except Exception as e:
            print(f"Error handling additional questions: {str(e)}")
            return False

    def handle_experience_question(self, question):
        """Handle years of experience question"""
        try:
            input_field = question.find_element(By.CSS_SELECTOR, "input[type='number']")
            input_field.clear()
            input_field.send_keys(self.profile.get('years_experience', '5'))
        except Exception as e:
            print(f"Error handling experience question: {str(e)}")

    def handle_salary_question(self, question):
        """Handle salary expectation question"""
        try:
            input_field = question.find_element(By.CSS_SELECTOR, "input[type='text']")
            input_field.clear()
            input_field.send_keys(self.profile.get('salary_expectation', '100000'))
        except Exception as e:
            print(f"Error handling salary question: {str(e)}")

    def handle_visa_question(self, question):
        """Handle visa sponsorship question"""
        try:
            # Try to find radio buttons
            radio_buttons = question.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            if radio_buttons:
                # Select "Yes" if available
                for radio in radio_buttons:
                    if "yes" in radio.get_attribute("value").lower():
                        radio.click()
                        break
        except Exception as e:
            print(f"Error handling visa question: {str(e)}")

    def handle_relocation_question(self, question):
        """Handle relocation question"""
        try:
            # Try to find radio buttons
            radio_buttons = question.find_element(By.CSS_SELECTOR, "input[type='radio']")
            if radio_buttons:
                # Select "Yes" if available
                for radio in radio_buttons:
                    if "yes" in radio.get_attribute("value").lower():
                        radio.click()
                        break
        except Exception as e:
            print(f"Error handling relocation question: {str(e)}")

    def handle_generic_question(self, question):
        """Handle generic questions with text input"""
        try:
            # Try to find text input
            input_field = question.find_element(By.CSS_SELECTOR, "input[type='text']")
            input_field.clear()
            input_field.send_keys("Yes")
        except Exception as e:
            print(f"Error handling generic question: {str(e)}")

    def close(self):
        """Close the web driver"""
        if self.driver:
            self.driver.quit()

    def search_jobs(self, keywords, location=None, experience_level=None, limit=50):
        """
        Search for jobs on LinkedIn
        
        Args:
            keywords (str): Job title or keywords to search for
            location (str, optional): Location to search in
            experience_level (str, optional): Experience level filter
            limit (int, optional): Maximum number of jobs to return
        """
        try:
            # Ensure we're logged into LinkedIn
            if not self.login_to_linkedin():
                raise Exception("Failed to login to LinkedIn")

            # Construct the search URL with parameters
            base_url = "https://www.linkedin.com/jobs/search/?"
            params = {
                'keywords': keywords,
                'location': location if location else '',
                'f_E': self._get_experience_level_code(experience_level) if experience_level else '',
                'f_TPR': 'r86400',  # Last 24 hours
                'f_WT': '2',  # Remote jobs
                'position': '1',
                'pageNum': '0'
            }
            
            # Remove empty parameters
            params = {k: v for k, v in params.items() if v}
            
            # Construct the final URL
            search_url = base_url + '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
            print(f"Searching jobs with URL: {search_url}")
            
            # Navigate to the search page
            self.driver.get(search_url)
            time.sleep(3)

            # Wait for job cards to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-card-container"))
            )

            jobs = []
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while len(jobs) < limit:
                # Get all job cards
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")
                
                for card in job_cards:
                    if len(jobs) >= limit:
                        break
                        
                    try:
                        # Extract job details
                        title = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title").text
                        company = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle").text
                        
                        # Get job URL
                        url_element = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
                        url = url_element.get_attribute("href")
                        
                        # Get location
                        try:
                            location = card.find_element(By.CSS_SELECTOR, "span.job-search-card__location").text
                        except NoSuchElementException:
                            location = "Location not specified"
                            
                        # Get posted date
                        try:
                            posted_date = card.find_element(By.CSS_SELECTOR, "time").text
                        except NoSuchElementException:
                            posted_date = "Date not specified"
                            
                        # Get experience level
                        try:
                            experience = card.find_element(By.CSS_SELECTOR, "span.job-search-card__metadata-item").text
                        except NoSuchElementException:
                            experience = "Experience not specified"
                        
                        job = {
                            'title': title,
                            'company': company,
                            'location': location,
                            'posted_date': posted_date,
                            'experience_level': experience,
                            'url': url
                        }
                        
                        if job not in jobs:  # Avoid duplicates
                            jobs.append(job)
                            print(f"Found job: {title} at {company}")
                            
                    except Exception as e:
                        print(f"Error extracting job details: {str(e)}")
                        continue
                
                # Scroll to load more jobs
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Check if we've reached the end of the page
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            print(f"Found {len(jobs)} jobs matching the criteria")
            return jobs
            
        except Exception as e:
            print(f"Error searching jobs: {str(e)}")
            return []

    def _get_experience_level_code(self, experience_level):
        """
        Convert experience level to LinkedIn's filter code
        
        Args:
            experience_level (str): Experience level (e.g., 'entry', 'mid', 'senior')
            
        Returns:
            str: LinkedIn's experience level filter code
        """
        experience_levels = {
            'entry': '1',  # Entry level
            'mid': '2',    # Mid-Senior level
            'senior': '3', # Senior level
            'executive': '4'  # Executive level
        }
        return experience_levels.get(experience_level.lower(), '')

def apply_to_job(profile, job):
    """
    Main function to apply to a job
    
    Args:
        profile (dict): User profile
        job (dict): Job details
    """
    applicator = JobApplicator(profile)
    try:
        applicator.apply_to_job(job)
    finally:
        applicator.close() 