from flask import Flask, request, jsonify, session
from flask_cors import CORS
from linkedin_oauth import LinkedInOAuth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://job-ai-applier-frontend.onrender.com",
            "https://*.onrender.com"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')

oauth = LinkedInOAuth()

@app.route('/api/auth/linkedin/url', methods=['GET'])
def get_linkedin_url():
    """Get LinkedIn OAuth URL"""
    auth_url = oauth.get_auth_url()
    return jsonify({'url': auth_url})

@app.route('/api/auth/linkedin/callback', methods=['POST'])
def linkedin_callback():
    """Handle LinkedIn OAuth callback"""
    code = request.json.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    token_data = oauth.get_access_token(code)
    if not token_data:
        return jsonify({'error': 'Failed to get access token'}), 400

    access_token = token_data.get('access_token')
    profile = oauth.get_profile(access_token)
    email = oauth.get_email(access_token)

    if not profile or not email:
        return jsonify({'error': 'Failed to get profile information'}), 400

    return jsonify({
        'access_token': access_token,
        'profile': profile,
        'email': email
    })

if __name__ == '__main__':
    app.run(debug=True) 