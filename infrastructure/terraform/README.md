# Terraform Setup – UPOU Admissions AI Helpdesk

This guide explains how to deploy and manage the infrastructure using Terraform.
Supports **macOS** and **Windows (WSL)**.

---

## 📌 Overview

This Terraform setup provisions:

* S3 Bucket (knowledge base)
* Lambda Function (AI backend)
* API Gateway (public endpoint)
* DynamoDB (ticket storage)
* EC2 Instance (frontend hosting)
* Security Group

---

## ⚙️ Prerequisites

You need:

* AWS Academy account
* Terraform
* AWS CLI
* Git
* Python (for Lambda packaging)

---

## 🖥️ Setup by OS

### 🍎 macOS (Recommended)

Install using Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install terraform awscli git python
```

---

### 🪟 Windows (WSL)

Inside WSL:

```bash
sudo apt update
sudo apt install terraform awscli git python3 python3-pip zip -y
```

---

## 🔐 AWS Credentials Setup

Set your AWS session credentials:

```bash
export AWS_ACCESS_KEY_ID="YOUR_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET"
export AWS_SESSION_TOKEN="YOUR_TOKEN"
```

---

## 🚀 Deployment Steps

### 1. Go to Terraform folder

```bash
cd infrastructure/terraform
```

---

### 2. Create variables file

```bash
cp terraform.tfvars.example terraform.tfvars
```

---

### 3. Add OpenAI API key

Edit:

```hcl
openai_api_key = "YOUR_KEY_HERE"
```

---

### 4. Initialize Terraform

```bash
terraform init
```

---

### 5. Apply configuration

```bash
terraform apply
```

Type:

```text
yes
```

---

## 📤 Outputs

After deployment, you will get:

* `api_url` – API endpoint
* `ec2_public_ip` – EC2 instance IP
* `bucket_name` – S3 bucket
* `lambda_name` – Lambda function
* `dynamodb_table_name` – DynamoDB table

---

## 🧪 Testing the API

```bash
curl -X POST <API_URL> \
  -H "Content-Type: application/json" \
  -d '{"question":"Who can apply to UPOU?"}'
```

---

## 🔄 Updating Lambda Code

### 1. Go to lambda folder

```bash
cd ~/terraform/lambda
```

### 2. Install dependencies (if needed)

```bash
pip3 install requests -t .
```

### 3. Zip the code

```bash
zip -r lambda.zip .
```

### 4. Re-apply Terraform

```bash
cd ~/terraform/upou-admissions-ai-helpdesk/infrastructure/terraform
terraform apply
```

---

## 🧹 Destroy Resources (IMPORTANT)

To avoid AWS charges:

```bash
./destroy.sh
```

---

## 🔐 Security Notes

* `terraform.tfvars` is NOT committed (contains secrets)
* Use `terraform.tfvars.example` as template
* Never push API keys to GitHub

---

## 🧠 Notes for macOS Users

* No need to install `zip` (already included)
* All commands work directly in Terminal
* No WSL required

---

## 🧠 Notes for Windows Users

* Use **WSL (Ubuntu recommended)**
* Run all commands inside WSL
* Avoid using PowerShell for Terraform setup

---

## 🏁 Summary

This setup allows:

* Automated infrastructure deployment
* Consistent environment setup
* Secure handling of credentials
* Easy teardown to avoid costs
