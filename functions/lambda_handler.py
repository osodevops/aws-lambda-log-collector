#!/usr/bin/env python
"""
This script will pull all the events (for the specified time period) for all the log groups and their respective log streams from cloudwatch logs 
and upload them to an s3 bucket.
"""
import boto3, json, time, logging
from datetime import date, datetime, timedelta
from botocore.exceptions import ClientError
from main.log_collector import log_collector

s3_bucket_name = os.environ['S3_BUCKET_NAME']
# logging init
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event,context):
    data = json.dumps(event)
    logger.info('Starting log collection based on this event:')
    logger.info(data)

    # grab parameters from our event
    resource_id = event['resources'][0]
    aws_region = event['region']
    log_group_list = []

    # init boto3
    boto3.session.Session(profile_name="default")
    client = boto3.client('logs', region_name=aws_region)
    s3 = boto3.resource('s3')

    response = client.describe_log_groups()
    for i in response['logGroups']:
        log_collector(i['logGroupName'], aws_region, s3_bucket_name)
        time.sleep(15)

