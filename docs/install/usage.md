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

By default, {{pcsm.short}} writes data to the target with `majority` [write concern :octicons-link-external-16:](https://www.mongodb.com/docs/manual/reference/write-concern/){:target="_blank"}. This applies to documents copied during the initial clone and to changes applied during replication. Write concern controls how many members must acknowledge a write before MongoDB reports it as successful. Waiting for a majority is the safest option, but if target secondaries fall behind, writes can stall while they wait.

You can set the write concern to `majority` or to a positive integer from `1` to `2147483647`, which is the number of members that must acknowledge each write. {{pcsm.short}} rejects `0` (unacknowledged writes) and custom named write concerns.

When you set the write concern to `1`, only the primary of the target replica set needs to acknowledge each write. On a sharded target, that's the primary of each affected shard. This can reduce write stalls when target secondaries lag behind.

The setting applies only to data writes. Checkpoints, high availability (HA) state, and DDL operations, such as creating collections and indexes, always use `majority`.

!!! warning "Acknowledged writes can be rolled back"
    With a write concern below `majority`, the target primary confirms a write before enough secondaries have it to survive a failover. If that primary fails and another member takes over, MongoDB can roll back writes the old primary had already confirmed. {{pcsm.short}} still saves its checkpoints with `majority`, but that doesn't protect the data written before them. On a sharded target, the same applies to every shard. If a rollback happens, you might need to start a fresh sync.

Keep `majority` if automatic recovery must preserve data durability. Use a lower value only for a controlled migration where you can restart and validate the copy after a target failure. While you run below `majority`:
{.power-number}

1. Avoid [stepping down :octicons-link-external-16:](https://www.mongodb.com/docs/manual/reference/method/rs.stepDown/){:target="_blank"} the target primary.

2. Keep the source available and verify that the target is consistent before cutover.

For details on rollbacks, see [Rollbacks during replica set failover :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/replica-set-rollbacks/){:target="_blank"} in the MongoDB documentation.

With any write concern, a slow target makes {{pcsm.short}} fall behind the source. Monitor the [source oplog window](../oplog-sizing.md#extend-the-oplog-window-if-the-lag-approaches-its-limit) and extend it before the changes {{pcsm.short}} still needs to apply are removed from the oplog.

The following examples set the write concern to `1`:

=== "Command line"

    ```{.bash data-prompt="$"}
    pcsm start --target-write-concern=1
    ```

=== "HTTP API"

    Send the value as a string in the `/start` request:

    ```{.bash data-prompt="$"}
    curl -X POST http://localhost:2242/start \
        -H "Content-Type: application/json" \
        --data '{"targetWriteConcern": "1"}'
    ```

=== "Environment variable"

    Set the variable for the `pcsm start` command:

    ```{.bash data-prompt="$"}
    export PCSM_TARGET_WRITE_CONCERN=1
    pcsm start
    ```

If you set both, the `--target-write-concern` flag takes precedence over `PCSM_TARGET_WRITE_CONCERN`. Only `pcsm start` reads the variable. The {{pcsm.short}} server ignores it and has no startup option for target write concern, so a run started without a per-run value uses `majority`. {{pcsm.short}} also ignores any write concern set in the target connection string.

The write concern belongs to the run. {{pcsm.short}} saves the value and keeps it through checkpoint recovery and [HA takeover](../high-availability.md#checkpoint-recovery). Since `pcsm resume` and `/resume` don't accept a write concern, the only way to change it is to start a new run. Keep in mind that a new run drops and recreates the selected target collections, as described in [Start the replication](#start-the-replication).

To confirm which value is in effect, check the [logs](../logging.md). When a run starts or recovers, the clone and replication components log `Config: TargetWriteConcern: <value>`.

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
