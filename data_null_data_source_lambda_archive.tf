data "null_data_source" "lambda_archive" {
  inputs = {
    filename = "${path.module}/functions/log_collector.zip"
  }
}
