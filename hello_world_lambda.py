import json
import time

def lambda_handler(event, context):
    print(f"Event: {event}")

    # Get echo value from event directly since we're not using API Gateway
    echo = event.get('echo')  # Use get() to avoid KeyError
    random_data = event.get('random_data')
    
    return {
        'message': 'Hello from Lambda!',
        'echo': echo,
        'random_data_length': len(random_data) if random_data else 0
    }
