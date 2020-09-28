resource "aws_iam_role" "log_collector_lambda" {
  name               = "${var.environment}-LOG-COLLECTOR-LAMBDA-ROLE"
  description        = "Allows Lambda function to execute log collection."
  assume_role_policy = data.aws_iam_policy_document.lambda_config_trust.json
}
