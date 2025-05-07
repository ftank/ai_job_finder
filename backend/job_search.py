from linkedin_integration import LinkedInJobSearch
import pandas as pd
from datetime import datetime
import time

def search_jobs(profile):
    """
    Search for jobs using LinkedIn integration and return matching jobs for manual application
    
    Args:
        profile (dict): User profile extracted from resume
        
    Returns:
        list: List of matching jobs with their details and URLs
    """
    try:
        # Initialize LinkedIn job search
        linkedin = LinkedInJobSearch()
        
        # Extract relevant keywords from profile
        keywords = extract_keywords(profile)
        
        # Search for jobs
        jobs = linkedin.search_jobs(
            keywords=keywords,
            location=profile.get('location'),
            experience_level=profile.get('experience_level'),
            limit=50
        )
        
        # Create a DataFrame for better display
        if jobs:
            df = pd.DataFrame(jobs)
            df['posted_date'] = pd.to_datetime(df['posted_date']).dt.strftime('%Y-%m-%d')
            
            # Save to CSV for reference
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'matching_jobs_{timestamp}.csv'
            df.to_csv(filename, index=False)
            
            # Create log file with the same timestamp
            log_filename = f'job_search_{timestamp}.log'
            
            # Prepare the output message
            output = []
            output.append(f"\nFound {len(jobs)} matching jobs. Details saved to {filename}")
            output.append("\nHere are the matching jobs:")
            output.append("=" * 80)
            
            for idx, job in enumerate(jobs, 1):
                output.append(f"\n{idx}. {job['title']} at {job['company']}")
                output.append(f"   Location: {job['location']}")
                output.append(f"   Posted: {job['posted_date']}")
                output.append(f"   Experience Level: {job['experience_level']}")
                output.append(f"   Apply here: {job['url']}")
                output.append("-" * 80)
            
            # Write to log file
            with open(log_filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output))
            
            # Print to terminal
            print('\n'.join(output))
            
            return jobs
        else:
            message = "No matching jobs found."
            print(message)
            
            # Write to log file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_filename = f'job_search_{timestamp}.log'
            with open(log_filename, 'w', encoding='utf-8') as f:
                f.write(message)
            
            return []
        
    except Exception as e:
        error_message = f"Error in job search: {str(e)}"
        print(error_message)
        
        # Write error to log file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f'job_search_{timestamp}.log'
        with open(log_filename, 'w', encoding='utf-8') as f:
            f.write(error_message)
        
        return []

def extract_keywords(profile):
    """
    Extract relevant keywords from profile for job search
    
    Args:
        profile (dict): User profile
        
    Returns:
        str: Space-separated keywords
    """
    keywords = []
    
    # Add skills
    if 'skills' in profile:
        keywords.extend(profile['skills'])
    
    # Add job titles
    if 'experience' in profile:
        for exp in profile['experience']:
            if 'title' in exp:
                keywords.append(exp['title'])
    
    # Add education
    if 'education' in profile:
        for edu in profile['education']:
            if 'degree' in edu:
                keywords.append(edu['degree'])
            if 'major' in edu:
                keywords.append(edu['major'])
    
    return ' '.join(keywords) 