# upou-admissions-ai-helpdesk

# 📘 UPOU Admissions AI Helpdesk Assistant

## 👥 Group Members
- Member 1 – Project Lead / Integration (Nicole/Christian)
- Member 2 – Knowledge Base Engineer (Egie) 
- Member 3 – Knowledge Base Engineer (Christian)  
- Member 4 – Backend Developer (Kim) 
- Member 5 – AI Engineer (Nicole) 
- Member 6 – Frontend Developer (Elvin / Rosel) 
- Member 7 – Frontend–Backend Integrator (John Rey) 
- Member 8 – Cloud Engineer (Terraform) (Jv) 
- Member 9 – Ticketing & QA Engineer (John Rey) 

---

## 📌 Project Overview

This project is a **Context-Aware AI Helpdesk Assistant** designed to answer inquiries related to the **University of the Philippines Open University (UPOU) Admissions**.

The system uses a **Retrieval-Augmented Generation (RAG)** approach to ensure that all responses are:
- ✅ Based on official UPOU documents  
- ✅ Accurate and context-aware  
- ✅ Free from hallucinations  

If the system cannot find the answer in the knowledge base, it will:
- Politely inform the user  
- Offer to create a **support ticket**

---

## 🎯 Key Features

- 💬 Chat-based helpdesk interface  
- 📚 Answers based strictly on official UPOU Admission data  
- ⚠️ Refuses off-topic questions  
- 🧠 Context-aware responses using AWS + OpenAI  
- 🎫 Automatic ticket creation for unanswered queries  
- 🖥️ Deployed on AWS EC2 with public access  

---

## 🏗️ System Architecture

```
User (Web Browser)
        ↓
Frontend (EC2)
        ↓
AWS Lambda (Middleware)
        ↓
Amazon S3 (Knowledge Base)
        ↓
OpenAI API (Response Generation)
        ↓
Response back to User
```
Optional:
```
No Answer Found → DynamoDB / AWS SES (Ticketing)
```

---

## ☁️ Technologies Used

### 🔹 AWS Services
- Amazon EC2 – Web hosting  
- Amazon S3 – Knowledge base storage  
- AWS Lambda – Backend processing  
- AWS IAM – Secure access (LabRole)  
- Amazon DynamoDB – Ticket storage  
- Amazon SES (Optional) – Email notifications  

### 🔹 Development Tools
- Python (Backend, Lambda)  
- JavaScript / React (Frontend)  
- Terraform (Infrastructure as Code)  
- OpenAI API (AI response generation)  

---

## 📂 Project Structure

```
upou-admissions-ai-helpdesk/
│
├── frontend/                 # Member 6 & 7 - Chat UI
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatBox.js
│   │   │   ├── Message.js
│   │   ├── App.js
│   │   ├── api.js
│   ├── package.json
│
├── backend/                  # Member 4 & 5 - Lambda + OpenAI logic
│   ├── lambda/
│   │   ├── handler.py
│   │   ├── openai_service.py
│   │   ├── s3_retriever.py
│   │   ├── prompt.txt
│   │   └── requirements.txt
│
├── data-processing/          # Member 2 & 3 - Data cleaning & formatting
│   ├── raw/
│   ├── processed/
│   ├── scripts/
│   │   ├── clean_data.py
│   │   ├── format_to_md.py
│   │   └── upload_to_s3.py
│
├── infrastructure/           # Member 8 - Terraform scripts
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── terraform.tfvars
│
├── ticketing/                # Member 9 - Ticketing system
│   ├── create_ticket.py
│   ├── ses_email.py
│   └── dynamodb.py
│
├── integration/              # Member 1 - API + testing
│   ├── api_gateway.py
│   └── end_to_end_test.py
│
├── docs/                     # Documentation
│   ├── architecture.md
│   ├── setup_guide.md
│
├── .env.example
├── README.md
└── .gitignore
```

---

## 📚 Knowledge Base

The chatbot uses **10–15 structured documents** related to:
- Admission requirements  
- Application procedures  
- Deadlines  
- FAQs  
- Contact details  

All documents are:
- Stored in **Amazon S3**
- Formatted in **Markdown / CSV**
- Organized by category for efficient retrieval  

---

## ⚙️ How It Works (RAG Flow)

1. User submits a question via the web interface  
2. Request is sent to AWS Lambda  
3. Lambda retrieves relevant documents from S3  
4. Context + question is sent to OpenAI API  
5. AI generates a response based on provided context  
6. Response is returned to the user  

If no relevant data is found:
- A fallback message is returned  
- A ticket is created in DynamoDB  

---

## 🤖 System Prompt Design

The chatbot is guided by a system prompt that ensures:

- It acts as a **professional UPOU helpdesk agent**
- It only answers based on **provided documents**
- It does **not hallucinate**
- It refuses **off-topic questions**
- It provides a **fallback response when unsure**

---

## 🚀 Deployment Guide

### 🔹 Prerequisites
- AWS Learner Lab account  
- OpenAI API Key  
- Terraform installed  

---

### 🔹 Steps

#### 1. Clone Repository
```bash
git clone https://github.com/your-repo/upou-admissions-ai-helpdesk.git
cd upou-admissions-ai-helpdesk
```

#### 2. Setup Environment Variables
Create a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
AWS_REGION=ap-southeast-1
```

#### 3. Deploy Infrastructure (Terraform)
```bash
cd infrastructure/terraform
terraform init
terraform apply
```

#### 4. Deploy Lambda
- Zip backend files
- Upload to AWS Lambda
- Set handler: `handler.lambda_handler`

#### 5. Run Frontend (EC2)
```bash
cd frontend
npm install
npm start
```

---

### 🧪 Testing

The system was tested using:
- ✅ Admission-related queries
- ❌ Off-topic questions (e.g., jokes, cooking)
- ⚠️ Edge cases (missing data, unclear queries)

---

### ⚠️ Error Handling
- Displays loading state during API calls
- Handles API timeouts gracefully
- Returns fallback message if no data is found

---

### 🔐 Security Practices
- No API keys stored in repository
- Uses `.env` for sensitive data
- AWS IAM Role (LabRole) used for permissions

---

### 🎥 Demo
- 📺 Demo Video: (Insert YouTube Link Here)
- 🌐 Live Application: (Insert EC2 URL Here)

---

### 📊 Project Evaluation Alignment
| Criteria | Implementation |
| :--- | :--- |
| AWS Integration | EC2, Lambda, S3, IAM |
| Data Quality | Structured KB (10–15 docs) |
| Prompt Engineering | Controlled AI responses |
| UI/UX | Chat interface with history |
| Error Handling | Loading + fallback responses |

---

### 📌 Future Improvements
- 🔍 Vector search (FAISS / embeddings)
- 📊 Analytics dashboard for queries
- 🌍 Multi-language support
- 🤝 Live agent escalation

---

### 📜 License
This project is for academic purposes under IS 215.
