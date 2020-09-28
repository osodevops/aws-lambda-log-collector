resource "aws_cloudwatch_event_rule" "timer_alert" {
  name = "${upper(var.environment)}-LOG-COLLECTOR-TIMER-ALERT"
  description = "Send alerts to start log collection."
  schedule_expression = "cron(0 15 2 * * ? *)"
}

resource "aws_cloudwatch_event_target" "lambda_alert" {
  rule      = aws_cloudwatch_event_rule.timer_alert.name
  target_id = "log-collector-lambda"
  arn       = aws_lambda_function.log_collector_lambda.arn
}

