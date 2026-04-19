variable "lambda_role" {}

variable "aws_region" {
    default = "us-east-1"
}

variable "OPENAI_API_KEY" {
	description = "OpenAI API key to use from Lambda environment"
	type        = string
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