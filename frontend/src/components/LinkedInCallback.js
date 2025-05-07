import React, { useEffect } from 'react';

const LinkedInCallback = () => {
  useEffect(() => {
    const handleCallback = () => {
      console.log('Callback component mounted');
      
      // Get the authorization code and state from URL
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      
      console.log('URL parameters:', { code, state });
      
      // Verify state matches what we stored
      const storedState = sessionStorage.getItem('linkedin_oauth_state');
      console.log('Stored state:', storedState);
      
      if (state === storedState && code) {
        console.log('State verified, sending code to opener');
        // Send the code back to the opener window
        if (window.opener) {
          window.opener.postMessage({ 
            type: 'linkedin-auth-success',
            code: code
          }, '*');
          console.log('Message sent to opener');
        } else {
          console.error('No opener window found');
        }
      } else {
        console.error('State verification failed or no code received');
      }
      
      // Close this window
      console.log('Closing popup window');
      window.close();
    };

    handleCallback();
  }, []);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      fontFamily: 'Arial, sans-serif'
    }}>
      <p>Completing authentication...</p>
    </div>
  );
};

export default LinkedInCallback; 