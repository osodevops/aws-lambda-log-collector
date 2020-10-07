#!/usr/bin/env python
"""
This script will pull all the events (for the specified time period) for all the log groups and their respective log streams from cloudwatch logs 
and upload them to an s3 bucket.
"""
import boto3, json, time, logging, os, gzip
from datetime import date, datetime, timedelta
from botocore.exceptions import ClientError

# EXPORT S3_BUCKET_NAME="cloudwatch-compressed-logs-eu-west-2-637085696726"
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
    passnumber = 1

    # grab region parameter from our event
    aws_region = event['region']
    # initialize a logstream object array - this is a list of all log groups (objects) in the account
    log_group_object_array = []
    # initialize a log group list array - this is the list of log groups that will eventually get processed
    log_group_array = []

    # init boto3
    client = boto3.client('logs', region_name=aws_region)
    response = client.describe_log_groups()

    # get the output of LogGroups api call, "stream" it into an array of objects and then loop through the array to create a list array of logGroupNames 
    log_group_stream = client.describe_log_groups() #logGroupName=log_group_name, descending=True, limit=50, orderBy='LastEventTime')
    log_group_object_array += log_group_stream['logGroups']
    log_group_name_dict = [stream_lg['logGroupName'] for stream_lg in log_group_object_array]

    # LogGroups API call will only return max 50 results so we need to handle situations where the number of logGroups is greater than 50
    while 'nextToken' in log_group_stream:
        log_group_stream = client.describe_log_groups(nextToken=log_group_stream['nextToken'])
        log_group_object_array += log_group_stream['logGroups']
    log_group_name_dict = [stream_lg['logGroupName'] for stream_lg in log_group_object_array]

    # If there are logs from many log groups we want to ensure that we stay within lambda execution time limits.
    # That is why we will first check that we don't waste time processing log groups which have no new entries.
    # Log group will be processed further if it has at least one new event.
    print('------------- Lambda log-collector --------------')
    print('Preprosessing log groups:')
    h = 1
    for i in log_group_name_dict:
        one_log_stream_object = []
        print(str(h) + ' ' + i)
        # get the output of DescribeLogStreams API. Get only the logStream with latest entry, "stream" it into an object
        one_log_stream = client.describe_log_streams(logGroupName=i, descending=True, limit=1, orderBy='LastEventTime')
        one_log_stream_object += one_log_stream['logStreams']
        # a log group may exist without any log streams. Make sure a log stream exists. After that loop through the object to get the logStreamName 
        if one_log_stream_object != []:
            one_log_stream_name = [stream_ls['logStreamName'] for stream_ls in one_log_stream_object]
            # With the logGroupName and the logStreamName verify that there are log entries for the period. If there are then add the logGroup to the log_group_array
            log_entries = client.get_log_events(logGroupName=str(i), logStreamName=one_log_stream_name[0], startTime=ts, endTime=te)
            if log_entries['events'] != []:
                log_group_array.append(i)
        h = h + 1

    # Preprocessing finished
    print('\n' + 'Log groups which have new entries are: ')
    for n in log_group_array:
        print(n)
    # print(log_group_array)
    print('Total ' + str(len(log_group_array)))
    # With the final list array (log_group_array) we start the process of gathering log events
    for e in log_group_array:
        log_collector(str(e), str(aws_region), str(s3_bucket_name), int(passnumber))
        passnumber = passnumber + 1
        time.sleep(2)
    print('Finished processing')

def log_collector(logGroupName, awsRegion, s3BucketName, passNumber):
    log_group_name = logGroupName
    aws_region = awsRegion
    s3_bucket_name = s3BucketName
    lgnumber = passNumber
    # the name of the s3 object will be transformed to a string not containing forward slashes and not starting with a dash
    folder_name = logGroupName.replace("/","-")
    if folder_name.startswith('-'):
        folder_name = folder_name[1:]
    file_name = logGroupName.replace("/","-") + '-' + timestring + '.gz'
    if file_name.startswith('-'):
        file_name = file_name[1:]
    # init boto3 for s3
    s3 = boto3.resource('s3')
    client = boto3.client('logs', region_name=aws_region)
    print('\nFor LogGroup ' + str(lgnumber) + ' ' + logGroupName)
    print('Events between: ' + str(ts) + ' and ' + str(te))
    print('------------- LogStreamName -------------- : # events')
    all_streams = []
    stream_batch = client.describe_log_streams(logGroupName=log_group_name, descending=True, limit=50, orderBy='LastEventTime')
    all_streams += stream_batch['logStreams']
    stream_names = [stream['logStreamName'] for stream in all_streams]

    # LogStreams API call will only return max 50 results at a time so we need to handle situations where the number is greater.
    # But since a single log group can, over the years, accumulate tens of thousands of log streams and since we don't want to
    # fetch all these old log groups we set the upper limit with (k). Upper limit amounts to 50*(k)=250 in this case.
    k = 0
    while 'nextToken' in stream_batch and k < 5:
        stream_batch = client.describe_log_streams(logGroupName=log_group_name, descending=True, limit=50, orderBy='LastEventTime', nextToken=stream_batch['nextToken'])
        all_streams += stream_batch['logStreams']
        k = k + 1
    stream_names = [stream['logStreamName'] for stream in all_streams]
    # print(len(all_streams))
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
# lambda_handler({'region': 'eu-west-2', 'account': '637085696726'}, {'context'})
