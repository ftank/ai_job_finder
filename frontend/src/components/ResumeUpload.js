import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper,
  CircularProgress
} from '@mui/material';
import { CloudUpload } from '@mui/icons-material';

const ResumeUpload = ({ onJobsReceived }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError('Please select a PDF file');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('resume', file);

    try {
      const response = await fetch('http://localhost:5000/api/upload-resume', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to upload resume');
      }

      onJobsReceived(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 4, 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center',
        maxWidth: 600,
        mx: 'auto',
        my: 4
      }}
    >
      <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
      
      <Typography variant="h5" component="h2" gutterBottom>
        Upload Your Resume
      </Typography>
      
      <Typography variant="body1" color="textSecondary" align="center" sx={{ mb: 3 }}>
        Upload your resume in PDF format to find matching jobs
      </Typography>

      <Box sx={{ width: '100%', mb: 2 }}>
        <input
          accept=".pdf"
          style={{ display: 'none' }}
          id="resume-file"
          type="file"
          onChange={handleFileChange}
        />
        <label htmlFor="resume-file">
          <Button
            variant="outlined"
            component="span"
            fullWidth
            disabled={uploading}
          >
            Select PDF File
          </Button>
        </label>
      </Box>

      {file && (
        <Typography variant="body2" sx={{ mb: 2 }}>
          Selected file: {file.name}
        </Typography>
      )}

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <Button
        variant="contained"
        color="primary"
        onClick={handleUpload}
        disabled={!file || uploading}
        fullWidth
      >
        {uploading ? (
          <>
            <CircularProgress size={24} sx={{ mr: 1 }} />
            Uploading...
          </>
        ) : (
          'Find Matching Jobs'
        )}
      </Button>
    </Paper>
  );
};

export default ResumeUpload; 