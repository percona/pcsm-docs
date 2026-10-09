# Use {{pcsm.full_name}}

{{pcsm.full_name}} doesn't automatically start data replication after startup. It has the `idle` status indicating that it is ready to accept requests.

!!! tip "Understanding the workflow"

    For an overview of how {{pcsm.short}} works and the replication workflow stages, see [How {{pcsm.full_name}} works](../intro.md).

You can interact with {{pcsm.full_name}} using the command-line interface or via the HTTP API. Read more about [{{pcsm.short}} HTTP API](../api.md).

For command-line subcommands, responses are written to `stdout` while logs and errors are written to `stderr`. For details on capturing command output, see [Logging](../logging.md).

!!! warning "Target collections are overwritten on start"
    When you start replication (for example, using `pcsm start` or the `/start` API endpoint), {{pcsm.short}} drops and recreates the collections selected for replication on the target, overwriting any existing data in those collections. Databases and collections that are not selected for replication remain untouched.

## Start the replication

Start the replication process between source and target clusters. {{pcsm.short}} starts copying the data from the source to the target. First it does the initial sync by cloning the data and then applying all the changes that happened since the clone start. 

Then it uses [change streams :octicons-link-external-16:](https://www.mongodb.com/docs/manual/changeStreams/) to track changes on the source and replicate them to the target.

=== "Command line"

    ```{.bash data-prompt="$"}
    $ pcsm start
    ```

    ??? example "Expected output"

        ```{.json .no-copy}
        {
          "ok": true
        }
        ```

=== "HTTP API"
    
    Send a POST request to the `/start` endpoint:

    ```{.bash data-prompt="$"}
    $ curl -X POST http://localhost:2242/start 

    ```

### Configure target write concern

!!! admonition "Version added: 1.1.0"

You can choose the [write concern :octicons-link-external-16:](https://www.mongodb.com/docs/v8.0/reference/write-concern/){:target="_blank"} for data written to the target during the initial clone and ongoing replication. Write concern determines how many MongoDB members must acknowledge a write before PCSM continues. The default is `majority`.

Using `1` requires acknowledgment from the target primary only. This can reduce write stalls when target secondaries lag. The setting applies to data writes only. Checkpoints, high availability (HA) state, and schema changes, such as creating collections and indexes, always use `majority`.

!!! warning "Rollback risk with a lower write concern"

    With a write concern below majority, a target primary failure or stepdown can roll back data that PCSM has already recorded as copied. Majority checkpoints do not protect those data writes from rollback. A fresh synchronization may be required.

    Keep `majority` when you rely on automatic recovery to preserve acknowledged data. Use a lower value only for a controlled migration where you can restart and validate the copy after a target failure. Avoid target primary stepdowns during the run. Retain the source and verify target consistency before cutover.

Set the write concern when starting a new run. Use `majority` or a decimal integer from `1` to `2147483647`. Numeric values specify the number of data-bearing members that must acknowledge each write. PCSM rejects `0`, negative values, values above this range, and custom named write concerns.

The following examples use `1`:

=== "Command line"

    ```{.bash data-prompt="$"}
    $ pcsm start --target-write-concern=1
    ```

=== "HTTP API"

    Send the value as a string in the `/start` request:

    ```{.bash data-prompt="$"}
    $ curl -X POST http://localhost:2242/start \
        -H "Content-Type: application/json" \
        --data '{"targetWriteConcern": "1"}'
    ```

=== "Environment variable"

    Set the variable for the `pcsm start` command:

    ```{.bash data-prompt="$"}
    $ export PCSM_TARGET_WRITE_CONCERN=1
    $ pcsm start
    ```

The `--target-write-concern` flag overrides `PCSM_TARGET_WRITE_CONCERN`. This environment variable applies only to `pcsm start`. The PCSM server process ignores it. A run started without an explicit write concern uses `majority`, including a run started automatically with the server's `--start` option. Write concern options in the target connection string do not override this setting.

The selected value is saved with the run and retained during checkpoint recovery and [HA takeover](../high-availability.md#checkpoint-recovery). You cannot change it with `pcsm resume` or `/resume`. To use a different value, start a new run. Starting a new run drops and recreates the selected target collections, as described in [Start the replication](#start-the-replication).

When a run starts or recovers, the [logs](../logging.md) show `Config: TargetWriteConcern: <value>` for the clone and replication components. If the target slows down during migration, monitor the [source oplog window](../oplog-sizing.md#extend-the-oplog-window-if-the-lag-approaches-its-limit) and extend it before required changes expire.

## Start the filtered replication

You can replicate the whole dataset or specific namespaces - databases and collections. You can specify what namespaces to include and/or exclude from the replication. 

To include or exclude a specific database and all collections it includes, pass it in the format `mydb.*`.

When both include and exclude filters are used, the exclude filter takes precedence. For instance, if you include all collections in the `mydb` database but exclude `mydb.users`, PCSM will replicate all collections from `mydb` **except** `mydb.users`.

=== "Command line"

    ```{.bash data-prompt="$"}
    $ pcsm start \ 
    --include-namespaces="db1.collection1,db2.collection2" \
    --exclude-namespaces="db3.collection3"
    ```

    ??? example "Expected output"

        ```{.json .no-copy}
        {
          "ok": true
        }
        ```

=== "HTTP API"
    
    Send a POST request to the `/start` endpoint:

    ```{.bash data-prompt="$"}
    $ curl -X POST http://localhost:2242/start -d '{
        "includeNamespaces": ["db1.collection1", "db2.collection2"],
        "excludeNamespaces": ["db3.collection3"]
    }'
    ```

## Pause the replication

You can pause the replication at any moment. {{pcsm.short}} stops the replication, saves the timestamp, and enters the `paused` state. {{pcsm.short}} uses the saved timestamp after you [resume the replication](#resume-the-replication).

=== "Command line"

    ```{.bash data-prompt="$"}
    $ pcsm pause
    ```

=== "HTTP API"

    Send a POST request to the `/pause` endpoint:

    ```{.bash data-prompt="$"}
    $ curl -X POST http://localhost:2242/pause
    ```

## Resume the replication

Resume the replication. {{pcsm.short}} changes the state to `running` and copies the changes that occurred from the timestamp it saved when you paused the replication. Then it continues monitoring data changes and replicating them in real time. 

=== "Command line"

    ```{.bash data-prompt="$"}
    $ pcsm resume
    ```

=== "HTTP API"

    Send a POST request to the `/resume` endpoint:

    ```{.bash data-prompt="$"}
    $ curl -X POST http://localhost:2242/resume
    ```

The replication may fail for some reason, like lost connectivity or the like. In this case you can resume replication by adding the `--from-failure` flag to the `resume` command:

=== "Command line"

    ```{.bash data-prompt="$"}
    $ pcsm resume --from-failure
    ```

=== "HTTP API"

    Send a POST request to the `/resume` endpoint:

    ```{.bash data-prompt="$"}
    $ curl -X POST http://localhost:2242/resume -d '{
        "fromFailure": true
    }'
    ```


## Check the replication status

Check the current status of the replication process.

=== "Command line"

    ```{.bash data-prompt="$"}
    $ pcsm status
    ```

=== "HTTP API"

    Send a GET request to the `/status` endpoint:

    ```{.bash data-prompt="$"}
    $ curl http://localhost:2242/status
    ```

## Finalize the replication

When you no longer need / want to replicate data, finalize the replication. {{pcsm.short}} stops replication, creates the required indexes on the target, and stops. This is a one-time operation. You cannot restart the replication after you finalized it. If you run the `start` command, {{pcsm.short}} will start the replication anew, with the initial sync. 

=== "Command line"

    ```{.bash data-prompt="$"}
    $ pcsm finalize
    ```

=== "HTTP API"
    
    Send a POST request to the `/finalize` endpoint:

    ```{.bash data-prompt="$"}
    $ curl -X POST http://localhost:2242/finalize
    ```

### Check finalization status

You can use the `/status` endpoint to monitor finalization progress and inspect the outcome after it completes.

During finalization, `/status` indicates that finalization is in progress. After it completes, `/status` reports the finalization result, including whether any index builds were unsuccessful.

For general `/status` endpoint details, see the [{{pcsm.short}} HTTP API](../api.md). The example below shows the finalization-specific fields returned after finalization completes.

??? example "Example: Finalization completed with one failed index"

    ```{.json .no-copy}
    {
      "ok": true,
      "state": "finalized",
      "info": "Finalized",
      "lagTimeSeconds": 0,
      "eventsRead": 1234,
      "eventsApplied": 1234,
      "initialSync": {
        "completed": true,
        "cloneCompleted": true,
        "clonedSizeBytes": 1073741824
      },
      "finalization": {
        "completed": true,
        "startedAt": "2026-05-07T10:30:00Z",
        "completedAt": "2026-05-07T10:30:42Z",
        "unsuccessfulIndexes": [
          {
            "namespace": "mydb.users",
            "indexName": "email_unique_idx",
            "type": "failed",
            "reason": "recreate index mydb.users.email_unique_idx: duplicate key error",
            "keys": {"email": 1}
          }
        ]
      }
    }
    ```

The `unsuccessfulIndexes` array will not appear if there are no unsuccessful indexes.

#### Unsuccessful indexes

The `unsuccessfulIndexes` array lists indexes that could not be finalized successfully on the target cluster. During finalization, PCSM retries the creation of `failed` and `incomplete` indexes, while `inconsistent` indexes are skipped. Only indexes that remain unsuccessful after these retry attempts are reported in the `unsuccessfulIndexes` array. Each entry contains:

| **Field** | **Type** | **Description** |
|---|---|---|
| `namespace` | string | The MongoDB namespace containing the index, in `database.collection` format. |
| `indexName` | string | The index name as registered in the data store. |
| `type` | string | Machine-readable problem category. |
| `keys` | object | Key specification: field names mapped to their sort order or index type. |
| `reason` | string | Human-readable explanation of what was observed during this finalize attempt. |

The `type` field can contain the following values:

| **Type** | **Reason** |  **What it means** |
|---|---|---|
| `failed` | `MongoDB error message (not stable)` | The index build was attempted and encountered an error and could not be completed successfully. As a result, the index is not available in a usable state on the target cluster. |
| `incomplete` | `MongoDB error message (not stable)` | The index could not be successfully recreated during the finalization phase. PCSM reports the index as incomplete, and the reason contains the error message returned by MongoDB during the failed recreation attempt.|
| `inconsistent` | `index is missing on one or more source shards` | Indexes that exist on some shards but are missing on others. |
