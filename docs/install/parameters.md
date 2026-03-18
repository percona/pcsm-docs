# Percona ClusterSync for MongoDB startup configuration

When [starting the `pcsm` process](start-pcsm.md), you can use the following options:

- `--port`: The port on which the server will listen (default: 2242)
- `--source`: The MongoDB connection string for the source cluster
- `--target`: The MongoDB connection string for the target cluster
- `--log-level`: The log level (default: "info")
- `--log-json`: Output log in JSON format with disabled color
- `--no-color`: Disable log ASCI color


??? example "Example"

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
| `PCSM_REPL_NUM_WORKERS` | Controls how many concurrent replication worker goroutines PCSM uses to apply DML (insert/update/replace/delete) events to the target cluster. |`runtime.NumCPU()`|
| `PCSM_REPL_CHANGE_STREAM_BATCH_SIZE` | Sets the maximum number of change stream events PCSM will request and read from MongoDB per batch while streaming changes from the source cluster. |`10000`|
| `PCSM_REPL_EVENT_QUEUE_SIZE` | Controls the size of the internal event queue used by the replication subsystem. |`5000`|
| `PCSM_REPL_WORKER_QUEUE_SIZE` | Defines the maximum number of replication events that each replication worker thread can queue before processing. |`5000`|
| `PCSM_REPL_BULK_OPS_SIZE` | Defines the maximum number of operations that can be grouped together into a single bulk apply batch during replication. |`5000`|
