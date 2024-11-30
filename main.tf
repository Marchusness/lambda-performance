provider "aws" {
  region = var.aws_region
}

# S3 Bucket
resource "aws_s3_bucket" "data_bucket" {
  bucket = var.bucket_name
}

# IAM Role for Lambda functions
resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda functions
resource "aws_iam_role_policy" "lambda_policy" {
  name = "lambda_execution_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "lambda:InvokeFunction",
          "lambda:InvokeAsync"
        ]
        Resource = "*"
      }
    ]
  })
}

# Orchestrator Lambda
resource "aws_lambda_function" "orchestrator" {
  filename      = "lambda_orchestrator.zip"
  function_name = "orchestrator_lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_orchestrator.lambda_handler"
  runtime       = "python3.8"
  timeout       = 900 # 15 minutes
  memory_size   = 3072
  source_code_hash = filebase64sha256("lambda_orchestrator.zip")

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.data_bucket.id
    }
  }
}

# Downloader Lambda
resource "aws_lambda_function" "downloader" {
  count         = length(var.memory_sizes)
  filename      = "lambda_downloader.zip"
  function_name = "downloader_lambda_${var.memory_sizes[count.index]}mb"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_downloader.lambda_handler"
  runtime       = "python3.8"
  memory_size   = var.memory_sizes[count.index]
  timeout       = 900 # 15 minutes
  source_code_hash = filebase64sha256("lambda_downloader.zip")

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.data_bucket.id
    }
  }
}

# Hello World Lambda
resource "aws_lambda_function" "hello_world" {
  filename      = "hello_world_lambda.zip"
  function_name = "hello_world_lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "hello_world_lambda.lambda_handler"
  runtime       = "python3.8"
  timeout       = 30
  memory_size   = 128
  source_code_hash = filebase64sha256("hello_world_lambda.zip")
}

# Lambda Invoke Orchestrator
resource "aws_lambda_function" "lambda_invoke_orchestrator" {
  filename      = "lambda_invoke_other_lambdas_orchestrator.zip"
  function_name = "lambda_invoke_orchestrator"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_invoke_other_lambdas_orchestrator.lambda_handler"
  runtime       = "python3.9"
  timeout       = 900 # 15 minutes
  memory_size   = 3072 # 3GB for handling multiple concurrent invocations
  source_code_hash = filebase64sha256("lambda_invoke_other_lambdas_orchestrator.zip")

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.data_bucket.id
      HELLO_WORLD_LAMBDA_ARN = aws_lambda_function.hello_world.arn
    }
  }

  depends_on = [aws_lambda_function.hello_world]
}

# Add a Lambda concurrency reservation for the Hello World Lambda
# resource "aws_lambda_function_event_invoke_config" "hello_world_concurrency" {
#   function_name = aws_lambda_function.hello_world.function_name
#   maximum_retry_attempts = 0
# }

# resource "aws_lambda_provisioned_concurrency_config" "hello_world_concurrency" {
#   function_name                     = aws_lambda_function.hello_world.function_name
#   provisioned_concurrent_executions = 800
#   qualifier                        = aws_lambda_function.hello_world.version
# }

