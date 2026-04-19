provider "aws" {
  region = var.aws_region
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "kb_bucket" {
  bucket = "upou-kb-${random_id.suffix.hex}"

  tags = {
    Name        = "UPOU KB Bucket"
    Environment = "dev"
  }
}

resource "aws_s3_object" "kb_files" {
  for_each = fileset("../../knowledge-base/output_for_s3", "*.{csv,md}")

  bucket = aws_s3_bucket.kb_bucket.id
  key    = each.value
  source = "../../knowledge-base/output_for_s3/${each.value}"

  etag = filemd5("../../knowledge-base/output_for_s3/${each.value}")
}

# Upload the local lambda.zip into the knowledge-bucket so Terraform can
# point Lambda to an S3 object instead of doing a direct large upload.
resource "aws_s3_object" "lambda_zip" {
  bucket = aws_s3_bucket.kb_bucket.bucket
  key    = "lambda/lambda.zip"
  # Upload the file that lives in this Terraform module directory.
  source = "../../backend/lambda/lambda.zip"

  # Use an etag so Terraform updates the object when the file changes.
  etag = filemd5("../../backend/lambda/lambda.zip")

  # Keep the object public ACL off (default). Adjust server-side encryption
  # or ACLs here if required by your org.
}

# Lambda Function
resource "aws_lambda_function" "upou_ai" {
  function_name = "upou-helpdesk-lambda"
  # If Terraform created the role (var.create_role = true) use its ARN,
  # otherwise use the existing role ARN supplied in var.lambda_role.
  # element(concat(...), 0) returns the created role ARN when present,
  # or falls back to var.lambda_role when the list is empty.
  role = element(concat(aws_iam_role.lambda_role.*.arn, [var.lambda_role]), 0)
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"

  # Increase timeout so external requests (S3, OpenAI) have time to complete.
  timeout       = 15
  memory_size   = 256

  # Use S3 deployment to avoid large direct uploads from the CLI. Terraform
  # will upload the local file via aws_s3_bucket_object.lambda_zip and then
  # reference it here.
  s3_bucket = aws_s3_bucket.kb_bucket.bucket
  s3_key    = aws_s3_object.lambda_zip.key
  depends_on = [aws_s3_object.lambda_zip]
  
  environment {
    variables = {
      OPENAI_API_KEY     = "${var.OPENAI_API_KEY}"
      S3_BUCKET          = "${aws_s3_bucket.kb_bucket.bucket}"
      DDB_TICKETS_TABLE  = "${aws_dynamodb_table.tickets.name}"
      OPENAI_MODEL       = "${var.OPENAI_MODEL}"
      LOG_LEVEL          = "INFO"
    }
  }
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

  tags = {
    Name        = "UPOU Ticket Table"
    Environment = "dev"
  }
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "upou_api" {
  name = "upou-api"
}

# Resource (/ask)
resource "aws_api_gateway_resource" "ask" {
  rest_api_id = aws_api_gateway_rest_api.upou_api.id
  parent_id   = aws_api_gateway_rest_api.upou_api.root_resource_id
  path_part   = "ask"
}

# Method (POST)
resource "aws_api_gateway_method" "post_method" {
  rest_api_id   = aws_api_gateway_rest_api.upou_api.id
  resource_id   = aws_api_gateway_resource.ask.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integration with Lambda
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.upou_api.id
  resource_id = aws_api_gateway_resource.ask.id
  http_method = aws_api_gateway_method.post_method.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.upou_ai.invoke_arn
}

# Allow API Gateway to invoke Lambda
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.upou_ai.function_name
  principal     = "apigateway.amazonaws.com"
}

# Deploy API
resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [aws_api_gateway_integration.lambda_integration]

  rest_api_id = aws_api_gateway_rest_api.upou_api.id
  stage_name  = "dev"
}

output "api_url" {
  value = "https://${aws_api_gateway_rest_api.upou_api.id}.execute-api.${var.aws_region}.amazonaws.com/dev/ask"
}

output "bucket_name" {
  value = aws_s3_bucket.kb_bucket.id
}

output "lambda_name" {
  value = aws_lambda_function.upou_ai.function_name
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.tickets.name
}

# Get a recent Ubuntu AMI (safe default)
data "aws_ami" "ubuntu" {
  most_recent = true

  owners = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security group (HTTP + SSH)
resource "aws_security_group" "ec2_sg" {
  name        = "upou-ec2-sg-${random_id.suffix.hex}"
  description = "Allow HTTP and SSH"

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "UPOU EC2 SG"
    Environment = "dev"
  }
}

# EC2 instance
resource "aws_instance" "frontend" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.ec2_sg.id]

  associate_public_ip_address = true

  tags = {
    Name        = "UPOU Frontend EC2"
    Environment = "dev"
  }
}

# Output public IP
output "ec2_public_ip" {
  value = aws_instance.frontend.public_ip
}
