import json
import time

def lambda_handler(event, context):
    time.sleep(1)
    
    return {
        'body': 'Hello, World!'
    }
