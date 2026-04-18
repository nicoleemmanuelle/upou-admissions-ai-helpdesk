# Terraform Setup – UPOU Admissions AI Helpdesk

This guide walks you through deploying, updating, and destroying your infrastructure using Terraform.

Supports:
- macOS
- Windows (WSL)

---

## 📌 Overview

This setup provisions:

- S3 Bucket (knowledge base files from `/kb`)
- Lambda Function (from `/lambda/lambda.zip`)
- API Gateway (`/ask` endpoint)
- DynamoDB (ticket storage)
- EC2 Instance (frontend)
- Security Group

---

## 📂 Project Structure

```
~/terraform/
├── infrastructure/
│   └── terraform/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars.example
│       ├── destroy.sh
│       └── versions.tf
├── lambda/
│   ├── lambda.zip
│   ├── lambda_function.py
│   └── requirements.txt
└── kb/
    ├── admissions.md
    └── admission2.md
```

---

## ⚙️ Prerequisites

Install the following:

- Terraform
- AWS CLI
- Git
- Python 3
- zip (WSL only)

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
sudo apt install terraform awscli git python3 python3-pip zip -y
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

## 🚀 Step 2: Navigate to Terraform Directory

```
cd ~/terraform/infrastructure/terraform
```

---

## 📝 Step 3: Create Variables File

```
cp terraform.tfvars.example terraform.tfvars
```

Edit:

```
vim terraform.tfvars
```

Update:

```
openai_api_key = "YOUR_OPENAI_KEY"
```

---

## 📦 Step 4: Prepare Lambda Package

```
cd ~/terraform/lambda
pip3 install -r requirements.txt -t .
zip -r lambda.zip .
```

---

## 📂 Step 5: Verify Knowledge Base Files

```
cd ~/terraform/kb
ls
```

---

## ⚡ Step 6: Initialize Terraform

```
cd ~/terraform/infrastructure/terraform
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

- api_url
- ec2_public_ip
- bucket_name
- lambda_name
- dynamodb_table_name

---

## 🧪 Step 8: Test the API

```
curl -X POST <API_URL> \
  -H "Content-Type: application/json" \
  -d '{"question":"Who can apply to UPOU?"}'
```

---

## 🔄 Updating Lambda Code

```
cd ~/terraform/lambda
zip -r lambda.zip .
cd ~/terraform/infrastructure/terraform
terraform apply
```

---

## 🧹 Destroy Resources (IMPORTANT)

```
cd ~/terraform/infrastructure/terraform
chmod +x destroy.sh
./destroy.sh
```

---

## ⚠️ Common Issues

- S3 not empty → handled by script
- Lambda not updating → rebuild zip
- Expired AWS creds → re-export

---

## 🔐 Security Notes

- Do NOT commit terraform.tfvars
- Keep API keys private

---

## 🧠 Notes

- `/kb` auto-uploaded to S3
- Lambda path: `../lambda/lambda.zip`
- API path: `/dev/ask`

---

## 🏁 Summary

- Automated infrastructure
- Serverless backend
- Public API
- Storage (S3 + DynamoDB)
- EC2 frontend
- Easy cleanup
