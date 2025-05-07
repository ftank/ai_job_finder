# Job AI Applier

This project automates the process of finding jobs that match your resume and applying to them using AI.

## Features
- Extracts your profile from a PDF resume
- Searches for jobs on job boards
- Uses AI to match jobs to your profile
- Automatically applies to jobs that are a good fit
- Logs all applications

## Usage
1. Place your resume PDF in the project directory.
2. Run `main.py` to extract your profile and start the job search and application process.

## Requirements
- Python 3.8+
- See `requirements.txt` for dependencies

## Project Structure
- `main.py`: Entry point
- `resume_parser.py`: Extracts and parses your resume
- `job_search.py`: Finds jobs
- `ai_matcher.py`: Matches jobs to your profile
- `apply.py`: Handles applications
- `log.csv`: Application log 