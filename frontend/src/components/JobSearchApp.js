import React, { useState, useEffect } from 'react';
import LinkedInAuth from './LinkedInAuth';
import './JobSearchApp.css';

const JobSearchApp = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = sessionStorage.getItem('linkedin_access_token');
      if (!token) {
        setIsAuthenticated(false);
        return;
      }

      const response = await fetch('http://localhost:5000/api/auth/linkedin/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
        // Clear invalid token
        sessionStorage.removeItem('linkedin_access_token');
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      setIsAuthenticated(false);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setError('');
    } else {
      setError('Please select a valid PDF file');
      setSelectedFile(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('resume', selectedFile);

    try {
      const response = await fetch('http://localhost:5000/api/upload-resume', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        // Handle successful job search results
        console.log('Job search results:', data);
      } else {
        const error = await response.json();
        setError(error.message || 'Error uploading resume');
      }
    } catch (error) {
      setError('Error uploading resume. Please try again.');
    }
  };

  if (!isAuthenticated) {
    return <LinkedInAuth onAuthSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="job-search-container">
      <div className="job-search-box">
        <h2>Job Search</h2>
        <p className="search-description">
          Upload your resume to find matching job opportunities
        </p>

        <div className="upload-section">
          <div className="file-input-container">
            <input
              type="file"
              id="resume"
              accept=".pdf"
              onChange={handleFileChange}
              className="file-input"
            />
            <label htmlFor="resume" className="file-input-label">
              {selectedFile ? selectedFile.name : 'Choose PDF Resume'}
            </label>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            onClick={handleUpload}
            disabled={!selectedFile}
            className="search-button"
          >
            Search Jobs
          </button>
        </div>
      </div>
    </div>
  );
};

export default JobSearchApp; 