# Percona ClusterSync for MongoDB startup configuration

When [starting the `pcsm` process](start-pcsm.md), you can use the following options:

- `--port`: The port on which the server will listen (default: 2242)
- `--source`: The MongoDB connection string for the source cluster
- `--target`: The MongoDB connection string for the target cluster
- `--log-level`: The log level (default: "info")
- `--log-json`: Output log in JSON format with disabled color
- `--no-color`: Disable log ASCI color

Example:

```{.bash data-prompt="$"}
$ pcsm \
    --source <source-mongodb-uri> \
    --target <target-mongodb-uri> \
    --port 2242 \
    --log-level debug \
    --log-json
```

## Environment variables

Alternatively, you can define the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PCSM_SOURCE_URI` | MongoDB connection string for the source cluster | - |
| `PCSM_TARGET_URI` | MongoDB connection string for the target cluster | - |
| `PCSM_PORT` | Server port number | `2242` |
| `PCSM_CLONE_NUM_PARALLEL_COLLECTIONS` | Number of collections cloned in parallel | `2` |
| `PCSM_CLONE_NUM_READ_WORKERS` | Number of read workers for cloning | `NumCPU / 4` |
| `PCSM_CLONE_NUM_INSERT_WORKERS` | Number of insert workers for cloning | `NumCPU * 4` |
| `PCSM_MONGODB_CLI_OPERATION_TIMEOUT` | Maximum time to wait before timing out MongoDB client operations such as insert, update, delete. If the timeout is reached, the operation will fail.  | `5m` |
| `PCSM_REPL_WORKER_FLUSH_INTERVAL` | Maximum time between bulk write flushes to the target. Lower values reduce lag and higher values batch more ops per write. | `1s` |
| `PCSM_REPL_WORKER_BULK_QUEUE_SIZE` | Number of pending bulk batches per worker while a write is in progress. Higher values can improve throughput at the cost of increased memory usage. | `3` |
| `PCSM_SOURCE_CLIENT_COMPRESSORS` | Allows you to specify which compression algorithms the source client should use when reading events/documents. Useful because throughput can vary dramatically depending on how compressible the source data is.| `snappy,zstd,zlib` |
| `PCSM_TARGET_CLIENT_COMPRESSORS` | Allows you to control compression on the target side as well.| `snappy,zstd,zlib` |
