# Percona ClusterSync for MongoDB startup configuration

When [starting the `pcsm` process](start-pcsm.md), you can use the following options:

- `--port`: The port on which the server will listen (default: 2242)
- `--source`: The MongoDB connection string for the source cluster
- `--target`: The MongoDB connection string for the target cluster
- `--log-level`: The log level (default: "info")
- `--log-json`: Output log in JSON format with disabled color
- `--no-color`: Disable log ANSI color
- `--mongodb-operation-timeout`: Timeout for MongoDB operations (default: 5m)
- `--clone-num-parallel-collections`: Number of collections cloned in parallel during clone.
- `--clone-num-read-workers`: Number of read workers that read collection segments from the source. Shared for all collections.
<<<<<<< Updated upstream
- `--clone-num-insert-workers`: Number of write workers that write batches to the target. Shared for all collections.
- `--clone-segment-size`: Clone segment size
- `--clone-read-batch-size`: Read cursor batch size
- `--use-collection-bulk-write`: Forces collection-level bulk write instead of the newer client-level bulk write (MongoDB 8.0+).
=======
- `--clone-num-insert-workers`: Number of insert workers that write batches to the target. Shared for all collections.

>>>>>>> Stashed changes


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
| `PCSM_CLONE_NUM_INSERT_WORKERS` | Number of insert workers for cloning | `NumCPU * 2` |
<<<<<<< Updated upstream
| `PCSM_CLONE_SEGMENT_SIZE` | Clone segment size | - |
| `PCSM_CLONE_READ_BATCH_SIZE` | Read cursor batch size | - |
| `PCSM_MONGODB_OPERATION_TIMEOUT` | Maximum time to wait before timing out MongoDB client operations such as insert, update, delete. If the timeout is reached, the operation will fail. Previously named `PCSM_MONGODB_CLI_OPERATION_TIMEOUT`; the old name may still be accepted for backward compatibility but is deprecated. | `5m` |
| `PCSM_LOG_LEVEL` | Log level used for output (e.g., debug, info, warn, error). Controls the verbosity of logs. | `info` |
=======
| `PCSM_MONGODB_OPERATION_TIMEOUT` | Maximum time to wait before timing out MongoDB client operations such as insert, update, delete. If the timeout is reached, the operation will fail.| `5m`|
| `PCSM_LOG_LEVEL` |Log level used for output (e.g., debug, info, warn, error). Controls the verbosity of logs. | `info` |
>>>>>>> Stashed changes
| `PCSM_LOG_JSON` | Output logs in JSON format. When enabled, log coloring is automatically disabled. | `false` |
| `PCSM_LOG_NO_COLOR` | Disable ANSI color codes in log output (useful for non-interactive terminals and log aggregation systems). | `false` |
| `PCSM_USE_COLLECTION_BULK_WRITE` | Forces collection-level bulk write instead of the newer client-level bulk write (MongoDB 8.0+). | `false` |


