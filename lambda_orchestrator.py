import boto3
import json
import os
import random
import string
import time

s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')

BUCKET_NAME = os.environ['BUCKET_NAME']
FILE_SIZE = 1024 * 1024 * 512  # 0.5 GB
NUM_FILES = 20
TOTAL_SIZE = FILE_SIZE * NUM_FILES

LAMBDA_MEMORY_SIZES = [1024, 2048, 3072, 4096, 6144, 10240]

def generate_random_data(size):
    return os.urandom(size)
import logging

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Generate and upload random data
    logger.info("Starting to generate and upload random data")
    # for i in range(NUM_FILES):
    #     data = generate_random_data(FILE_SIZE)
    #     s3.put_object(Bucket=BUCKET_NAME, Key=f'file_{i}.txt', Body=data)
    #     logger.info(f"Uploaded file_{i}.txt")
    
    logger.info(f"Uploaded {NUM_FILES} files of {FILE_SIZE / (1024 * 1024 * 1024):.2f} GB each")

    # Invoke downloader Lambdas
    logger.info("Starting to invoke downloader Lambdas")
    results = []
    for memory in LAMBDA_MEMORY_SIZES:
        total_download_time = 0
        total_time = 0
        for i in range(100):
            function_name = f"downloader_lambda_{memory}mb"
            start_time = time.time()
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse'
            )
            end_time = time.time()
            
            payload = json.loads(response['Payload'].read())
            download_time = payload['download_time']
            
            total_download_time += download_time
            total_time += end_time - start_time
            logger.info(f"Invoked {function_name} with memory size {memory}MB")
        
        results.append({
            'memory_size': memory,
            'download_time': total_download_time / 100,
            'total_time': total_time / 100
        })
    
    # Save results to S3
    logger.info("Saving results to S3")
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key='results.json',
        Body=json.dumps(results, indent=2)
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Orchestration completed successfully')
    }
