#!/bin/bash

# Create IAM role for Elastic Beanstalk
echo "Creating IAM role for Elastic Beanstalk..."
aws iam create-role \
    --role-name job-ai-applier-eb-role \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "elasticbeanstalk.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }'

# Attach policy to the role
echo "Attaching policy to the role..."
aws iam put-role-policy \
    --role-name job-ai-applier-eb-role \
    --policy-name job-ai-applier-eb-policy \
    --policy-document file://aws/elastic-beanstalk-policy.json

# Create security group
echo "Creating security group..."
aws ec2 create-security-group \
    --group-name job-ai-applier-sg \
    --description "Security group for Job AI Applier application" \
    --vpc-id vpc-xxxxxxxx  # Replace with your VPC ID

# Add inbound rules
echo "Adding inbound rules..."
aws ec2 authorize-security-group-ingress \
    --group-name job-ai-applier-sg \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-name job-ai-applier-sg \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-name job-ai-applier-sg \
    --protocol tcp \
    --port 22 \
    --cidr YOUR_IP/32  # Replace with your IP

# Create S3 bucket for application artifacts
echo "Creating S3 bucket for application artifacts..."
aws s3 mb s3://job-ai-applier-artifacts

# Create bucket policy
echo "Creating bucket policy..."
aws s3api put-bucket-policy \
    --bucket job-ai-applier-artifacts \
    --policy '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowElasticBeanstalkAccess",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:role/job-ai-applier-eb-role"
                },
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::job-ai-applier-artifacts",
                    "arn:aws:s3:::job-ai-applier-artifacts/*"
                ]
            }
        ]
    }'

echo "Security setup complete!" 