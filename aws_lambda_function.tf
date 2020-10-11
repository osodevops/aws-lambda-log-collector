resource "aws_lambda_function" "log_collector_lambda" {
  filename         = data.archive_file.log_collector.output_path
  description      = "Collects logs and stores them in s3."
  function_name    = "${upper(var.environment)}-LOG-COLLECTOR-FUNCTION"
  role             = aws_iam_role.log_collector_lambda.arn
  handler          = "log_collector.lambda_handler"
  runtime          = "python3.6"
  memory_size      = 640
  timeout          = 900
  source_code_hash = data.archive_file.log_collector.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_NAME = var.s3_bucket_name
    }
  }

  tags = merge(
    var.common_tags,
    {
    "Name" = "${var.environment}-LOG-COLLECTOR-LAMBDA"
    },
  )
}
