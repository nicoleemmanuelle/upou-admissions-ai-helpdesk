## Terraform Infrastructure & Cleanup

This Terraform configuration provisions the full AWS infrastructure for the UPOU Admissions AI Helpdesk, including backend services, API endpoints, and frontend hosting.

### Infrastructure Overview

* **S3 Bucket**

  * Stores knowledge base files (`.md`, `.csv`, `.json`)
  * Hosts Lambda deployment package and frontend build assets

* **Lambda Functions**

  * `upou-helpdesk-lambda` – Handles AI queries using a RAG pipeline
  * `upou-ticket-lookup` – Retrieves ticket data from DynamoDB

* **API Gateway**

  * `/ask` – Accepts user queries
  * `/id/{ticket_id}` – Retrieves ticket information
  * Configured with CORS support

* **DynamoDB**

  * Stores support tickets with UUID as the primary key

* **SNS**

  * Sends email notifications when fallback tickets are created

* **EC2 (Nginx)**

  * Hosts the frontend application
  * Automatically downloads and serves built assets from S3

* **Security Group**

  * Allows HTTP (80), HTTPS (443), and SSH (22)

### Key Features

* Automatically generates a unique S3 bucket name
* Uploads knowledge base, Lambda package, and frontend files to S3
* Uses S3-based Lambda deployment to avoid large direct uploads
* Dynamically configures environment variables
* Fully deployable using `terraform apply`

### Outputs

After deployment, Terraform provides:

* `api_url` – API Gateway endpoint
* `ec2_public_ip` – Public IP of the frontend
* `bucket_name` – S3 bucket name
* `lambda_name` – Lambda function name
* `dynamodb_table_name` – DynamoDB table
* `sns_topic_arn` – SNS topic for notifications

---

## Cleanup Script (`destroy.sh`)

The `destroy.sh` script safely removes all AWS resources created by Terraform.

### Process

1. Retrieves the S3 bucket name from Terraform output
2. Empties the S3 bucket (required before deletion)
3. Executes `terraform destroy` to remove all resources

### Usage

```bash
bash destroy.sh
```

### Notes

* Prevents errors caused by non-empty S3 buckets
* Automates full cleanup without manual steps
* Uses `-auto-approve` for seamless execution
