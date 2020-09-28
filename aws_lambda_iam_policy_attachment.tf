resource "aws_iam_policy_attachment" "log_collector_policy" {
  name       = "${var.environment}-log-collector-attachment"
  roles      = [aws_iam_role.log_collector_lambda.name]
  policy_arn = aws_iam_policy.log_collector_policy.arn
}
