import boto3
import json
import os
import time
import asyncio
import aioboto3
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import math
import logging
from botocore.config import Config

def generate_random_payload(kb: int) -> str:
    random_data = os.urandom(math.floor(kb * 1024)).hex()
    return json.dumps({'random_data': random_data})

GLOBAL_PAYLOAD = generate_random_payload(kb=0.5)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BUCKET_NAME = os.environ['BUCKET_NAME']
HELLO_WORLD_LAMBDA_ARN = os.environ['HELLO_WORLD_LAMBDA_ARN']
INVOCATION_COUNT = 800

# Configure boto3 client with increased max connections
boto3_config = Config(
    max_pool_connections=INVOCATION_COUNT,
    retries={'max_attempts': 0}  # Disable retries to avoid throttling
)

s3 = boto3.client('s3')
lambda_client = boto3.client('lambda', config=boto3_config)


"""
Invokes multiple lambdas using asyncio
"""
async def invoke_lambdas_async(session, lambda_arn: str, count: int) -> List[Dict]:
    """Invokes multiple lambdas using asyncio"""
    
    async with session.client('lambda', config=boto3_config) as lambda_client:
        tasks = [
            asyncio.create_task(
                lambda_client.invoke(
                    FunctionName=lambda_arn,
                    InvocationType='RequestResponse',
                    Payload=GLOBAL_PAYLOAD
                )
            )
            for _ in range(count)
        ]
        
        results = []
        for completed_task in asyncio.as_completed(tasks):
            try:
                result = await completed_task
                results.append(result)
            except Exception as e:
                logging.error(f"Task failed with error: {str(e)}")
                results.append({"error": str(e)})
        
        return results

async def parallel_invoke_asyncio() -> float:
    session = aioboto3.Session()
    await invoke_lambdas_async(session, HELLO_WORLD_LAMBDA_ARN, INVOCATION_COUNT)








"""
Uses ThreadPoolExecutor to invoke lambdas in parallel
"""
def invoke_single_lambda(lambda_arn: str) -> Dict:
    return lambda_client.invoke(
        FunctionName=lambda_arn,
        InvocationType='RequestResponse',
        Payload=GLOBAL_PAYLOAD
    )

def parallel_invoke_threadpool() -> float:
    with ThreadPoolExecutor(max_workers=INVOCATION_COUNT) as executor:
        futures = [
            executor.submit(invoke_single_lambda, HELLO_WORLD_LAMBDA_ARN)
            for _ in range(INVOCATION_COUNT)
        ]
        for future in as_completed(futures):
            future.result()








"""
Hybrid approach using ThreadPoolExecutor with asyncio
"""
async def run_async_batch_coroutine(batch_size: int) -> float:
    session = aioboto3.Session()
    return await invoke_lambdas_async(session, HELLO_WORLD_LAMBDA_ARN, batch_size)

def run_async_batch(batch_size: int) -> float:
    return asyncio.run(run_async_batch_coroutine(batch_size))

def parallel_invoke_hybrid(num_threads: int = 2) -> float:
    batch_size = math.ceil(INVOCATION_COUNT / num_threads)
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(run_async_batch, batch_size)
            for _ in range(num_threads)
        ]
        for future in as_completed(futures):
            future.result()

def lambda_invoke_timer(func):
    total_time = 0
    reruns = 10

    for _ in range(reruns):
        start_time = time.time()
        result = func()
        end_time = time.time()
        logger.info(f"Function '{func.__name__}' executed in {end_time - start_time:.4f} seconds")
        total_time += end_time - start_time
    return total_time / reruns

def async_timer_wrapper():
    return asyncio.run(parallel_invoke_asyncio())







"""
Orchestrator Lambda Handler that invokes the the other lambdas and saves the results to S3
"""
def lambda_handler(event, context):
    results = {
        'asyncio_time': lambda_invoke_timer(async_timer_wrapper),
        'threadpool_time': lambda_invoke_timer(parallel_invoke_threadpool),
        'hybrid_time': lambda_invoke_timer(parallel_invoke_hybrid),
    }
    
    # Save results to S3
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key='lambda_invoke_other_lambdas_orchestrator_results.json',
        Body=json.dumps(results, indent=2)
    )
    
    return {
        'statusCode': 200,
        'body': 'Orchestration completed successfully',
        'results': json.dumps(results, indent=2)
    }
