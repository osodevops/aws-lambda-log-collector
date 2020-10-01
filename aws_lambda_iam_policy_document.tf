data "aws_iam_policy_document" "lambda_config_trust" {
  statement {
    effect = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda_config_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:PutObject",
    ]

    resources = [
      "${module.bucket-tableau-backup.s3_arn}/*",
    ]

  }

  statement {
    effect = "Allow"
    actions   = ["cloudwatch:*"]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions   = ["logs:*"]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    effect = "Allow"
    actions = ["kms:*"]
    resources = ["*"]
  }
}
