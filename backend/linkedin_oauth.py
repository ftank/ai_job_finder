import os
import requests
from dotenv import load_dotenv

load_dotenv()

class LinkedInOAuth:
    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:3000/callback')
        self.scope = 'r_liteprofile r_emailaddress w_member_social'

    def get_auth_url(self):
        """Generate LinkedIn OAuth URL"""
        return f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope={self.scope}"

    def get_access_token(self, code):
        """Exchange authorization code for access token"""
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            return response.json()
        return None

    def get_profile(self, access_token):
        """Get user profile information"""
        profile_url = "https://api.linkedin.com/v2/me"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'cache-control': 'no-cache',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        response = requests.get(profile_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_email(self, access_token):
        """Get user email address"""
        email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'cache-control': 'no-cache',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        response = requests.get(email_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'elements' in data and len(data['elements']) > 0:
                return data['elements'][0]['handle~']['emailAddress']
        return None 