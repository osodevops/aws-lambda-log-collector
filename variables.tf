variable "environment" {
  description = "Set the environment from where the logs are collected."
  type = string
}

variable "s3_bucket_name" {
  description = "Set the s3 bucket to which to store the logs."
  default = "Default"
  type = string
}

variable "common_tags" {
  type = map
}

variable "s3_sse_algorithm" {
  default = "aws:kms"
}

locals {
  compressed_logs_bucket_name = "cloudwatch-compressed-logs-${data.aws_region.current.name}-${data.aws_caller_identity.current.account_id}"
}