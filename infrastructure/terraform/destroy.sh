#!/bin/bash
set -e

echo "Starting cleanup..."

BUCKET=$(terraform output -raw bucket_name)

echo "Emptying S3 bucket: $BUCKET"
aws s3 rm s3://$BUCKET --recursive

echo "Destroying Terraform resources..."
terraform destroy -auto-approve

echo "Cleanup complete."
