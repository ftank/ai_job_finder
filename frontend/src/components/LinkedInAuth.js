import React, { useState } from 'react';
import './LinkedInAuth.css';

const LinkedInAuth = ({ onAuthSuccess }) => {
  const [error, setError] = useState('');

  const handleLinkedInLogin = async () => {
    try {
      // LinkedIn OAuth configuration
      const clientId = process.env.REACT_APP_LINKEDIN_CLIENT_ID || '77ouq1crxpcz32';
      const redirectUri = process.env.REACT_APP_LINKEDIN_REDIRECT_URI || 'https://ai-job-finder.onrender.com/callback';
      const scope = 'r_liteprofile r_emailaddress w_member_social';
      
      console.log('OAuth Configuration:', {
        clientId,
        redirectUri,
        scope
      });
      
      // Generate random state for security
      const state = Math.random().toString(36).substring(7);
      
      // Store state in session storage for verification
      sessionStorage.setItem('linkedin_oauth_state', state);
      
      // Construct the authorization URL
      const linkedInAuthUrl = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent(scope)}&state=${state}`;
      
      console.log('Full authorization URL:', linkedInAuthUrl);
      
      // Open LinkedIn auth in a new window
      const width = 600;
      const height = 600;
      const left = window.screenX + (window.outerWidth - width) / 2;
      const top = window.screenY + (window.outerHeight - height) / 2;
      
      const authWindow = window.open(
        linkedInAuthUrl,
        'LinkedIn Authentication',
        `width=${width},height=${height},left=${left},top=${top}`
      );

      if (!authWindow) {
        throw new Error('Popup window was blocked. Please allow popups for this site.');
      }

      // Listen for messages from the popup window
      const messageHandler = async (event) => {
        console.log('Received message:', event.data);
        
        if (event.data.type === 'linkedin-auth-success') {
          // Get the authorization code from the popup
          const code = event.data.code;
          console.log('Received authorization code');
          
          try {
            // Send the code to your backend for token exchange
            const response = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/linkedin/callback`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ code })
            });
            
            if (!response.ok) {
              const errorData = await response.json();
              console.error('Token exchange failed:', errorData);
              throw new Error('Failed to exchange code for token');
            }
            
            const data = await response.json();
            console.log('Authentication successful');
            
            if (data.access_token) {
              // Store the token in session storage
              sessionStorage.setItem('linkedin_access_token', data.access_token);
              console.log('Token stored in session storage');
              
              // Call the success callback
              if (onAuthSuccess) {
                onAuthSuccess(data);
              }
            } else {
              console.error('No access token in response:', data);
              setError('Failed to get access token');
            }
          } catch (error) {
            console.error('Error exchanging code for token:', error);
            setError('Error exchanging code for token. Please try again.');
          }
          
          // Clean up the event listener
          window.removeEventListener('message', messageHandler);
        }
      };

      window.addEventListener('message', messageHandler);
      
    } catch (error) {
      console.error('Error in LinkedIn login:', error);
      setError(error.message || 'Error starting LinkedIn authentication. Please try again.');
    }
  };

  return (
    <div className="linkedin-auth-container">
      <div className="linkedin-auth-box">
        <h2>Welcome to Job AI Applier</h2>
        <p className="auth-description">
          Connect your LinkedIn account to get started with automated job applications
        </p>
        
        {error && <div className="error-message">{error}</div>}
        
        <button 
          onClick={handleLinkedInLogin}
          className="linkedin-button"
        >
          <svg className="linkedin-icon" viewBox="0 0 24 24">
            <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
          </svg>
          Connect with LinkedIn
        </button>
        
        <div className="auth-info">
          <p>
            By connecting your LinkedIn account, you agree to our Terms of Service and Privacy Policy.
            We only request access to information necessary for job applications.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LinkedInAuth; 