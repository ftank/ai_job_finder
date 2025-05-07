import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LinkedInCallback.css';

const LinkedInCallback = () => {
  const navigate = useNavigate();
  const [status, setStatus] = useState('Processing...');
  const [error, setError] = useState(null);

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
        const errorDescription = urlParams.get('error_description');
        
        console.log('URL parameters:', { code, state, error, errorDescription });
        
        if (error) {
          throw new Error(errorDescription || `LinkedIn OAuth error: ${error}`);
        }
        
        // Verify state to prevent CSRF
        const storedState = sessionStorage.getItem('linkedin_oauth_state');
        console.log('Stored state:', storedState);
        console.log('Received state:', state);
        
        if (!storedState) {
          throw new Error('No state found in session storage');
        }
        
        if (state !== storedState) {
          throw new Error('Invalid state parameter - possible CSRF attack');
        }

        if (code) {
          setStatus('Authorization successful, sending to main window...');
          console.log('Authorization code received, sending to opener window');
          
          // Send message to opener window
          if (window.opener) {
            window.opener.postMessage({
              type: 'linkedin-auth-success',
              code: code
            }, window.location.origin);
            console.log('Message sent to opener window');
            
            // Wait a moment before closing to ensure message is received
            setTimeout(() => {
              window.close();
            }, 1000);
          } else {
            console.log('No opener window found, redirecting to home');
            navigate('/');
          }
        } else {
          throw new Error('No authorization code received');
        }
      } catch (error) {
        console.error('Error in callback:', error);
        setError(error.message);
        setStatus('Authentication failed');
        
        // Send error to opener window
        if (window.opener) {
          window.opener.postMessage({
            type: 'linkedin-auth-error',
            error: error.message
          }, window.location.origin);
          
          // Wait a moment before closing to ensure message is received
          setTimeout(() => {
            window.close();
          }, 2000);
        } else {
          // If no opener, redirect to home after a delay
          setTimeout(() => {
            navigate('/');
          }, 3000);
        }
      }
    };

    handleCallback();
  }, [navigate]);

  return (
    <div className="callback-container">
      <div className="callback-box">
        <h2>LinkedIn Authentication</h2>
        {error ? (
          <>
            <div className="error-message">
              <p>{error}</p>
            </div>
            <p>You will be redirected to the home page...</p>
          </>
        ) : (
          <>
            <div className="status-message">
              <p>{status}</p>
            </div>
            <p>This window will close automatically.</p>
          </>
        )}
      </div>
    </div>
  );
};

export default LinkedInCallback; 