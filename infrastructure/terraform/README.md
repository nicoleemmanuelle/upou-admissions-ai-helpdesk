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
* **Security Group** – manages networking rules for the EC2 instance
* **IAM Role** – Lambda permissions (optional creation)

---

## 📂 Project Structure

```
upou-admissions-ai-helpdesk/
├── backend/
│   └── lambda/
│       ├── handler.py
│       ├── openai_service.py
│       ├── s3_retriever.py
│       ├── prompt.txt
│       ├── package_clean.sh
│       └── lambda.zip
├── knowledge-base/
│   └── output_for_s3/
│       ├── *.md
│       └── *.csv
├── infrastructure/
│   └── terraform/
│       ├── main.tf
│       ├── lambda_role.tf
│       ├── variables.tf
│       ├── terraform.tfvars.example
│       ├── destroy.sh
│       └── versions.tf
```

---

## ⚙️ Prerequisites

Install:

* Terraform
* AWS CLI
* Git
* Python 3
* zip (for Lambda packaging)

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

```bash
# Option 1: Environment variables (temporary session, e.g. AWS Academy)
export AWS_ACCESS_KEY_ID="YOUR_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET"
export AWS_SESSION_TOKEN="YOUR_TOKEN"

# Option 2: AWS CLI config (recommended for long-term use)
aws configure
```

Verify:

```bash
aws sts get-caller-identity
```

---

## 🚀 Step 2: Go to Terraform Directory

```
cd infrastructure/terraform
```

---

### 📝 Step 3: Create Variables File

```bash
cp terraform.tfvars.example terraform.tfvars
vim terraform.tfvars
```

Update values:

```hcl
aws_region      = "us-east-1"
OPENAI_API_KEY  = "YOUR_OPENAI_API_KEY"
create_role     = true
lambda_role     = ""  # Leave empty if create_role = true
```

### Using an existing IAM role

If you already have a role:

```hcl
create_role  = false
lambda_role  = "arn:aws:iam::123456789012:role/your-existing-role"
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
