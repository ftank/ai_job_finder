import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

class LinkedInOAuth:
    def __init__(self):
        self.profile_url = 'https://api.linkedin.com/v2/me'
        self.email_url = 'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))'
        
    def get_profile(self, token):
        """Get user profile using access token"""
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'cache-control': 'no-cache',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            # Get basic profile
            profile_response = requests.get(self.profile_url, headers=headers)
            profile_response.raise_for_status()
            profile = profile_response.json()
            
            # Get email address
            email_response = requests.get(self.email_url, headers=headers)
            email_response.raise_for_status()
            email_data = email_response.json()
            
            # Add email to profile
            if 'elements' in email_data and email_data['elements']:
                profile['email'] = email_data['elements'][0]['handle~']['emailAddress']
                
            return profile
            
        except Exception as e:
            print(f"Error getting profile: {str(e)}")
            return None 