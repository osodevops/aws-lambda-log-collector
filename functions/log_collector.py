#!/usr/bin/env python
"""
This script will pull all the events (for the specified time period) for all the log groups and their respective log streams from cloudwatch logs 
and upload them to an s3 bucket.
"""
import boto3, json, time, logging, os, gzip
from datetime import date, datetime, timedelta
from botocore.exceptions import ClientError

s3_bucket_name = os.environ['S3_BUCKET_NAME']
start_number_of_days= 1
end_number_of_days= 0
#############################
timestring = datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%Hh%Mm%Ss')
ts=(int((datetime.today() - timedelta(hours=24 * start_number_of_days)).timestamp())) * 1000
te=(int((datetime.today() - timedelta(hours=24 * end_number_of_days)).timestamp())) * 1000

# logging init
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event,context):
    data = json.dumps(event)
    logger.info('Starting log collection based on this event:')
    logger.info(data)

    # grab parameters from our event
    aws_region = event['region']

    # init boto3
    client = boto3.client('logs', region_name=aws_region)
    response = client.describe_log_groups()
    for i in response['logGroups']:
        log_collector(str(i['logGroupName']), str(aws_region), str(s3_bucket_name))
        time.sleep(15)


def log_collector(logGroupName, awsRegion, s3BucketName):
    log_group_name = logGroupName
    aws_region = awsRegion
    s3_bucket_name = s3BucketName
    folder_name = logGroupName.replace("/","-")
    if folder_name.startswith('-'):
        folder_name = folder_name[1:]
    file_name = logGroupName.replace("/","-") + '-' + timestring + '.gz'
    if file_name.startswith('-'):
        file_name = file_name[1:]
    # init boto3
    client = boto3.client('logs', region_name=aws_region)
    print('For LogGroup ' + logGroupName)
    print('Events between: ' + str(ts) + ' and ' + str(te))
    print('------------- LogStreamName -------------- : # events')
    all_streams = []
    stream_batch = client.describe_log_streams(logGroupName=log_group_name)
    all_streams += stream_batch['logStreams']

    while 'nextToken' in stream_batch:
        stream_batch = client.describe_log_streams(logGroupName=log_group_name, nextToken=stream_batch['nextToken'])
        all_streams += stream_batch['logStreams']
    stream_names = [stream['logStreamName'] for stream in all_streams]
    
    out_file = []
    for stream in stream_names:
        logs_batch = client.get_log_events(logGroupName=log_group_name, logStreamName=stream, startTime=ts, endTime=te)
        for event in logs_batch['events']:
            event.update({'group': log_group_name, 'stream': stream})
            out_file.append(json.dumps(event))
        print(stream, ":", len(logs_batch['events']))
        while 'nextToken' in logs_batch:
            logs_batch = client.get_log_events(logGroupName=log_group_name, logStreamName=stream, startTime=ts, endTime=te,
                                               nextToken=logs_batch['nextToken'])
            for event in logs_batch['events']:
                event.update({'group': log_group_name, 'stream': stream})
                out_file.append(json.dumps(event))
    
    print('-------------------------------------------\nTotal number of events: ' + str(len(out_file)))
    print(file_name)
    s3 = boto3.resource('s3')
    json_str = json.dumps(out_file)
    json_bytes = json_str.encode('utf-8')
    gzip_object = gzip.compress(json_bytes)
    s3object = s3.Object(s3_bucket_name, folder_name + '/' + file_name)
    print('Starting the upload of file ' + file_name + ' to s3 bucket ' + s3_bucket_name)
    try:
        s3object.put(Body=gzip_object)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchUpload':
            print("Upload Failed")
    else:
        print("Log file uploaded to s3\n")

### Local test event
# lambda_handler({'region': 'eu-west-2', 'account': '111222333444'}, {'context'})