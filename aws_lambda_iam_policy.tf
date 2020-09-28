resource "aws_iam_policy" "log_collector_policy" {
  name        = "${upper(var.environment)}-LOG-COLLECTOR-LAMBDA-POLICY"
  path        = "/"
  description = "Log collector Lambda function policy to access CloudWatch, s3 and KMS"

  policy = data.aws_iam_policy_document.lambda_config_policy.json
}
