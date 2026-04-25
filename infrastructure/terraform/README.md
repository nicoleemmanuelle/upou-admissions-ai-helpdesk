# Terraform Setup – UPOU Admissions AI Helpdesk

This guide explains how to **deploy, test, update, and destroy** the infrastructure using Terraform.

Supports:

* macOS
* Windows (WSL)

---

## 📌 Overview

This project provisions a **serverless AI helpdesk system** using AWS:

* **S3 Bucket** – stores knowledge base files and Lambda package
* **Lambda Function** – handles AI queries (RAG-based)
* **API Gateway** – exposes `/ask` endpoint
* **DynamoDB** – stores fallback support tickets
* **EC2 Instance** – hosts frontend
* **IAM Role** – Lambda permissions (optional creation)

---

## 📂 Project Structure

```
upou-admissions-ai-helpdesk/
├── backend/
│   └── lambda/
│       ├── handler.py                # Main Lambda handler
│       ├── openai_service.py        # OpenAI integration
│       ├── s3_retriever.py          # Retrieves context from S3
│       ├── prompt.txt               # Prompt template for LLM
│       ├── package_clean.sh         # Script to package Lambda
│       └── lambda.zip               # Packaged Lambda (build artifact)
│
├── frontend/
│   ├── src/                         # React/Vite source code
│   ├── public/                      # Static public assets
│   ├── index.html                  # Entry HTML file
│   ├── package.json                # Dependencies and scripts
│   ├── package-lock.json           # Locked dependency versions
│   ├── vite.config.js              # Vite configuration
│   ├── tailwind.config.js          # Tailwind CSS config
│   ├── postcss.config.js           # PostCSS config
│   └── dist/                       # Build output (NOT committed)
│
├── knowledge-base/
│   └── output_for_s3/
│       ├── *.md                    # Knowledge base markdown files
│       └── *.csv                   # Structured knowledge data
│
├── infrastructure/
│   └── terraform/
│       ├── main.tf                 # Main infrastructure definition
│       ├── lambda_role.tf          # IAM role (optional)
│       ├── variables.tf            # Input variables
│       ├── terraform.tfvars.example# Example variables file
│       ├── destroy.sh              # Cleanup script
│       └── versions.tf             # Provider versions
│
└── .gitignore                      # Ignored files (secrets, builds)
```

---

## ⚙️ Prerequisites

Install:

* Terraform
* AWS CLI
* Git
* Python 3

---

## 🖥️ Setup

### 🍎 macOS

```
brew install terraform awscli git python
```

---

### 🪟 Windows (WSL)

```
sudo apt update
sudo apt install terraform awscli git python3 zip -y
```

---

## 🔐 Step 1: Configure AWS Credentials

```
export AWS_ACCESS_KEY_ID="YOUR_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET"
export AWS_SESSION_TOKEN="YOUR_TOKEN"
```

Verify:

```
aws sts get-caller-identity
```

---

## 🚀 Step 2: Go to Terraform Directory

```
cd infrastructure/terraform
```

---

## 📝 Step 3: Create Variables File

```
cp terraform.tfvars.example terraform.tfvars
vim terraform.tfvars
```

Update values:

```
aws_region     = "us-east-1"
openai_api_key = "YOUR_OPENAI_KEY"
create_role    = false
lambda_role    = "YOUR_EXISTING_ROLE_ARN"
```

> Set `create_role = true` if Terraform should create the IAM role.

---

## 📦 Step 4: Package Lambda (IMPORTANT)

Use the clean packaging approach:

```
cd ../../backend/lambda
./package_clean.sh
```

This creates:

```
backend/lambda/lambda.zip
```

---

## 📂 Step 5: Verify Knowledge Base

```
cd ../../knowledge-base/output_for_s3
ls
```

Ensure `.md` or `.csv` files exist.

---

## ⚡ Step 6: Initialize Terraform

```
cd ../../infrastructure/terraform
terraform init
```

---

## 🚀 Step 7: Deploy Infrastructure

```
terraform apply
```

Type:

```
yes
```

---

## 🌐 Step 8: Frontend Deployment (EC2 + S3)

The frontend is automatically deployed using:

* **EC2 (nginx)** – serves the UI
* **S3 (public bucket)** – stores built frontend files
* **Terraform user_data** – bootstraps the server

---

### 📦 Frontend Build (IMPORTANT)

Before running Terraform, build the frontend:

```bash
cd frontend
npm install
npm run build
```

This generates:

```
frontend/dist/
```

---

### ⚙️ How Deployment Works

During `terraform apply`, the EC2 instance:

1. Installs nginx
2. Downloads `index.html` from S3
3. Dynamically detects asset files (JS/CSS)
4. Downloads all required assets
5. Downloads static images (e.g., logo)
6. Serves the frontend on port 80

---

### 🧠 Dynamic Asset Handling (IMPORTANT)

The system avoids hardcoded filenames using:

```bash
grep + dynamic asset download
```

This ensures:

* Works even after `npm run build`
* Handles hashed filenames automatically
* Prevents broken UI after updates

---

### 🖼️ Static Assets Fix (Logo Issue)

Some assets (e.g., images) are not referenced in `index.html`.

Fix applied:

```bash
manual download via curl
```

Example:

```
assets/up-seal.png
```

---

### 🌍 Access Frontend

After deployment:

```
http://<ec2_public_ip>
```

---

### 🧪 Test Frontend

Try:

```
What programs does UPOU offer?
```

Expected:

* UI loads correctly
* Styling works
* Logo is visible
* Chat responds correctly

---

### 🔄 Updating Frontend

After making changes:

```bash
cd frontend
npm run build

cd ../infrastructure/terraform
terraform taint aws_instance.frontend
terraform apply
```

---

### ⚠️ Notes

* `dist/` is NOT committed (build artifact)
* Always rebuild before Terraform
* S3 bucket must remain public (AWS Academy limitation)

---

## 🔐 Frontend Environment Variables (.env)

The frontend requires an environment file to connect to the deployed backend API.

---

### 📁 File Location

Create this file:

```bash
frontend/.env
```

---

### 📝 Required Variable

```env
VITE_API_URL=https://<api_id>.execute-api.us-east-1.amazonaws.com/dev/ask
```

---

### 🔍 How to Get the API URL

After running `terraform apply`, check the output:

```text
api_url = "https://<api_id>.execute-api.us-east-1.amazonaws.com/dev/ask"
```

👉 Copy that value and paste it into your `.env` file.

---

### ⚠️ Important Notes

* This file is **required for the frontend to work**
* Do NOT commit `.env` to Git (already ignored via `.gitignore`)
* If the API URL changes (new deployment), update this file

---

### 🔄 After Updating `.env`

Rebuild the frontend:

```bash
cd frontend
npm run build
```

Then redeploy:

```bash
cd ../infrastructure/terraform
terraform apply
```

---

### 🧠 Example

```env
VITE_API_URL=https://oq9izlb4ge.execute-api.us-east-1.amazonaws.com/dev/ask
```


## 🏁 Updated Summary

* Fully automated infrastructure (Terraform)
* Serverless AI backend (Lambda + OpenAI)
* Knowledge-based responses (S3)
* Ticket fallback system (DynamoDB)
* Public API (API Gateway)
* Frontend hosted via EC2 (nginx) with dynamic asset deployment
* Easy cleanup with script


## 📤 Outputs

After deployment, Terraform will show:

* `api_url` → your API endpoint
* `ec2_public_ip` → frontend server
* `bucket_name`
* `lambda_name`
* `dynamodb_table_name`

---

## 🧪 Step 8: Test the API

```
curl -X POST <API_URL> \
  -H "Content-Type: application/json" \
  -d '{"query":"How do I apply to UPOU?"}'
```

---

## 🔄 Updating Lambda Code

After making changes:

```
cd ../../backend/lambda
./package_clean.sh

cd ../../infrastructure/terraform
terraform apply
```

---

## 🔄 Updating Knowledge Base

1. Update files inside:

```
knowledge-base/output_for_s3/
```

2. Re-run:

```
terraform apply
```

---

## 🧹 Destroy Resources (IMPORTANT)

```
cd infrastructure/terraform
chmod +x destroy.sh
./destroy.sh
```

This:

* empties S3 bucket
* destroys all resources

---

## ⚠️ Common Issues

**Lambda not updating**

* Re-run `package_clean.sh`

**Always returning fallback**

* Check S3 files exist and match query keywords

**API returns 500**

* Check CloudWatch logs
* Verify `OPENAI_API_KEY`

**S3 deletion fails**

* Use `destroy.sh` (already handles cleanup)

---

## 🔐 Security Notes

* Do NOT commit `terraform.tfvars`
* Do NOT expose API keys
* Prefer AWS Secrets Manager for production

---

## 🧠 Notes

* Knowledge base is automatically uploaded to S3
* Lambda uses **RAG (Retrieval-Augmented Generation)**
* API endpoint:

```
/dev/ask
```

---

## 🏁 Summary

* Fully automated infrastructure (Terraform)
* Serverless AI backend (Lambda + OpenAI)
* Knowledge-based responses (S3)
* Ticket fallback system (DynamoDB)
* Public API (API Gateway)
* Frontend hosting (EC2)
* Easy cleanup with script
