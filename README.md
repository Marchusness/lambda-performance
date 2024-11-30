# Results

## lambda_invoke_other_lambdas

This test compares the performance of invoking 390 other lambdas in parallel using asyncio, threadpool, and a hybrid approach.

Files used:

- hello_world_lambda.py
- lambda_invoke_other_lambdas_orchestrator.py

The asyncio approach of invoking the lambdas is 50% faster than the threadpool approach. Note that the hello world lambda waits for 1 seconds before returning. Thus, 1 seconds should be subtracted from the total times to have a better comparison of invoker performance. Taking into account the 1 second wait time, the asyncio approach takes 1.3898900508880616 seconds and the threadpool approach takes 2.87318811416626 seconds, showing a 50% performance increase for the asyncio approach.

The asyncio_time and hybrid_time produce similar results but the hybrid approach is more complex to implement and doesn't have the as_completed function that both asyncio and threadpool have.

Results are averaged over 10 runs.

Results with a 50kb payload:

```
{
  "asyncio_time": 2.3898900508880616,
  "threadpool_time": 3.87318811416626,
  "hybrid_time": 2.3548757076263427
}
```

Results with a 1kb payload:

```
{
  "asyncio_time": 2.2028354167938233,
  "threadpool_time": 3.7333420276641847,
  "hybrid_time": 2.238196587562561
}
```

## S3 Download Times

This test compares the performance of downloading 20 500mb files from S3 from a lambda function with different memory sizes ([1024, 2048, 3072, 4096, 6144, 10240]).

Files used:

- lambda_downloader.py
- lambda_orchestrator.py

Results are averaged over 100 runs.

download_time is the time taken to list the files and download all of them.
total_time is the time taken for the lambda function (which downloads the files) to run.

```

[
{
"memory_size": 1024,
"download_time": 0.46986615896224976,
"total_time": 0.49315175533294675
},
{
"memory_size": 2048,
"download_time": 0.2622713804244995,
"total_time": 0.28418920040130613
},
{
"memory_size": 3072,
"download_time": 0.2116856598854065,
"total_time": 0.23385329008102418
},
{
"memory_size": 4096,
"download_time": 0.1946907162666321,
"total_time": 0.21736995935440062
},
{
"memory_size": 6144,
"download_time": 0.18896052598953247,
"total_time": 0.21148773908615112
},
{
"memory_size": 10240,
"download_time": 0.1608742094039917,
"total_time": 0.18336345434188842
}
]

```
