from flask import Flask, jsonify, request, session
from flask_cors import CORS
from job_search import search_jobs
from resume_parser import parse_resume
from linkedin_integration import LinkedInJobSearch
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://job-ai-applier-frontend.onrender.com",
            "https://*.onrender.com",
            "https://ai-job-finder.onrender.com"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 600
    }
})
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route('/api/jobs/search', methods=['GET'])
def search_jobs_endpoint():
    keywords = request.args.get('keywords', '')
    location = request.args.get('location', '')
    experience_level = request.args.get('experience_level', '')
    
    linkedin_search = LinkedInJobSearch()
    jobs = linkedin_search.search_jobs(keywords, location, experience_level)
    
    return jsonify(jobs)

@app.route('/api/job/<job_id>', methods=['GET'])
def get_job_details(job_id):
    linkedin_search = LinkedInJobSearch()
    job_details = linkedin_search.get_job_details(job_id)
    
    if job_details:
        return jsonify(job_details)
    return jsonify({'error': 'Job not found'}), 404

@app.route('/api/auth/linkedin/profile', methods=['GET'])
def get_profile():
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not access_token:
        return jsonify({'error': 'No access token provided'}), 401
    
    linkedin_search = LinkedInJobSearch()
    profile = linkedin_search.get_profile(access_token)
    
    if profile:
        return jsonify(profile)
    return jsonify({'error': 'Failed to get profile'}), 400

# Add error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(502)
def bad_gateway(error):
    return jsonify({'error': 'Bad gateway'}), 502

# Add health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False) 