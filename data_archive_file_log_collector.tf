data "archive_file" "log_collector" {
  type        = "zip"
  source_file = "${path.module}/functions/log_collector.py"
  output_path = data.null_data_source.lambda_archive.outputs.filename
}
