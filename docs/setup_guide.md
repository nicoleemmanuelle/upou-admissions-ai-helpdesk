# UPOU Admissions AI Helpdesk — Setup Guide

This guide walks you through setting up and running the entire project from scratch after cloning the repo.

---

## Prerequisites

Install the following on your machine before starting:

| Tool | Version | Install |
|------|---------|---------|
| **Node.js** | v18+ | https://nodejs.org/ |
| **npm** | comes with Node.js | — |
| **Python 3** | 3.9+ | https://www.python.org/ or macOS: `xcode-select --install` |
| **pip3** | comes with Python 3 | — |
| **AWS CLI** | v2 | https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html |
| **Terraform** | v1.x | https://developer.hashicorp.com/terraform/install |

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/nicoleemmanuelle/upou-admissions-ai-helpdesk.git
cd upou-admissions-ai-helpdesk
git checkout backend-kim
```

---

## Step 2: Configure AWS Credentials

Go to **AWS Academy Learner Lab** → Start Lab → Click **AWS Details** → Copy the credentials.

```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_SESSION_TOKEN="your_session_token"
```

> **Note:** Learner Lab credentials expire every ~4 hours. You need to re-export them each session.

Verify it works:

```bash
aws sts get-caller-identity
```

---

## Step 3: Build the Lambda Package

The Lambda runs on **Amazon Linux (x86_64)**, so dependencies must be installed for that platform — even if you're on Mac or Windows.

```bash
cd backend/lambda

# Install dependencies for Linux Lambda
pip3 install -r requirements.txt \
  -t /tmp/lambda_build \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --python-version 3.12

# Copy source files into the build
cp handler.py openai_service.py s3_retriever.py prompt.txt /tmp/lambda_build/

# Create the zip
cd /tmp/lambda_build
zip -r lambda.zip . -x "*.pyc" "*__pycache__*" "*.dist-info/*" "bin/*"

# Move zip back to the repo (Terraform expects it here)
cp lambda.zip /path/to/upou-admissions-ai-helpdesk/backend/lambda/lambda.zip
```

---

## Step 4: Deploy Infrastructure with Terraform

Terraform creates: S3 bucket (knowledge base), Lambda function, API Gateway, DynamoDB table, EC2 instance.

```bash
cd infrastructure/terraform

# Create your config file from the example
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set:

```hcl
aws_region     = "us-east-1"
openai_api_key = "your-openai-api-key"
```

> Ask your team lead for the OpenAI API key, or use the UPOU endpoint key.

Then deploy:

```bash
terraform init
terraform apply -auto-approve
```

After it completes, note the outputs:

```
api_url      = "https://xxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/ask"
bucket_name  = "upou-kb-xxxxxxxx"
lambda_name  = "upou-ai-function"
```

---

## Step 5: Fix CORS (Required)

Terraform creates only the POST method. You also need an OPTIONS method for CORS preflight:

```bash
# Get your API ID and resource ID
API_ID=$(aws apigateway get-rest-apis --region us-east-1 --query "items[?name=='upou-api'].id" --output text)
RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region us-east-1 --query "items[?pathPart=='ask'].id" --output text)
LAMBDA_ARN=$(aws lambda get-function --function-name upou-ai-function --region us-east-1 --query "Configuration.FunctionArn" --output text)

# Create OPTIONS method with Lambda proxy
aws apigateway put-method --rest-api-id $API_ID --resource-id $RESOURCE_ID \
  --http-method OPTIONS --authorization-type NONE --region us-east-1

aws apigateway put-integration --rest-api-id $API_ID --resource-id $RESOURCE_ID \
  --http-method OPTIONS --type AWS_PROXY --integration-http-method POST \
  --uri "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations" \
  --region us-east-1

# Redeploy the API
aws apigateway create-deployment --rest-api-id $API_ID --stage-name dev --region us-east-1
```

---

## Step 6: Upload Knowledge Base (if not auto-uploaded)

Terraform auto-uploads CSV files from `knowledge-base/output for S3/`. If that folder is missing or you need to re-upload:

```bash
BUCKET=$(aws s3 ls --region us-east-1 | grep upou-kb | awk '{print $3}')
aws s3 cp "knowledge-base/output for S3/01_rag_output_main.csv" "s3://$BUCKET/" --region us-east-1
aws s3 cp "knowledge-base/output for S3/02_rag_output_addtl.csv" "s3://$BUCKET/" --region us-east-1
```

---

## Step 7: Update the Frontend API URL

After Terraform deploys, you get a new API Gateway URL. Update it in the frontend:

Edit `frontend/src/api.js`:

```js
const API_URL = "https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/dev/ask";
```

Replace `YOUR-API-ID` with the actual API ID from the Terraform output.

---

## Step 8: Run the Frontend Locally

```bash
cd frontend
npm install
npm start
```

Opens at **http://localhost:3000**

---

## Step 9 (Optional): Deploy Frontend to S3 for a Public URL

```bash
cd frontend
npm run build

# Create a bucket
FRONTEND_BUCKET="upou-helpdesk-frontend-$(date +%s)"
aws s3 mb "s3://$FRONTEND_BUCKET" --region us-east-1

# Enable static website hosting
aws s3 website "s3://$FRONTEND_BUCKET" --index-document index.html --error-document index.html

# Allow public access
aws s3api put-public-access-block --bucket "$FRONTEND_BUCKET" \
  --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Set public read policy
cat > /tmp/policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicRead",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::$FRONTEND_BUCKET/*"
  }]
}
EOF
aws s3api put-bucket-policy --bucket "$FRONTEND_BUCKET" --policy file:///tmp/policy.json

# Upload build
aws s3 sync build/ "s3://$FRONTEND_BUCKET/"

echo "Live at: http://$FRONTEND_BUCKET.s3-website-us-east-1.amazonaws.com"
```

---

## Verify Everything Works

Test the API directly:

```bash
curl -s -X POST https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/dev/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the admission requirements?"}' | python3 -m json.tool
```

You should get a JSON response with admissions info.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `No module named 'pydantic_core._pydantic_core'` | Rebuild Lambda zip with `--platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.12` |
| `field larger than field limit (131072)` | Already fixed in `s3_retriever.py` — uses `csv.field_size_limit(1_000_000)` |
| CORS errors in browser | Run Step 5 to add OPTIONS method, then redeploy API Gateway |
| `NoCredentials` error | Re-export your AWS Learner Lab credentials (they expire) |
| OpenAI 401 error | Check that `openai_api_key` in `terraform.tfvars` is correct |
| "I'm sorry, I don't have enough information..." | S3 knowledge base may be empty — run Step 6 to upload CSVs |
| Lambda timeout (30s) | Cold start + S3 read + OpenAI call can be slow; retry once |

---

## Project Architecture

```
User (Browser)
      ↓
Frontend (React on S3 or localhost)
      ↓ POST /ask
API Gateway
      ↓
Lambda (handler.py)
      ├── s3_retriever.py  →  S3 Knowledge Base (CSV files)
      └── openai_service.py →  OpenAI API (gpt-4o-mini)
      ↓
Response back to User
```

---

## Key Files

| File | Purpose |
|------|---------|
| `backend/lambda/handler.py` | Lambda entry point, CORS handling |
| `backend/lambda/s3_retriever.py` | Retrieves relevant KB chunks from S3 |
| `backend/lambda/openai_service.py` | Calls OpenAI with context + prompt |
| `backend/lambda/prompt.txt` | System prompt for the AI |
| `backend/lambda/requirements.txt` | Python dependencies (openai, boto3) |
| `frontend/src/App.js` | React chat UI |
| `frontend/src/api.js` | API call to Lambda (update URL here) |
| `infrastructure/terraform/main.tf` | All AWS resources |
| `infrastructure/terraform/terraform.tfvars.example` | Template for config |
