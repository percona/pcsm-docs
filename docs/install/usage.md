# Use {{pcsm.full_name}}

{{pcsm.full_name}} doesn't automatically start data replication after startup. It has the `idle` status indicating that it is ready to accept requests.

!!! tip "Understanding the workflow"

    For an overview of how {{pcsm.short}} works and the replication workflow stages, see [How {{pcsm.full_name}} works](../intro.md).

You can interact with {{pcsm.full_name}} using the command-line interface or via the HTTP API. Read more about [{{pcsm.short}} HTTP API](../api.md).

!!! note "CLI exit codes and error output"
    The examples on the page show `{"ok": true}` as the expected output for successful commands. This is correct for successful responses. However, client subcommands now exit with a non-zero code when the server returns an error response (for example, `{"ok": false, "error": "..."}`). Previously, they exited with code `0` and printed the error JSON to **stdout**. Now, the error message is written to **stderr** and the process exits non-zero.


## Before you start

Your target MongoDB cluster may be empty or contain data. {{pcsm.short}} replicates data from the source to the target but doesn't manage the target's data. If the target already has the same data as the source, {{pcsm.short}} overwrites it. However, if the target contains different data, {{pcsm.short}} doesn't delete it during replication. This leads to inconsistencies between the source and target. To ensure consistency, manually delete any existing data from the target before starting replication.

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
| `keys` | object | Key specification: field names mapped to their sort order or index type. |
| `type` | string | Machine-readable problem category. |
| `reason` | string | Human-readable explanation of what was observed during this finalize attempt. |

The `type` field can contain the following values:

| **Type** | **Reason** |  **What it means** |
|---|---|---|
| `failed` | MongoDB error message (not stable) | The index build was attempted and encountered an error and could not be completed successfully. As a result, the index is not available in a usable state on the target cluster. |
| `incomplete` | `"Index build did not complete"` | The index build was still in progress on the source cluster during the clone phase. Because the build had not finished, PCSM could not clone a complete and consistent version of the index to the target cluster. As a result, the index is reported as `incomplete` and is not cloned on the target.|
| `inconsistent` | `"Index exists on source but not on target"` | Indexes that exist on some shards but are missing on others, or whose builds fail on certain shards because of conflicting or invalid data.|