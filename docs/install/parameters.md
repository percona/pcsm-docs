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

    **--clone-segment-size**

    ```{.bash data-prompt="$"}
    $ pcsm start --clone-segment-size=1G
    {
    "ok": true
    }
    ```

    Check the logs

    ```
    2026-05-21 08:34:50.989 INF Starting HTTP server at     http://localhost:2242
    2026-05-21 08:37:22.475 INF GET /status s=http
    2026-05-21 08:43:56.309 INF GET /status s=http
    2026-05-21 08:44:59.346 INF POST /start s=http
    2026-05-21 08:44:59.347 INF Config: NumWorkers: 12 s=repl
    2026-05-21 08:44:59.347 INF Config: UseCollectionBulkWrite: false s=repl
    2026-05-21 08:44:59.347 INF Config: ChangeStreamBatchSize: 10000 s=repl
    2026-05-21 08:44:59.347 INF Config: EventQueueSize: 5000 s=repl
    2026-05-21 08:44:59.347 INF Config: WorkerQueueSize: 5000 s=repl
    2026-05-21 08:44:59.347 INF Config: BulkOpsSize: 5000 s=repl
    2026-05-21 08:44:59.347 INF Config: WorkerFlushInterval: 1s s=repl
    2026-05-21 08:44:59.347 INF Config: WorkerBulkQueueSize: 3 s=repl
    2026-05-21 08:44:59.347 INF Starting Cluster Replication s=pcsm
    2026-05-21 08:44:59.347 INF Starting Data Clone s=clone
    2026-05-21 08:44:59.349 INF Namespace "test_db.collection_0" included ns=test_db.collection_0 s=clone
    2026-05-21 08:44:59.351 INF Estimated Total Size 24 MB s=clone size_bytes=24220000
    2026-05-21 08:44:59.351 DBG NumParallelCollections: 2 s=clone
    2026-05-21 08:44:59.351 INF Config: NumReadWorkers: 3 s=copy
    2026-05-21 08:44:59.351 INF Config: NumInsertWorkers: 24 s=copy
    2026-05-21 08:44:59.351 INF Config: SegmentSizeBytes: 1000000000 (1.0 GB) s=copy
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
| `PCSM_CLONE_SEGMENT_SIZE` | Defines the segment size used during clone operations. Accepts values in bytes or with size suffixes such as 500MB or 1GiB. If not specified, PCSM automatically calculates the segment size based on collection size and available read workers. | `Auto` |
| `PCSM_MONGODB_CLI_OPERATION_TIMEOUT` | Maximum time to wait before timing out MongoDB client operations such as insert, update, delete. If the timeout is reached, the operation will fail.  | `5m` | 
| `PCSM_REPL_NUM_WORKERS` | Controls how many concurrent replication worker goroutines PCSM uses to apply DML (insert/update/replace/delete) events to the target cluster. | `runtime.NumCPU()` |
| `PCSM_REPL_CHANGE_STREAM_BATCH_SIZE` | Sets the maximum number of change stream events PCSM will request and read from MongoDB per batch while streaming changes from the source cluster. | `10000` |
| `PCSM_REPL_EVENT_QUEUE_SIZE` | Controls the size of the internal event queue used by the replication subsystem. | `5000` |
| `PCSM_REPL_WORKER_QUEUE_SIZE` | Defines the maximum number of replication events that each replication worker thread can queue before processing. | `5000` |
| `PCSM_REPL_BULK_OPS_SIZE` | Defines the maximum number of operations that can be grouped together into a single bulk apply batch during replication. | `5000` |

