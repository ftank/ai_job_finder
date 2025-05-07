import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Box,
  CircularProgress,
  Collapse,
  IconButton,
  Chip,
  Link,
  Divider
} from '@mui/material';
import { 
  WorkOutline, 
  LocationOn, 
  AccessTime,
  ExpandMore,
  ExpandLess,
  Business,
  People,
  AttachMoney,
  School,
  Schedule,
  Event
} from '@mui/icons-material';

const JobCard = ({ job }) => {
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [details, setDetails] = useState(null);

  const fetchJobDetails = async () => {
    if (!job.job_id || details) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:5000/api/job/${job.job_id}`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch job details');
      }
      
      setDetails(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (expanded) {
      fetchJobDetails();
    }
  }, [expanded]);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  // Helper function to safely extract text from nested objects
  const getText = (obj) => {
    if (!obj) return '';
    if (typeof obj === 'string') return obj;
    if (obj.text) return obj.text;
    if (obj.attributes && obj.attributes.text) return obj.attributes.text;
    return '';
  };

  // Helper function to format description text with line breaks
  const formatDescription = (text) => {
    if (!text) return '';
    return text.split('\\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        {index < text.split('\\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  // Helper function to extract skills from job details
  const getSkills = (details) => {
    if (!details) return [];
    if (Array.isArray(details.skills)) return details.skills;
    if (details.skills && Array.isArray(details.skills.text)) return details.skills.text;
    return [];
  };

  // Helper function to extract company details
  const getCompanyDetails = (details) => {
    if (!details) return null;
    
    return {
      name: details.company || '',
      website: details.company_details?.website || '',
      description: details.company_details?.description || ''
    };
  };

  // Helper function to extract job metadata
  const getJobMetadata = (details) => {
    if (!details) return null;

    return {
      employmentType: details.employment_type || '',
      seniorityLevel: details.seniority_level || '',
      industry: details.industry || '',
      jobType: details.job_type || '',
      applicantsCount: details.applicants_count || 0,
      salary: details.salary || '',
      benefits: details.benefits || [],
      applicationDeadline: details.application_deadline || '',
      jobStatus: details.job_status || ''
    };
  };

  const companyInfo = details ? getCompanyDetails(details) : null;
  const jobMetadata = details ? getJobMetadata(details) : null;

  return (
    <Card sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      transition: 'transform 0.2s',
      '&:hover': {
        transform: 'translateY(-4px)',
        boxShadow: 3
      }
    }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography variant="h6" component="h2" gutterBottom>
          {details?.title || getText(job.title)}
        </Typography>
        
        <Typography color="textSecondary" gutterBottom>
          {companyInfo?.name || getText(job.company)}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <LocationOn sx={{ mr: 1, fontSize: 20 }} />
          <Typography variant="body2">
            {details?.location || getText(job.location)}
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <AccessTime sx={{ mr: 1, fontSize: 20 }} />
          <Typography variant="body2">
            Posted: {details?.posted_date || getText(job.posted_date)}
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <WorkOutline sx={{ mr: 1, fontSize: 20 }} />
          <Typography variant="body2">
            {details?.experience_level || getText(job.experience_level)}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button 
            variant="contained" 
            color="primary" 
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
          >
            Apply Now
          </Button>
          
          <IconButton onClick={handleExpandClick}>
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>

        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Box sx={{ mt: 2 }}>
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                <CircularProgress size={24} />
              </Box>
            )}

            {error && (
              <Typography color="error" sx={{ my: 2 }}>
                {error}
              </Typography>
            )}

            {details && (
              <>
                {jobMetadata && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Job Details:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {jobMetadata.employmentType && (
                        <Chip 
                          icon={<Schedule />}
                          label={jobMetadata.employmentType}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      )}
                      {jobMetadata.seniorityLevel && (
                        <Chip 
                          icon={<School />}
                          label={jobMetadata.seniorityLevel}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      )}
                      {jobMetadata.industry && (
                        <Chip 
                          icon={<Business />}
                          label={jobMetadata.industry}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      )}
                      {jobMetadata.applicantsCount > 0 && (
                        <Chip 
                          icon={<People />}
                          label={`${jobMetadata.applicantsCount} applicants`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      )}
                      {jobMetadata.salary && (
                        <Chip 
                          icon={<AttachMoney />}
                          label={jobMetadata.salary}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </Box>
                )}

                {details.skills?.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Required Skills:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {details.skills.map((skill, index) => (
                        <Chip 
                          key={index} 
                          label={getText(skill)} 
                          size="small" 
                          color="primary" 
                          variant="outlined" 
                        />
                      ))}
                    </Box>
                  </Box>
                )}

                {details.description && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Description:
                    </Typography>
                    <Typography 
                      variant="body2" 
                      color="textSecondary"
                      sx={{ 
                        whiteSpace: 'pre-line',
                        '& br': {
                          display: 'block',
                          content: '""',
                          marginTop: '0.5em'
                        }
                      }}
                    >
                      {formatDescription(details.description)}
                    </Typography>
                  </Box>
                )}

                {companyInfo && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Company Details:
                    </Typography>
                    {companyInfo.name && (
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Business sx={{ mr: 1, fontSize: 20 }} />
                        <Typography variant="body2" color="textSecondary">
                          {companyInfo.name}
                        </Typography>
                      </Box>
                    )}
                    {companyInfo.website && (
                      <Box sx={{ mb: 1 }}>
                        <Link 
                          href={companyInfo.website} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          color="primary"
                        >
                          Visit Company Website
                        </Link>
                      </Box>
                    )}
                    {companyInfo.description && (
                      <Typography 
                        variant="body2" 
                        color="textSecondary"
                        sx={{ 
                          whiteSpace: 'pre-line',
                          '& br': {
                            display: 'block',
                            content: '""',
                            marginTop: '0.5em'
                          }
                        }}
                      >
                        {formatDescription(companyInfo.description)}
                      </Typography>
                    )}
                  </Box>
                )}

                {jobMetadata?.benefits?.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Benefits:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {jobMetadata.benefits.map((benefit, index) => (
                        <Chip 
                          key={index}
                          label={benefit}
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                )}

                {jobMetadata?.applicationDeadline && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Application Deadline:
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Event sx={{ mr: 1, fontSize: 20 }} />
                      <Typography variant="body2" color="textSecondary">
                        {jobMetadata.applicationDeadline}
                      </Typography>
                    </Box>
                  </Box>
                )}
              </>
            )}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default JobCard; 