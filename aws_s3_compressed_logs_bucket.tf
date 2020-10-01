module "bucket-tableau-backup" {
//  source                  = "git::ssh://git@github.com/osodevops/aws-terraform-module-s3.git"
  source                  = "../../aws-terraform-module-s3"
  s3_bucket_name          = local.compressed_logs_bucket_name
  s3_bucket_force_destroy = false
  s3_bucket_policy        = ""
  common_tags             = var.common_tags

  # Bucket public access
  restrict_public_buckets = true
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true

  versioning = {
    enabled = false
  }
}