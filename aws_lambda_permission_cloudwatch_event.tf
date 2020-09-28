resource "aws_lambda_permission" "cloudwatch_event" {
  statement_id  = "AllowExecutionFromCloudWatchEvent"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.log_collector_lambda.lambda_handler
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.timer_alert.arn
}
