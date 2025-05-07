import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const LinkedInCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        console.log('Callback component mounted');
        console.log('Current URL:', window.location.href);
        
        // Get the authorization code from the URL
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const error = urlParams.get('error');
        
        console.log('URL parameters:', { code, state, error });
        
        if (error) {
          throw new Error(`LinkedIn OAuth error: ${error}`);
        }
        
        // Verify state to prevent CSRF
        const storedState = sessionStorage.getItem('linkedin_oauth_state');
        console.log('Stored state:', storedState);
        console.log('Received state:', state);
        
        if (state !== storedState) {
          throw new Error('Invalid state parameter');
        }

        if (code) {
          console.log('Authorization code received, sending to opener window');
          // Send message to opener window
          if (window.opener) {
            window.opener.postMessage({
              type: 'linkedin-auth-success',
              code: code
            }, window.location.origin);
            console.log('Message sent to opener window');
            window.close();
          } else {
            console.log('No opener window found, redirecting to home');
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
      <p>If this window doesn't close automatically, you can close it manually.</p>
    </div>
  );
};

export default LinkedInCallback; 