import json
import time

def lambda_handler(event, context):
    time.sleep(1)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Orchestration completed successfully')
    }
