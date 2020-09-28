data "null_data_source" "lambda_file" {
  inputs = {
    filename = substr("${path.module}/functions/log_collector.py", length(path.cwd) + 1, -1)
  }
}
