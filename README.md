# UPOU Admissions AI Helpdesk

A context-aware AI helpdesk assistant for the University of the Philippines Open University (UPOU) Admissions Office. The system answers prospective student inquiries using Retrieval-Augmented Generation (RAG) grounded strictly in official UPOU documents, with automatic ticket creation for unanswered queries.

---

## Demo
[Watch the demo on YouTube](https://youtu.be/MRZZBYkwHl0?si=weY3y-8VIVWgjlK5)

## Table of Contents

- [Demo](#demo)
- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Knowledge Base](#knowledge-base)
- [DynamoDB Schema](#dynamodb-schema)
- [SSL / HTTPS Setup](#ssl--https-setup)
- [Teardown](#teardown)
- [Troubleshooting](#troubleshooting)
- [Team](#team)

---

## Overview

Students ask admissions questions through a React chat interface hosted on an EC2 instance. Each query is processed by an AWS Lambda function that:

1. Retrieves the most relevant documents from an S3 knowledge base using keyword scoring
2. Sends the retrieved context to OpenAI GPT-4o-mini to generate a grounded answer
3. Falls back to creating a support ticket in DynamoDB and notifying the admissions team via SNS email if no relevant context is found or if the model expresses uncertainty

The design prevents hallucinations by instructing the model to answer only from the provided context and by treating any uncertain response as a trigger for human escalation.

---

## Architecture

```
User (Browser)
  │
  ▼
EC2 Instance (Nginx + React SPA + static ticket.html)
  │
  ├──► POST /ask ──────────────────────────────────────────────────┐
  │                                                                │
  │                                                     AWS Lambda (Python 3.11)
  │                                                         │
  │                                         ┌──────────────┼──────────────┐
  │                                         ▼              ▼              ▼
  │                                    s3_retriever   openai_service  ticketing_services
  │                                         │              │              │
  │                                    S3 Bucket      OpenAI API     DynamoDB + SNS
  │
  └──► GET /id/{ticket_id} ──► AWS Lambda (ticket_lookup.py) ──► DynamoDB
```

**AWS services used:**

| Service | Purpose |
|---|---|
| EC2 (t2.micro) | Hosts Nginx serving the React frontend |
| API Gateway | REST endpoints (`/ask`, `/id/{ticket_id}`) |
| Lambda (Python 3.11) | RAG pipeline and ticket management |
| S3 | Knowledge base document storage |
| DynamoDB | Support ticket storage |
| SNS | Email notifications to admissions team |
| Textract | Extract text from scanned documents, PDFs, and images |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS |
| Backend | Python 3.11, AWS Lambda |
| AI / LLM | OpenAI GPT-4o-mini via `is215-openai.upou.io` |
| Infrastructure | Terraform (AWS provider ~5.0) |
| Web Server | Nginx on Amazon Linux 2 (EC2) |
| IaC | Terraform with random provider ~3.0 |

---

## Features

### Chat Interface
- Real-time Q&A with the UPOU Admissions AI
- Chat history persisted in browser `localStorage` with timestamps
- Date range filter modal to browse historical conversations
- Clear history button
- Responsive Tailwind CSS UI with UPOU branding (maroon, gold)
- Auto-scroll to the latest message

### Retrieval-Augmented Generation (RAG)
- Stop-word filtering removes common terms before scoring
- Remaining terms (>2 characters) are scored against all S3 documents by term frequency
- Top 5 documents selected; up to 12,000 characters of context sent to the model
- Temperature set to 0.0 for deterministic, factual responses
- System prompt instructs the model to answer only from provided context

### Automatic Ticket Fallback
Triggered when:
- No relevant S3 documents are found for the query, OR
- The OpenAI response contains uncertainty phrases (e.g., "I don't know", "I'm not sure")

On fallback, the system:
- Detects **category** via keyword matching: `admission`, `enrollment`, `finance`, `general`
- Detects **priority**: `HIGH` (urgent/asap), `MEDIUM` (help), `LOW` (default)
- Creates a ticket in DynamoDB with a UUID, timestamp, and full query
- Publishes an SNS email notification to the admissions team
- Returns a clickable "View your support ticket" link to the user

### Ticket Tracker Page (`/ticket.html`)
- Standalone static page served from EC2
- Displays ticket ID, status, question, answer, and submission time
- Accepts `?id=<ticket_id>` URL parameter to look up a specific ticket

### Infrastructure as Code
- All AWS resources defined in Terraform (`infrastructure/terraform/`)
- Compatible with AWS Learner Lab (supports both new IAM role creation and existing role reuse)
- Single-command deploy via `deploy.sh`

---

## Project Structure

```
upou-admissions-ai-helpdesk/
├── deploy.sh                          # One-command deploy script
├── setup_ssl.sh                       # Let's Encrypt SSL provisioning
│
├── backend/lambda/
│   ├── handler.py                     # Main Lambda entry point (RAG pipeline)
│   ├── openai_service.py              # OpenAI API integration
│   ├── s3_retriever.py                # Document retrieval and ranking
│   ├── ticketing_services.py          # Ticket creation + SNS notifications
│   ├── ticket_lookup.py               # GET /id/{ticket_id} handler
│   ├── prompt.txt                     # System prompt for the LLM
│   ├── requirements.txt               # Python dependencies (boto3)
│   └── package_clean.sh               # Builds lambda.zip
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # Main chat component
│   │   ├── api.js                     # sendQuery() — POST /ask
│   │   ├── main.jsx
│   │   └── components/
│   │       ├── ChatBox.js
│   │       └── Message.js
│   ├── public/
│   │   ├── ticket.html                # Support ticket tracker
│   │   └── assets/up-seal.png
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── knowledge-base/
│   ├── output_for_s3/                 # ~125 processed .md / .json / .csv files
│   ├── for_textract/                  # Raw PDFs/images for Textract
│   ├── urls.txt                       # UPOU URLs to scrape
│   ├── 00_admission_url_scraper.py    # Web scraper
│   ├── 03_kb_generationv2.py          # OpenAI-powered Markdown formatter
│   └── 03_aws_textractv2.py           # AWS Textract processor
│
├── infrastructure/terraform/
│   ├── main.tf                        # All AWS resources
│   ├── lambda_role.tf                 # IAM role and policies
│   ├── variables.tf                   # Variable declarations
│   ├── versions.tf                    # Provider version constraints
│   ├── terraform.tfvars.example       # Config template (copy and fill in)
│   └── destroy.sh                     # Teardown script (empties S3 first)
│
└── integration/
    ├── api_gateway.py                 # Integration test helper
    └── end_to_end_test.py             # End-to-end test
```

---

## Prerequisites

Ensure the following are installed and available in your shell:

- [Terraform](https://developer.hashicorp.com/terraform/install) ≥ 1.0
- [Node.js](https://nodejs.org/) ≥ 18 and npm
- Python 3.11+ and pip
- `zip` (for packaging Lambda)
- AWS credentials with permissions to create Lambda, S3, DynamoDB, SNS, API Gateway, EC2, and IAM resources

---

## Configuration

Copy the Terraform variables template and fill in the required values:

```bash
cp infrastructure/terraform/terraform.tfvars.example infrastructure/terraform/terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
aws_region         = "us-east-1"
openai_api_key     = "sk-..."
notification_email = "admissions@upou.edu.ph"

# Option A — let Terraform create a new role
create_role = true

# Option B — use an existing role (e.g., AWS Learner Lab)
# create_role  = false
# lambda_role  = "arn:aws:iam::123456789012:role/LabRole"
```

Export your AWS credentials:

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."   # required for Learner Lab
```

---

## Deployment

Run the single deploy script from the repository root:

```bash
bash deploy.sh
```

The script performs the following steps automatically:

1. Packages Lambda functions into `backend/lambda/lambda.zip`
2. Runs `terraform init` and `terraform apply` (Phase 1) — provisions Lambda, S3, DynamoDB, SNS, API Gateway
3. Extracts the API Gateway URL from Terraform output
4. Writes `frontend/.env` with `VITE_API_URL=<api_url>`
5. Runs `npm install` and `npm run build` in the frontend directory
6. Taints the EC2 instance to trigger redeployment with the new frontend build
7. Runs `terraform apply` (Phase 2) — deploys the updated frontend to EC2

At the end of the script, the public IP of the EC2 instance is printed. Open `http://<EC2_PUBLIC_IP>` in a browser to access the helpdesk.

**After deployment:** Check your inbox for an SNS subscription confirmation email and click the confirmation link to receive ticket notifications.

---

## API Reference

Both endpoints are served through Amazon API Gateway and support CORS (`Access-Control-Allow-Origin: *`).

### POST /ask

Submit a query to the helpdesk.

**Request body:**
```json
{ "query": "What are the admission requirements for MIS?" }
```

**Response — answer found:**
```json
{
  "response": "Applicants to the MIS program must..."
}
```

**Response — fallback ticket created:**
```json
{
  "response": "I was unable to find a specific answer. A support ticket has been created for you.",
  "ticket": {
      "id": "a1b2c3d4-...",
      "question": "What are the admission requirements for MIS?",
      "answer": null,
      "status": "pending",
      "category": "admission",
      "priority": "MEDIUM",
      "timestamp": "2026-05-02T08:00:00Z"
  }
}
```

---

### GET /id/{ticket_id}

Retrieve a support ticket by ID.

**Example:** `GET /id/a1b2c3d4-e5f6-...`

**Response — ticket found:**
```json
{
  "id": "a1b2c3d4-...",
  "question": "What are the admission requirements for MIS?",
  "answer": null,
  "status": "pending",
  "category": "admission",
  "priority": "MEDIUM",
  "timestamp": "2025-05-02T08:00:00Z"
}
```

**Response — not found:** HTTP 404

---

## Knowledge Base

The knowledge base consists of ~125 files in `knowledge-base/output_for_s3/` uploaded to S3 at deploy time. File types include:

- Processed admissions web pages (Markdown)
- AWS Textract output from scanned PDFs and forms (JSON/Markdown)
- Academic calendars (trimestral and semestral)
- Program-specific admission info (BAMS, MIS, Masters, etc.)
- Application forms and consent documents

**Processing pipeline** (run manually to regenerate the knowledge base):

```bash
# 1. Scrape UPOU admissions pages listed in urls.txt
python knowledge-base/00_admission_url_scraper.py

# 2. Process scanned PDFs and images with AWS Textract
python knowledge-base/03_aws_textractv2.py

# 3. Format raw content into structured admissions Markdown using OpenAI
python knowledge-base/03_kb_generationv2.py
```

---

## DynamoDB Schema

**Table name:** `tickets`
**Primary key:** `id` (String, UUID)

| Attribute | Type | Description |
|---|---|---|
| `id` | String | UUID, primary key |
| `question` | String | User's original query |
| `answer` | String / null | Response when resolved |
| `status` | String | `pending` / `open` / `resolved` / `closed` |
| `category` | String | `admission` / `enrollment` / `finance` / `general` |
| `priority` | String | `HIGH` / `MEDIUM` / `LOW` |
| `timestamp` | String | ISO 8601 UTC |

**Global Secondary Indexes:**
- `category-index` (partition key: `category`)
- `priority-index` (partition key: `priority`)

---

## Lambda Environment Variables

Set automatically by Terraform during deployment:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key (from `terraform.tfvars`) |
| `S3_BUCKET` | Knowledge base bucket name (auto-generated) |
| `DDB_TICKETS_TABLE` | `tickets` |
| `SNS_TOPIC_ARN` | Topic ARN for email notifications |
| `OPENAI_MODEL` | Default: `gpt-4o-mini` |
| `LOG_LEVEL` | Default: `INFO` |

---

## SSL / HTTPS Setup

After deployment, run the SSL setup script **on the EC2 instance** to provision a Let's Encrypt TLS certificate. You need a domain name pointing to the EC2 public IP before running this step.

```bash
# Run the following if host key changed
# ssh-keygen -R <ip_address>

# From your local machine — copy the script to EC2
scp -i vockey.pem infrastructure/setup_ssl.sh ec2-user@<ec2_public_ip_address>:~

# SSH in and run it
ssh -i vockey.pem ec2-user@<ec2_public_ip_address>
bash setup_ssl.sh <domain> <email>
```

The script installs Certbot, provisions the certificate, and configures Nginx for HTTPS with automatic HTTP → HTTPS redirection.

---

## Teardown

To destroy all AWS resources:

```bash
cd infrastructure/terraform/
bash destroy.sh
```

The destroy script empties the S3 knowledge base bucket before running `terraform destroy` to avoid the "bucket not empty" error.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Lambda always returns a fallback ticket | S3 knowledge base is empty or query terms don't match any documents | Verify files were uploaded to S3; check CloudWatch logs |
| API returns HTTP 500 | Missing or invalid `OPENAI_API_KEY`, or OpenAI endpoint unreachable | Check Lambda environment variables and CloudWatch logs |
| `ticket.html` shows a blank page | `localStorage` does not contain the API endpoint | Visit the main helpdesk page first so it can set `localStorage` |
| SNS email notifications not arriving | SNS subscription not confirmed | Click the confirmation link in the subscription email sent to `notification_email` |
| EC2 SSH connection times out | Instance is stopped | Start the instance from the AWS console |
| Terraform lock error | Stale state lock | Run `terraform force-unlock <lock_id>` |
| `terraform destroy` fails with "bucket not empty" | S3 objects not cleaned up | Use `destroy.sh` instead of running `terraform destroy` directly |

---

## Team

| Role                           | Member(s)                           |
| ------------------------------ | ----------------------------------- |
| Project Lead / Integration     | Nicole, Jayvee                      |
| Project Coordinator            | Nicole, Christian                   |
| Knowledge Base Engineering     | Egie, Christian                     |
| Backend Development            | Nicole, John Rey, Jayvee, Kim       |
| AI / RAG Engineering           | Nicole, John Rey                    |
| Frontend Development           | Elvin, Kim, Nicole, John Rey, Rosel |
| Cloud / Infrastructure         | Jayvee, Nicole                      |
| Ticketing & Email Notification | Adrian                              |
