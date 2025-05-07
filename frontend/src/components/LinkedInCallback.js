import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const LinkedInCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get the authorization code from the URL
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        
        // Verify state to prevent CSRF
        const storedState = sessionStorage.getItem('linkedin_oauth_state');
        if (state !== storedState) {
          throw new Error('Invalid state parameter');
        }

        if (code) {
          // Send message to opener window
          if (window.opener) {
            window.opener.postMessage({
              type: 'linkedin-auth-success',
              code: code
            }, window.location.origin);
            window.close();
          } else {
            // If no opener, redirect to home
            navigate('/');
          }
        } else {
          throw new Error('No authorization code received');
        }
      } catch (error) {
        console.error('Error in callback:', error);
        // Send error to opener window
        if (window.opener) {
          window.opener.postMessage({
            type: 'linkedin-auth-error',
            error: error.message
          }, window.location.origin);
          window.close();
        } else {
          navigate('/');
        }
      }
    };

    handleCallback();
  }, [navigate]);

  return (
    <div className="callback-container">
      <h2>Processing LinkedIn Authentication...</h2>
      <p>Please wait while we complete the authentication process.</p>
    </div>
  );
};

export default LinkedInCallback; 