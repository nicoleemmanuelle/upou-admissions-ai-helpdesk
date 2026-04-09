provider "aws" {
  region = "ap-southeast-1"
}

# S3 Bucket
resource "aws_s3_bucket" "kb" {
  bucket = "upou-admissions-kb"
}

# EC2 Instance
resource "aws_instance" "web" {
  ami           = var.ami
  instance_type = "t2.micro"

  tags = {
    Name = "IS215-Project"
  }
}

# Lambda Function
resource "aws_lambda_function" "backend" {
  function_name = "upou-helpdesk-lambda"
  role          = var.lambda_role
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"

  filename = "lambda.zip"
}

# DynamoDB
resource "aws_dynamodb_table" "tickets" {
  name         = "tickets"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}