resource "aws_s3_bucket_policy" "bucket_policy" {
  depends_on = [module.bucket-tableau-backup]
  bucket     = module.bucket-tableau-backup.s3_id
  policy     = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "S3:Delete*",
      "Resource": [
        "${module.bucket-tableau-backup.s3_arn}/*",
        "${module.bucket-tableau-backup.s3_arn}"
      ]
    }
  ]
}
POLICY

}

