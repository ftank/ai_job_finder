from flask import Flask, request, redirect, session
from linkedin_oauth import LinkedInOAuth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')

oauth = LinkedInOAuth()

@app.route('/')
def index():
    """Redirect to LinkedIn authorization"""
    auth_url = oauth.get_authorization_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle OAuth callback"""
    try:
        # Get the authorization response
        auth_response = request.url
        
        # Fetch token using the authorization response
        token = oauth.fetch_token(auth_response)
        
        # Get user profile to verify authentication
        profile = oauth.get_profile()
        if profile:
            return "Successfully authenticated with LinkedIn! You can close this window."
        else:
            return "Authentication failed. Please try again."
            
    except Exception as e:
        return f"Error during authentication: {str(e)}"

if __name__ == '__main__':
    app.run(port=5000) 