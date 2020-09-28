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