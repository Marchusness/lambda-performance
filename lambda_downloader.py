import boto3
import os
import time
import threading

s3 = boto3.client('s3')
transfer = boto3.s3.transfer.S3Transfer(s3)

BUCKET_NAME = os.environ['BUCKET_NAME']

def download_file(key):
    s3.get_object(Bucket=BUCKET_NAME, Key=key)

def lambda_handler(event, context):
    start_time = time.time()
    
    # Download all files from S3 using multithreading
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    threads = []
    for obj in response['Contents']:
        if obj['Key'].startswith('file_'):
            thread = threading.Thread(target=download_file, args=(obj['Key'],))
            threads.append(thread)
            thread.start()
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    download_time = end_time - start_time
    
    return {
        'statusCode': 200,
        'body': 'Download completed',
        'download_time': download_time
    }
