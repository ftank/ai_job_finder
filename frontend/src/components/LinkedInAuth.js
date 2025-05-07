import React, { useState } from 'react';
import './LinkedInAuth.css';

const LinkedInAuth = ({ onAuthSuccess }) => {
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLinkedInLogin = async () => {
    try {
      setIsLoading(true);
      setError('');

      // LinkedIn OAuth configuration
      const clientId = process.env.REACT_APP_LINKEDIN_CLIENT_ID || '77ouq1crxpcz32';
      const redirectUri = process.env.REACT_APP_LINKEDIN_REDIRECT_URI || 'https://ai-job-finder.onrender.com/callback';
      const scope = 'r_liteprofile r_emailaddress w_member_social';
      
      console.log('OAuth Configuration:', {
        clientId,
        redirectUri,
        scope,
        apiUrl: process.env.REACT_APP_API_URL
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
            const apiUrl = process.env.REACT_APP_API_URL;
            console.log('Sending code to backend:', apiUrl);
            
            const response = await fetch(`${apiUrl}/api/auth/linkedin/callback`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ code })
            });
            
            if (!response.ok) {
              const errorData = await response.json();
              console.error('Token exchange failed:', errorData);
              throw new Error(errorData.error || 'Failed to exchange code for token');
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
            setError(error.message || 'Error exchanging code for token. Please try again.');
          } finally {
            setIsLoading(false);
          }
          
          // Clean up the event listener
          window.removeEventListener('message', messageHandler);
        } else if (event.data.type === 'linkedin-auth-error') {
          console.error('LinkedIn auth error:', event.data.error);
          setError(event.data.error);
          setIsLoading(false);
          window.removeEventListener('message', messageHandler);
        }
      };

      window.addEventListener('message', messageHandler);
      
    } catch (error) {
      console.error('Error in LinkedIn login:', error);
      setError(error.message || 'Error starting LinkedIn authentication. Please try again.');
      setIsLoading(false);
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
          disabled={isLoading}
        >
          {isLoading ? 'Connecting...' : 'Connect with LinkedIn'}
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