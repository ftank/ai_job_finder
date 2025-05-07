import os
from resume_parser import extract_profile
from job_search import search_jobs
from ai_matcher import match_jobs
from apply import apply_to_job
import pandas as pd

RESUME_FILE = 'resume.pdf'  # Place your resume PDF in the project directory and rename if needed
LOG_FILE = 'log.csv'


def main():
    # Step 1: Extract profile from resume
    if not os.path.exists(RESUME_FILE):
        print(f"Please place your resume PDF as '{RESUME_FILE}' in the project directory.")
        return

    print("Extracting profile from resume...")
    profile = extract_profile(RESUME_FILE)
    print("Profile extracted:", profile)

    # Step 2: Search for jobs
    print("Searching for jobs...")
    jobs = search_jobs(profile)
    print(f"Found {len(jobs)} jobs.")

    # Step 3: Match jobs using AI
    print("Matching jobs to your profile...")
    matched_jobs = match_jobs(profile, jobs)
    print(f"{len(matched_jobs)} jobs matched above threshold.")

    # Step 4: Apply to matched jobs
    for job in matched_jobs:
        print(f"Applying to: {job['title']} at {job['company']}")
        apply_to_job(profile, job)
        # Log application
        log_application(job)


def log_application(job):
    log_entry = pd.DataFrame([job])
    if not os.path.exists(LOG_FILE):
        log_entry.to_csv(LOG_FILE, index=False)
    else:
        log_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)


if __name__ == "__main__":
    main() 