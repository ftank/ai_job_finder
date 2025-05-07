#!/bin/bash

# Create a deployment package
echo "Creating deployment package..."
cd backend
zip -r ../deployment.zip . -x "*.git*" "*.pyc" "__pycache__/*" "*.DS_Store"

# Initialize EB CLI (if not already done)
echo "Initializing Elastic Beanstalk application..."
eb init -p python-3.9 job-ai-applier --region us-east-1

# Create environment (if not already done)
echo "Creating Elastic Beanstalk environment..."
eb create job-ai-applier-env --instance-type t2.micro --single

# Deploy the application
echo "Deploying application..."
eb deploy

echo "Deployment complete! Your application should be available at:"
eb status | grep CNAME 