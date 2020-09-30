resource "aws_s3_bucket" "compressed_logs" {
  bucket        = local.compressed_logs_bucket_name
  acl           = "log-delivery-write"
  force_destroy = false

  versioning {
    enabled = false
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = var.s3_sse_algorithm
      }
    }
  }

  #lifecycle rules for non-current versions (defaults to on)
  lifecycle_rule {
    enabled = true
    id      = "default"

    abort_incomplete_multipart_upload_days = 14

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 60
      storage_class = "GLACIER"
    }

    noncurrent_version_transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    noncurrent_version_transition {
      days          = 60
      storage_class = "GLACIER"
    }

    expiration {
      expired_object_delete_marker = false
      days                         = 90
    }
  }

  tags = merge(
    var.common_tags,
    {
      "Name" = local.compressed_logs_bucket_name
    },
  )
}