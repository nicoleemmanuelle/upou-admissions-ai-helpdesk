variable "lambda_role" {}

variable "aws_region" {
    default = "us-east-1"
}

variable "openai_api_key" {
  description = "OpenAI API key to use from Lambda environment"
  type        = string
  sensitive   = true
}

variable "OPENAI_MODEL" {
	description = "OpenAI model to use (e.g. gpt-4o-mini)"
	type        = string
	default     = "gpt-4o-mini"
}

variable "create_role" {
	description = "When true Terraform will create an IAM role for Lambda. Set to false to use an existing role ARN provided in lambda_role. Useful for restricted accounts like AWS Academy Learner Lab."
	type        = bool
	default     = true
}
