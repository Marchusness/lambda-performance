```
logger.info(f"Result: {result}")
```

Result:

```
{'ResponseMetadata': {'RequestId': '53e018cf-051a-4193-b5a8-314e170c36c3', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Wed, 04 Dec 2024 23:52:43 GMT', 'content-type': 'application/json', 'content-length': '103', 'connection': 'keep-alive', 'x-amzn-requestid': '53e018cf-051a-4193-b5a8-314e170c36c3', 'x-amzn-remapped-content-length': '0', 'x-amz-executed-version': '$LATEST', 'x-amzn-trace-id': 'Root=1-6750eb4b-235335bc1a1bfcac4eeb4430;Parent=0988e1e6ebd26ab8;Sampled=0;Lineage=1:38a5ab94:0'}, 'RetryAttempts': 0}, 'StatusCode': 200, 'ExecutedVersion': '$LATEST', 'Payload': <StreamingBody at 0x7fa8a4e245c0 for ClientResponseContentProxy at 0x7fa8a4e24580>}
```

The following code gets a payload dict from the result;

```
payload = await result['Payload'].read()
payload_dict = json.loads(payload)
```

the payload dict is the same as the one returned by the hello_world_lambda function:

```
{
    'message': 'Hello from Lambda!',
    'echo': echo,
    'random_data_length': len(random_data) if random_data else 0
}
```
