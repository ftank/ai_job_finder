from flask import Flask, jsonify, request, session
from flask_cors import CORS
from job_search import search_jobs
from resume_parser import parse_resume
from linkedin_integration import LinkedInJobSearch
from linkedin_oauth import LinkedInOAuth
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize LinkedIn OAuth for API calls only
linkedin_oauth = LinkedInOAuth()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_job_details(job_details):
    """Format job details into a consistent structure"""
    if not job_details:
        return None

    # Helper function to safely extract text
    def get_text(obj):
        if not obj:
            return ''
        if isinstance(obj, str):
            return obj
        if isinstance(obj, dict):
            if 'text' in obj:
                return obj['text']
            if 'attributes' in obj and 'text' in obj['attributes']:
                return obj['attributes']['text']
            if 'name' in obj:
                return obj['name']
        return ''

    # Extract company details
    company_details = job_details.get('companyDetails', {})
    
    # Extract company name from the correct path
    company_name = ''
    if 'com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany' in company_details:
        company_data = company_details['com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany']
        if 'companyResolutionResult' in company_data:
            company_name = get_text(company_data['companyResolutionResult'].get('name', ''))
    
    # Fallback to other company name fields if not found
    if not company_name:
        company_name = get_text(company_details.get('name', ''))
    if not company_name:
        company_name = get_text(job_details.get('companyName', ''))
    if not company_name:
        company_name = get_text(job_details.get('company', ''))
    if not company_name:
        company_name = get_text(job_details.get('formattedCompanyName', ''))
    
    company_website = company_details.get('website', '')
    company_description = get_text(company_details.get('description', ''))

    # Extract location
    location = get_text(job_details.get('location', ''))
    if not location:
        location = get_text(job_details.get('formattedLocation', ''))

    # Extract job metadata
    employment_type = get_text(job_details.get('employmentType', ''))
    if not employment_type:
        employment_type = get_text(job_details.get('formattedEmploymentType', ''))

    seniority_level = get_text(job_details.get('seniorityLevel', ''))
    if not seniority_level:
        seniority_level = get_text(job_details.get('formattedSeniorityLevel', ''))

    industry = get_text(job_details.get('industry', ''))
    if not industry:
        industry = get_text(job_details.get('formattedIndustry', ''))

    job_type = get_text(job_details.get('jobType', ''))
    if not job_type:
        job_type = get_text(job_details.get('formattedJobType', ''))

    applicants_count = job_details.get('applicantsCount', 0)
    salary = get_text(job_details.get('salary', ''))
    if not salary:
        salary = get_text(job_details.get('formattedSalary', ''))

    benefits = []
    if 'benefits' in job_details:
        if isinstance(job_details['benefits'], list):
            benefits = [get_text(benefit) for benefit in job_details['benefits']]
        elif isinstance(job_details['benefits'], dict):
            benefits = [get_text(benefit) for benefit in job_details['benefits'].get('text', [])]

    application_deadline = job_details.get('applicationDeadline', '')
    job_status = get_text(job_details.get('status', ''))

    # Extract skills
    skills = []
    if 'skills' in job_details:
        if isinstance(job_details['skills'], list):
            skills = [get_text(skill) for skill in job_details['skills']]
        elif isinstance(job_details['skills'], dict):
            if 'text' in job_details['skills']:
                skills = [get_text(skill) for skill in job_details['skills']['text']]
            elif 'values' in job_details['skills']:
                skills = [get_text(skill) for skill in job_details['skills']['values']]

    # Extract posted date
    posted_date = job_details.get('listedAt', '')
    if posted_date:
        try:
            from datetime import datetime
            posted_date = datetime.fromtimestamp(posted_date/1000).strftime('%Y-%m-%d')
        except:
            posted_date = ''

    # Extract experience level from workplaceTypesResolutionResults
    experience_level = ''
    if 'workplaceTypesResolutionResults' in job_details:
        workplace_types = job_details['workplaceTypesResolutionResults']
        if isinstance(workplace_types, dict):
            for key, value in workplace_types.items():
                if key.startswith('urn:li:fs_workplaceType:'):
                    if isinstance(value, dict) and 'localizedName' in value:
                        experience_level = value['localizedName']
                        break

    # Fallback to other experience level fields if not found
    if not experience_level:
        experience_level = get_text(job_details.get('experienceLevel', ''))
    if not experience_level:
        experience_level = get_text(job_details.get('formattedExperienceLevel', ''))

    return {
        'title': get_text(job_details.get('title', '')),
        'company': company_name,
        'location': location,
        'description': get_text(job_details.get('description', '')),
        'posted_date': posted_date,
        'experience_level': experience_level,
        'employment_type': employment_type,
        'seniority_level': seniority_level,
        'industry': industry,
        'job_type': job_type,
        'applicants_count': applicants_count,
        'salary': salary,
        'benefits': benefits,
        'application_deadline': application_deadline,
        'job_status': job_status,
        'skills': skills,
        'company_details': {
            'name': company_name,
            'website': company_website,
            'description': company_description
        }
    }

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse resume and get profile
        profile = parse_resume(filepath)
        
        # Search for jobs
        jobs = search_jobs(profile)
        
        # Clean up the uploaded file
        os.remove(filepath)
        
        return jsonify(jobs)
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/job/<job_id>', methods=['GET'])
def get_job_details(job_id):
    try:
        linkedin = LinkedInJobSearch()
        raw_job_details = linkedin.get_job_details(job_id)
        formatted_details = format_job_details(raw_job_details)
        
        if not formatted_details:
            return jsonify({'error': 'Job details not found'}), 404
            
        return jsonify(formatted_details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/linkedin/profile', methods=['GET'])
def get_profile():
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No valid authorization token provided'}), 401
            
        token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Invalid authorization token'}), 401
            
        # Get profile using the token
        profile = linkedin_oauth.get_profile(token)
        if not profile:
            return jsonify({'error': 'Failed to get profile'}), 400
            
        return jsonify({'profile': profile})
        
    except Exception as e:
        print(f"Error getting profile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/linkedin/logout', methods=['POST'])
def logout():
    try:
        # Clear session
        session.clear()
        return jsonify({'message': 'Logged out successfully'})
    except Exception as e:
        print(f"Error during logout: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/linkedin/callback')
def linkedin_callback():
    try:
        # Get the authorization code and state from URL
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code:
            return jsonify({'error': 'No authorization code received'}), 400
            
        # Return an HTML page that sends the code back to the opener window
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>LinkedIn Authentication</title>
        </head>
        <body>
            <script>
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'linkedin-auth-success',
                        code: '{code}'
                    }}, '*');
                }}
            </script>
        </body>
        </html>
        '''
        
    except Exception as e:
        print(f"Error in LinkedIn callback: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 