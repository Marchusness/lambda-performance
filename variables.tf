variable "aws_region" {
  description = "AWS region to deploy resources"
  default     = "us-west-2"
}

variable "bucket_name" {
  description = "Name of the S3 bucket"
  default     = "lambda-performance-test-bucket"
}

variable "memory_sizes" {
  description = "List of memory sizes for downloader Lambdas"
  type        = list(number)
  default     = [1024, 2048, 3072, 4096, 6144, 10240]
}
