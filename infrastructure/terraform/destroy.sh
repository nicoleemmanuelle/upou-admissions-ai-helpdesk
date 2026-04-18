#!/bin/bash

echo "Starting cleanup..."

# Get bucket name from Terraform output
BUCKET=$(terraform output -raw bucket_name)

echo "Emptying S3 bucket: $BUCKET"
aws s3 rm s3://$BUCKET --recursive

echo "Destroying Terraform resources..."
terraform destroy -auto-approve

echo "Cleanup complete."
