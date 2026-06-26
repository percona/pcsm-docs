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
- `--clone-num-insert-workers`: Number of insert workers that write batches to the target. Shared for all collections.
- `--clone-segment-size`: Segment size for clone operations. Accepts plain bytes or a unit suffix (e.g. `500MB`, `1GiB`). When omitted, the tool automatically calculates segment size based on collection size and available read workers.
- `--use-collection-bulk-write`: Forces collection-level bulk write instead of the newer client-level bulk write (MongoDB 8.0+).


??? example "Examples"

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
| `PCSM_CLONE_SEGMENT_SIZE` | Defines the segment size used during clone operations. Accepts values in bytes or with size suffixes such as `500MB` or `1GiB`. If not specified, PCSM automatically calculates the segment size based on collection size and available read workers. | `Auto` |
| `PCSM_MONGODB_CLI_OPERATION_TIMEOUT` | Maximum time to wait before timing out MongoDB client operations such as insert, update, delete. If the timeout is reached, the operation will fail.  | `5m` | 
| `PCSM_REPL_NUM_WORKERS` | Controls how many concurrent replication worker goroutines PCSM uses to apply DML (insert/update/replace/delete) events to the target cluster. | `runtime.NumCPU()` |
| `PCSM_REPL_CHANGE_STREAM_BATCH_SIZE` | Sets the maximum number of change stream events PCSM will request and read from MongoDB per batch while streaming changes from the source cluster. | `10000` |
| `PCSM_REPL_EVENT_QUEUE_SIZE` | Controls the size of the internal event queue used by the replication subsystem. | `5000` |
| `PCSM_REPL_WORKER_QUEUE_SIZE` | Defines the maximum number of replication events that each replication worker thread can queue before processing. | `5000` |
| `PCSM_REPL_BULK_OPS_SIZE` | Defines the maximum number of operations that can be grouped together into a single bulk apply batch during replication. | `5000` |

## MongoDB connection string options

PCSM supports the `maxPoolSize` MongoDB connection string option for configuring the maximum number of connections in the driver's connection pool.

Specify the option in the source and target MongoDB connection strings passed through `--source` and `--target`, or the `PCSM_SOURCE_URI` and `PCSM_TARGET_URI` environment variables.

### Syntax

If the URI contains no query parameters:

```bash
mongodb://host:27017/?maxPoolSize=500
```

If the URI already includes query parameters, append `maxPoolSize` with `&`:

```bash
mongodb://host:27017/?replicaSet=rs0&maxPoolSize=500
```

### Default behavior

If `maxPoolSize` is omitted, the MongoDB Go driver uses its default value of `100`.

Setting `maxPoolSize=0` removes the limit and allows the driver to create an unlimited number of connections.

### Recommendations

For clone operations, configure the connection pool so that it is at least as large as the corresponding worker count:

* **Source cluster:** `maxPoolSize` >= configured `--clone-num-read-workers` value
* **Target cluster:** `maxPoolSize` >= configured `--clone-num-insert-workers` value

At startup, PCSM logs the effective `maxPoolSize` for both clients. If the configured pool size is lower than the corresponding clone worker count, PCSM logs a warning because the connection pool may become a bottleneck.

!!! note
    `maxPoolSize` applies to each MongoDB server or mongos that the client connects to. It is not a global connection limit for the entire client.
