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


## MongoDB connection string

!!! admonition "Version added: 0.10.0"

PCSM supports the MongoDB `maxPoolSize` connection string option, which controls the maximum number of connections the MongoDB Go driver can maintain in its connection pool.

You can set this option in the source and/or target MongoDB connection strings using `--source` and `--target` command-line options or through the `PCSM_SOURCE_URI` and `PCSM_TARGET_URI` environment variables.

### Syntax

Append `maxPoolSize` as a query parameter to your connection string:

Without existing query parameters:

~~~text
mongodb://host:port/?maxPoolSize=500
~~~

With existing query parameters:

~~~text
mongodb://host:port/?replicaSet=rs0&maxPoolSize=500
~~~

??? example "Example: maxPoolSize=500"

    ```{.bash data-prompt="$"}
    $ pcsm --source='mongodb://rs00:30000/?maxPoolSize=500' --target='mongodb://rs10:30100' --log-level='debug'
    ```

    Output
    ```{.text .no-copy}
    2026-06-24 15:16:40.691 INF Percona ClusterSync for MongoDB v0.10.0 3eb82dd 2026-06-24_09:36_UTC
    2026-06-24 15:16:40.692 INF Config: source client compressors: [snappy zstd zlib] s=connect
    2026-06-24 15:16:40.692 INF Config: source client maxPoolSize: 500 s=connect
    2026-06-24 15:16:40.711 INF Connected to source cluster [Percona Server for MongoDB 8.0.16-5]: mongodb://rs00:30000
    2026-06-24 15:16:40.711 INF Config: target client compressors: [snappy zstd zlib] s=connect
    2026-06-24 15:16:40.711 INF Config: target client maxPoolSize: 100 (driver default) s=connect
    2026-06-24 15:16:40.724 INF Connected to target cluster [Percona Server for MongoDB 8.0.16-5]: mongodb://rs10:30100
    2026-06-24 15:16:40.728 INF Checking Recovery Data for "pcsm" s=recovery
    2026-06-24 15:16:40.729 INF Recovery Data not found s=recovery
    2026-06-24 15:16:40.729 INF Starting HTTP server at http://localhost:2242
    ```

### How maxPoolSize works

| **Configuration**|**Behavior**|
|-------------|--------|
| Not set | Driver defaults to **100** connections |
| `maxPoolSize=N`| Driver caps the pool at **N** connections |
| `maxPoolSize=0`| Removes the limit, allowing the driver to create as many connections as needed.|


??? example "Example: maxPoolSize not defined"
    ```{.bash data-prompt="$"}
    $ pcsm --source='mongodb://rs00:30000' --target='mongodb://rs10:30100' --log-level='debug'
    ```

    Output
    ```{.text .no-copy}
    2026-06-24 15:15:04.503 INF Percona ClusterSync for MongoDB v0.10.0 3eb82dd 2026-06-24_09:36_UTC
    2026-06-24 15:15:04.504 INF Config: source client compressors: [snappy zstd zlib] s=connect
    2026-06-24 15:15:04.504 INF Config: source client maxPoolSize: 100 (driver default) s=connect
    2026-06-24 15:15:04.525 INF Connected to source cluster [Percona Server for MongoDB 8.0.16-5]: mongodb://rs00:30000
    2026-06-24 15:15:04.525 INF Config: target client compressors: [snappy zstd zlib] s=connect
    2026-06-24 15:15:04.525 INF Config: target client maxPoolSize: 100 (driver default) s=connect
    2026-06-24 15:15:04.533 INF Connected to target cluster [Percona Server for MongoDB 8.0.16-5]: mongodb://rs10:30100
    2026-06-24 15:15:04.546 INF Checking Recovery Data for "pcsm" s=recovery
    2026-06-24 15:15:04.546 INF Recovery Data not found s=recovery
    2026-06-24 15:15:04.546 INF Starting HTTP server at http://localhost:2242
    ```
    
### Recommendations

For the best clone performance, size the connection pool to match or exceed the number of clone workers.

| Cluster | Recommended `maxPoolSize`           |
| ------- | ----------------------------------- |
| Source  | At least `--clone-num-read-workers`   |
| Target  | At least `--clone-num-insert-workers` |

When PCSM starts, it logs the effective `maxPoolSize` for both the source and target clients. If the configured pool size is smaller than the corresponding clone worker count, PCSM logs a warning because the available connections may limit throughput.

!!! note
    `maxPoolSize` applies independently to each MongoDB server or `mongos` instance that the client connects to. It does not define a single global connection limit for the entire client.