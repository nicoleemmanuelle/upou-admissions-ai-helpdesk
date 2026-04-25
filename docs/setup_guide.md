# 📘 UPOU Admissions AI Helpdesk Assistant

## 👥 Group Members

* Member 1 – Project Lead / Integration (Nicole/Christian)
* Member 2 – Knowledge Base Engineer (Egie)
* Member 3 – Knowledge Base Engineer (Christian)
* Member 4 – Backend Developer (Kim)
* Member 5 – AI Engineer (Nicole)
* Member 6 – Frontend Developer (Elvin / Rosel)
* Member 7 – Frontend–Backend Integrator (John Rey)
* Member 8 – Cloud Engineer (Terraform) (Jv)
* Member 9 – Ticketing & QA Engineer (John Rey)

---

## 📌 Project Overview

This project is a **Context-Aware AI Helpdesk Assistant** designed to answer inquiries related to the **University of the Philippines Open University (UPOU) Admissions**.

It implements a **Retrieval-Augmented Generation (RAG)** approach, ensuring responses are:

* ✅ Based only on official UPOU documents
* ✅ Context-aware and accurate
* ✅ Free from hallucinations

If no relevant information is found:

* A fallback response is returned
* A **support ticket is automatically created** in DynamoDB

---

## 🎯 Key Features

* 💬 Chat-based helpdesk interface
* 📚 Answers strictly based on knowledge base
* 🧠 Context-aware AI using OpenAI
* 🎫 Automatic ticket creation (fallback system)
* ⚠️ Refuses off-topic or unsupported queries
* ☁️ Fully deployed on AWS using Terraform

---

## 🏗️ System Architecture

```
User (Browser)
     ↓
Frontend (EC2)
     ↓
API Gateway (/ask)
     ↓
AWS Lambda (handler.py)
     ↓
S3 (Knowledge Base)
     ↓
OpenAI API
     ↓
Response to User
```

Fallback Flow:

```
No Context Found → DynamoDB (Ticket Created)
```

---

## ☁️ Technologies Used

### 🔹 AWS Services

* Amazon EC2 – Frontend hosting
* Amazon S3 – Knowledge base + Lambda package
* AWS Lambda – Backend logic
* API Gateway – Public API endpoint
* Amazon DynamoDB – Ticket storage
* AWS IAM – Role management

### 🔹 Development Tools

* Python – Backend (Lambda)
* React / Vite – Frontend
* Terraform – Infrastructure as Code
* OpenAI API – AI response generation

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

## ⚙️ How It Works (RAG Flow)

1. User sends a query via frontend
2. Request hits API Gateway (`/ask`)
3. Lambda (`handler.py`) processes request
4. Retrieves matching documents from S3
5. Sends context + query to OpenAI
6. Returns generated response

If no context is found:

* Lambda creates a ticket in DynamoDB
* Returns fallback response

---

## 📦 Deployment Guide

### 🔹 Prerequisites

* AWS Learner Lab account
* Terraform installed
* AWS CLI configured
* OpenAI API Key

---

### 🔹 Steps

#### 1. Clone Repository

```bash
git clone <your-repo-url>
cd upou-admissions-ai-helpdesk
```

---

#### 2. Configure Terraform Variables

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
vim terraform.tfvars
```

Update:

```hcl
aws_region     = "us-east-1"
openai_api_key = "YOUR_API_KEY"
create_role    = false
lambda_role    = "YOUR_ROLE_ARN"
```

---

#### 3. Package Lambda (IMPORTANT)

```bash
cd ../../backend/lambda
./package_clean.sh
```

---

#### 4. Deploy Infrastructure

```bash
cd ../../infrastructure/terraform
terraform init
terraform apply
```

---

#### 5. Get API Endpoint

After deployment:

```
https://<api-id>.execute-api.<region>.amazonaws.com/dev/ask
```

---

## 🔐 Frontend Environment Setup (.env)

The frontend requires an environment variable to connect to the deployed backend API.

---

### 📁 File Location

Create the following file:

```bash
frontend/.env
```

---

### 📝 Required Variable

```env
VITE_API_URL=https://<api-id>.execute-api.us-east-1.amazonaws.com/dev/ask
```

---

### 🔍 How to Get the API URL

After running Terraform:

```bash
terraform apply
```

Check the output:

```text
api_url = "https://<api-id>.execute-api.us-east-1.amazonaws.com/dev/ask"
```

👉 Copy this value and paste it into your `.env` file.

---

### ⚠️ Important Notes

* This file is **required for the frontend to work**
* Do NOT commit `.env` (already ignored in `.gitignore`)
* If you redeploy Terraform, the API URL may change → update `.env`
* The frontend will NOT connect to the backend without this

---

### 🔄 After Setting `.env`

Rebuild the frontend:

```bash
cd frontend
npm install
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


## 🧪 Testing

### Using curl

```bash
curl -X POST <API_URL> \
  -H "Content-Type: application/json" \
  -d '{"query":"How do I apply to UPOU?"}'
```

---

### Expected Results

* ✅ Answer → if context exists
* ⚠️ Fallback + ticket → if no data found

---

## 🔄 Updating the System

### Update Lambda

```bash
cd backend/lambda
./package_clean.sh

cd ../../infrastructure/terraform
terraform apply
```

---

### Update Knowledge Base

1. Modify files in:

```
knowledge-base/output_for_s3/
```

2. Re-run:

```bash
terraform apply
```

---

## 🧹 Destroy Resources

```bash
cd infrastructure/terraform
./destroy.sh
```

---

## ⚠️ Common Issues

* Lambda not updating → rebuild zip
* Always fallback → check S3 content
* API error → check CloudWatch logs
* Credentials expired → re-export AWS creds

---

## 🔐 Security Practices

* Do NOT commit `terraform.tfvars`
* Do NOT expose API keys
* Use IAM roles for access control

---

## 📊 Evaluation Alignment

| Criteria        | Implementation                         |
| --------------- | -------------------------------------- |
| AWS Integration | EC2, Lambda, S3, API Gateway, DynamoDB |
| AI Integration  | OpenAI with controlled prompting       |
| Data Handling   | Structured knowledge base              |
| DevOps          | Terraform (IaC)                        |
| Error Handling  | Fallback + ticket system               |

---

## 📌 Future Improvements

* 🔍 Vector search (FAISS / embeddings)
* 📊 Query analytics dashboard
* 🌍 Multi-language support
* 🤝 Human agent escalation

---

## 📜 License

This project is for academic purposes under IS 215.
