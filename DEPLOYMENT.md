# Deployment Guide – UPOU Admissions AI Helpdesk

This guide covers how to deploy, update, and tear down the UPOU Admissions AI Helpdesk on AWS.

---

## Table of Contents

- [Quick Deploy (Concise)](#quick-deploy-concise)
- [Manual Deployment (Detailed)](#manual-deployment-detailed)
  - [Prerequisites](#prerequisites)
  - [Step 1 – Configure AWS Credentials](#step-1--configure-aws-credentials)
  - [Step 2 – Set Terraform Variables](#step-2--set-terraform-variables)
  - [Step 3 – Package the Lambda Functions](#step-3--package-the-lambda-functions)
  - [Step 4 – Provision Backend Infrastructure (Phase 1)](#step-4--provision-backend-infrastructure-phase-1)
  - [Step 5 – Build the Frontend](#step-5--build-the-frontend)
  - [Step 6 – Deploy Frontend to EC2 (Phase 2)](#step-6--deploy-frontend-to-ec2-phase-2)
  - [Step 7 – Assign an Elastic IP to the EC2 Instance](#step-7--assign-an-elastic-ip-to-the-ec2-instance)
  - [Step 8 – Confirm SNS Email Subscription](#step-8--confirm-sns-email-subscription)
  - [Step 9 – Access the Application](#step-9--access-the-application)
  - [Step 10 – Enable HTTPS with Let's Encrypt](#step-10--enable-https-with-lets-encrypt)
- [Updating the Application](#updating-the-application)
- [Manual Teardown (Without destroy.sh)](#manual-teardown-without-destroysh)

---

## Quick Deploy (Concise)

> Assumes prerequisites are installed, AWS credentials are exported, and `terraform.tfvars` is already configured.

### Step 1 – Run the deploy script

```bash
chmod +x deploy.sh
bash deploy.sh
```

The script automatically:
- Packages Lambda into `backend/lambda/lambda.zip`
- Runs `terraform init` + `terraform apply` (Phase 1) to provision all backend AWS services
- Writes `frontend/.env` with the API Gateway URL from Terraform output
- Builds the React frontend (`npm install && npm run build`)
- Taints and re-deploys the EC2 instance with the new frontend build (Phase 2)

### Step 2 – Assign an Elastic IP

1. In the AWS Console, go to **EC2 > Elastic IPs**
2. Allocate a new Elastic IP (or use an existing one)
3. Associate it with the **IS215-Project** EC2 instance

This gives the instance a stable, persistent IP address that survives reboots.

### Step 3 – Enable HTTPS

Copy the SSL setup script to the EC2 instance and run it:

```bash
# Run this first if you get a host key conflict
ssh-keygen -R <ip_address>

# Copy the script from your local machine to EC2
scp -i vockey.pem setup_ssl.sh ec2-user@<ip_address>:~

# SSH in and run the script
ssh -i vockey.pem ec2-user@<ip_address>
bash setup_ssl.sh <domain> <email>
```

The script installs Certbot, provisions a Let's Encrypt TLS certificate, and configures Nginx for HTTPS with automatic HTTP → HTTPS redirection.

### Teardown

To destroy all AWS resources:

```bash
cd infrastructure/terraform/
bash destroy.sh
```

The destroy script empties the S3 knowledge base bucket before running `terraform destroy` to avoid the "bucket not empty" error.

---

## Manual Deployment (Detailed)

Use this approach when you need full control over each step, are troubleshooting a failed deploy, or are running in an environment where `deploy.sh` is not available.

### Prerequisites

Install the following tools before proceeding:

| Tool | Minimum Version | Installation |
|---|---|---|
| Terraform | ≥ 1.0 | `brew install terraform` (macOS) / `sudo apt install terraform` (WSL) |
| AWS CLI | any | `brew install awscli` / `sudo apt install awscli` |
| Node.js + npm | Node ≥ 18 | [nodejs.org](https://nodejs.org/) |
| Python | 3.11+ | `brew install python` / `sudo apt install python3` |
| zip | any | pre-installed on macOS / `sudo apt install zip` (WSL) |

---

### Step 1 – Configure AWS Credentials

Export your credentials as environment variables. These are required for both the AWS CLI and Terraform.

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY"
export AWS_SESSION_TOKEN="YOUR_SESSION_TOKEN"   # required for AWS Academy / Learner Lab
```

Verify the credentials are working:

```bash
aws sts get-caller-identity
```

You should see your account ID, user ID, and ARN in the response. If this command fails, double-check your credentials before continuing.

---

### Step 2 – Set Terraform Variables

Copy the example variables file and fill in the required values:

```bash
cp infrastructure/terraform/terraform.tfvars.example infrastructure/terraform/terraform.tfvars
```

Open `infrastructure/terraform/terraform.tfvars` and set the following:

```hcl
aws_region         = "us-east-1"
openai_api_key     = "sk-..."                      # Your OpenAI API key
notification_email = "admissions@upou.edu.ph"      # Receives SNS ticket alerts

# Option A — let Terraform create a new IAM role (default)
create_role = true
lambda_role = ""

# Option B — reuse an existing IAM role (e.g. AWS Learner Lab LabRole)
# create_role = false
# lambda_role = "arn:aws:iam::123456789012:role/LabRole"
```

> Do NOT commit `terraform.tfvars` to Git — it contains secrets. It is already listed in `.gitignore`.

---

### Step 3 – Package the Lambda Functions

Navigate to the Lambda source directory and run the packaging script:

```bash
cd backend/lambda
bash package_clean.sh
```

This produces `backend/lambda/lambda.zip`, which Terraform uploads to AWS. Re-run this step any time you modify Lambda source files.

---

### Step 4 – Provision Backend Infrastructure (Phase 1)

Navigate to the Terraform directory, initialize the working directory, then apply:

```bash
cd ../../infrastructure/terraform
terraform init
terraform apply
```

Terraform will display a plan of all resources it will create. Type `yes` when prompted to confirm.

Resources provisioned in this phase:

| Resource | Purpose |
|---|---|
| S3 bucket | Stores knowledge base files and the Lambda package |
| Lambda functions | RAG pipeline (`handler.py`) and ticket lookup (`ticket_lookup.py`) |
| API Gateway | Exposes `/ask` and `/id/{ticket_id}` REST endpoints |
| DynamoDB table | Stores support tickets |
| SNS topic | Sends email notifications to the admissions team |
| IAM role + policies | Grants Lambda access to S3, DynamoDB, SNS, and CloudWatch |
| EC2 instance | Hosts Nginx serving the React frontend |
| Security group | Controls inbound/outbound traffic for the EC2 instance |

After `terraform apply` completes, note the outputs:

```
api_url              = "https://<api_id>.execute-api.us-east-1.amazonaws.com/dev/ask"
ec2_public_ip        = "<ip>"
bucket_name          = "<bucket>"
lambda_name          = "<function_name>"
dynamodb_table_name  = "tickets"
```

Copy the `api_url` — you will need it in the next step.

---

### Step 5 – Build the Frontend

Navigate to the frontend directory, create the environment file, install dependencies, and build:

```bash
cd ../../frontend

# Create the environment file with your API URL
echo "VITE_API_URL=https://<api_id>.execute-api.us-east-1.amazonaws.com/dev/ask" > .env

# Install dependencies
npm install

# Build static files into frontend/dist/
npm run build
```

Replace the URL above with the actual `api_url` from Step 4.

The build output is written to `frontend/dist/`. This directory is not committed to Git and must be regenerated before each deployment.

---

### Step 6 – Deploy Frontend to EC2 (Phase 2)

Taint the EC2 instance so Terraform replaces it, picking up the new `frontend/dist/` build:

```bash
cd ../infrastructure/terraform

# Mark the EC2 instance for replacement
terraform taint aws_instance.frontend

# Apply — Terraform will destroy and recreate the EC2 instance
terraform apply
```

Type `yes` when prompted. Terraform will:

1. Create a new EC2 instance
2. Run a `user_data` bootstrap script that installs Nginx
3. Upload the built frontend files from S3 to the instance
4. Configure Nginx to serve the React SPA on port 80
5. Dynamically detect and download all hashed JS/CSS asset filenames — no hardcoded filenames required

The new `ec2_public_ip` will appear in the Terraform output once the apply completes.

---

### Step 7 – Assign an Elastic IP to the EC2 Instance

A standard EC2 public IP changes every time the instance is stopped and started. Associating an Elastic IP gives the instance a stable, persistent address.

1. In the AWS Console, go to **EC2 > Network & Security > Elastic IPs**
2. Click **Allocate Elastic IP address**, then **Allocate**
3. Select the newly allocated IP, click **Actions > Associate Elastic IP address**
4. Set **Resource type** to `Instance`, then select the **IS215-Project** EC2 instance
5. Click **Associate**

The Elastic IP is now the fixed public address for the instance. Use this IP (or a domain name pointing to it) for all subsequent steps.

---

### Step 8 – Confirm SNS Email Subscription

AWS SNS requires you to confirm the email subscription before it will deliver ticket notifications.

1. Check the inbox of the `notification_email` you set in `terraform.tfvars`
2. Open the email from `AWS Notifications` with subject **AWS Notification - Subscription Confirmation**
3. Click the **Confirm subscription** link

If the email does not arrive within a few minutes, check your spam folder.

---

### Step 9 – Access the Application

Open a browser and navigate to:

```
http://<ec2_public_ip>
```

To verify the deployment is working:

- The UPOU-branded chat interface loads
- The UP seal logo is visible
- Sending a query returns an AI-generated response or a support ticket link

To test the API directly:

```bash
curl -X POST https://<api_id>.execute-api.us-east-1.amazonaws.com/dev/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What programs does UPOU offer?"}'
```

---

### Step 10 – Enable HTTPS with Let's Encrypt

This step requires a domain name with a DNS A record pointing to the EC2 Elastic IP assigned in Step 7.

From your local machine, copy the SSL setup script to the EC2 instance:

```bash
# Clear the old host key if you get a conflict (e.g. after instance replacement)
ssh-keygen -R <ip_address>

# Copy the setup script to the EC2 instance
scp -i vockey.pem setup_ssl.sh ec2-user@<ip_address>:~

# SSH in and run it
ssh -i vockey.pem ec2-user@<ip_address>
bash setup_ssl.sh <domain> <email>
```

The script installs Certbot, provisions a Let's Encrypt TLS certificate for your domain, and reconfigures Nginx to serve HTTPS with automatic HTTP → HTTPS redirection.

---

## Updating the Application

### After modifying Lambda source code

```bash
cd backend/lambda
bash package_clean.sh

cd ../../infrastructure/terraform
terraform apply
```

### After modifying the frontend

```bash
cd frontend
npm run build

cd ../infrastructure/terraform
terraform taint aws_instance.frontend
terraform apply
```

### After modifying the knowledge base

Add or update files in `knowledge-base/output_for_s3/`, then re-apply Terraform to sync the changes to S3:

```bash
cd infrastructure/terraform
terraform apply
```

---

## Manual Teardown (Without destroy.sh)

`terraform destroy` will fail if the S3 bucket still contains objects, because Terraform cannot delete a non-empty bucket by default. Follow these steps to tear down all resources safely without relying on `destroy.sh`.

> If you prefer to use the script, run `bash infrastructure/terraform/destroy.sh` instead. It handles the S3 cleanup automatically.

### Step 1 – Identify the S3 Bucket Name

```bash
cd infrastructure/terraform
terraform output bucket_name
```

### Step 2 – Empty the S3 Bucket

Delete all objects in the bucket:

```bash
aws s3 rm s3://<bucket_name> --recursive
```

If versioning is enabled on the bucket, also delete all object versions and delete markers:

```bash
# Delete all versions
aws s3api list-object-versions --bucket <bucket_name> \
  --query 'Versions[].{Key:Key,VersionId:VersionId}' \
  --output text | \
  while read KEY VID; do
    aws s3api delete-object --bucket <bucket_name> --key "$KEY" --version-id "$VID"
  done

# Delete all delete markers
aws s3api list-object-versions --bucket <bucket_name> \
  --query 'DeleteMarkers[].{Key:Key,VersionId:VersionId}' \
  --output text | \
  while read KEY VID; do
    aws s3api delete-object --bucket <bucket_name> --key "$KEY" --version-id "$VID"
  done
```

### Step 3 – Destroy All Terraform-Managed Resources

```bash
terraform destroy
```

Type `yes` when prompted. Terraform will destroy all resources, resolving dependencies automatically:

- EC2 instance and security group
- API Gateway and Lambda functions
- DynamoDB table
- SNS topic and subscriptions
- S3 bucket (now empty)
- IAM role and policies (if `create_role = true`)

### Step 4 – Release the Elastic IP

Destroying the EC2 instance does not automatically release the Elastic IP — you must do this manually to avoid ongoing charges.

1. In the AWS Console, go to **EC2 > Elastic IPs**
2. Select the IP associated with the IS215-Project instance
3. Click **Actions > Disassociate Elastic IP address**, then confirm
4. Click **Actions > Release Elastic IP address**, then confirm

### Step 5 – Verify Destruction

Confirm that no resources remain:

```bash
# Check for any remaining S3 buckets with the project prefix
aws s3 ls | grep upou

# Check for Lambda functions
aws lambda list-functions \
  --query 'Functions[?starts_with(FunctionName, `upou`)].FunctionName'

# Check for DynamoDB tables
aws dynamodb list-tables \
  --query 'TableNames[?starts_with(@, `tickets`)]'
```

If any resources remain (e.g., because the Terraform state is out of sync), remove them manually from the AWS Console or using the AWS CLI.

> The `terraform.tfstate` file will still exist locally after teardown. Do not delete it unless you are certain all resources have been destroyed — it tracks what Terraform has provisioned and is needed to detect drift.
