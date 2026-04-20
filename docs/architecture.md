# 🏗️ System Architecture

## 📌 Overview

This project is an AI-powered admissions helpdesk built using a serverless architecture. It combines a frontend interface, backend AWS Lambda functions, and a knowledge base stored in S3, enhanced by AI-generated responses.

---

## 🧩 High-Level Architecture

```
User (Browser)
      ↓
Frontend (Vite + JS)
      ↓
API Gateway
      ↓
AWS Lambda (Python Backend)
      ↓
S3 (Knowledge Base)
      ↓
OpenAI API
```

---

## ⚙️ Components

### 1. Frontend

**Location:** `frontend/`

* Built using Vite + JavaScript
* Provides chat interface for users
* Sends user queries to backend API

---

### 2. API Gateway

**Location:** `integration/api_gateway.py`

* Entry point for HTTP requests
* Routes requests to Lambda function

---

### 3. Backend (AWS Lambda)

**Location:** `backend/lambda/`

Key files:

* `handler.py` → main entry point
* `openai_service.py` → handles AI interaction
* `s3_retriever.py` → retrieves data from S3

Responsibilities:

* Process user queries
* Retrieve relevant knowledge
* Call AI service
* Return responses to frontend

---

### 4. Knowledge Base (RAG)

**Location:** `knowledge-base/`

* Data processed into CSV/Markdown format
* Uploaded to S3
* Used for retrieval-augmented generation

---

### 5. Data Processing

**Location:** `data-processing/scripts/`

* Cleans and formats raw data
* Converts to structured formats
* Prepares data for AI retrieval

---

### 6. Infrastructure (Terraform)

**Location:** `infrastructure/terraform/`

Manages:

* AWS Lambda
* IAM Roles
* S3 Buckets
* Other cloud resources

---

## 🔄 Request Flow

1. User sends a message from the frontend
2. Frontend calls API Gateway
3. API Gateway triggers Lambda
4. Lambda retrieves relevant data from S3
5. Lambda sends request to AI service
6. Response is returned to frontend
7. Frontend displays the result

---

## 🔐 Security

* API keys stored as environment variables
* IAM roles restrict access to AWS resources
* No sensitive data exposed in frontend

---

## 🚀 Deployment

1. Provision infrastructure using Terraform
2. Deploy Lambda function
3. Upload knowledge base to S3
4. Deploy frontend

---

## 📈 Scalability

* AWS Lambda auto-scales based on demand
* S3 supports large-scale storage
* API Gateway handles traffic spikes

---

## 🧠 Key Concepts

* Retrieval-Augmented Generation (RAG)
* Serverless architecture
* Decoupled system design

---

## 📌 Future Improvements

* Add caching layer (Redis / DynamoDB)
* Improve semantic search accuracy
* Add authentication system
* Add monitoring and logging (CloudWatch)

