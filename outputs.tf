output "s3_bucket_name" {
  value = aws_s3_bucket.data_bucket.id
}

output "orchestrator_lambda_arn" {
  value = aws_lambda_function.orchestrator.arn
}

output "downloader_lambda_arns" {
  value = aws_lambda_function.downloader[*].arn
}
