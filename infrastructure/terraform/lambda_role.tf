data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# create_role controls whether Terraform creates the role or you provide an existing one
resource "aws_iam_role" "lambda_role" {
  count              = var.create_role ? 1 : 0
  name               = "upou-helpdesk-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "basic_exec" {
  count      = var.create_role ? 1 : 0
  role       = aws_iam_role.lambda_role[count.index].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "s3_read" {
  count      = var.create_role ? 1 : 0
  role       = aws_iam_role.lambda_role[count.index].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "dynamodb_full" {
  count      = var.create_role ? 1 : 0
  role       = aws_iam_role.lambda_role[count.index].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

/*
Optional: attach SES permissions if you plan to send emails from Lambda
resource "aws_iam_role_policy_attachment" "ses_send" {
  count      = var.create_role ? 1 : 0
  role       = aws_iam_role.lambda_role[count.index].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
}
*/

resource "aws_iam_role_policy" "sns_publish" {
  count = var.create_role ? 1 : 0
  name  = "sns-publish"
  role  = aws_iam_role.lambda_role[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "sns:Publish"
      Resource = aws_sns_topic.helpdesk_notifications.arn
    }]
  })
}
