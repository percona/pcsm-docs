# Troubleshooting guide

This guide helps you recover {{plm.full_name}} after an unexpected interruption, whether it occurs during initial data clone or real-time replication.

## Recover PLM during initial data clone

{{plm.full_name}} can interrupt because of various reasons. For example, it is restarted, abnormally exits or loses connection to the source or destination cluster for an extended time. In any of these cases you must restart the initial data clone.

### Symptoms

After subsequently starting the service, you may see such messages:

??? example "Sample error messages"

    ```{.text .no-copy}
    2025-06-02 21:25:38.927 INF Found Recovery Data. Recovering... s=recovery
    Error: new server: recover Percona Link for MongoDB: recover: cannot resume: replication is not started or not resuming from failure
    2025-06-02 21:25:38.929 FTL error="new server: recover Percona Link for MongoDB: recover: cannot resume: replication is not started or not resuming from failure"
    ```

### Recovery steps 

To recover PLM, do the following:
{.power-number}

1. Stop the `plm` service:

    ```{.bash data-prompt="$"}
    $ sudo systemctl stop plm
    ```

2. Reset the PLM state with the following command and pass the connection string URL to the target deployment:
 
    ```{.bash data-prompt="$"}
    $ plm reset --target <target-mongodb-uri>
    ```

    The command does the following:

    * Connects to the target MongoDB deployment
    * Deletes the metadata collections 
    * Restores the `plm` service from the `failed` state

3. Restart `plm`

    ```{.bash data-prompt="$"}
    $ sudo systemctl start plm
    ```

4. Start data replication from scratch:

    ```{.bash data-prompt="$"}
    $ plm start
    ```

## Recover PLM during real-time replication

PLM can successfully complete the initial data clone and then interrupt unexpectedly, during the real-time replication. The recovery steps differ depending on how PLM stopped.

### Unexpected shutdown

If PLM exits abnormally or is stopped unexpectedly, restart the `plm` service. This is typically sufficient as PLM resumes replication automatically from the last saved checkpoint.

??? example "Example logs"

    ```{.text .no-copy}
    2025-06-02 21:32:04.592 INF Starting Cluster Replication s=plm
    2025-06-02 21:32:04.592 DBG Change Replication is resuming s=repl
    2025-06-02 21:32:04.592 INF Change Replication resumed op_ts=[1748887947,1] s=repl
    2025-06-02 21:32:04.594 DBG Checkpoint saved s=checkpointing
    ```

### Replication fails while PLM is running

The `plm` process is active but the replication may fail due to a temporary connection issue or other reasons. After you resolve the reason of failure (restore the connection), follow these steps to recover PLM:

1. Check current replication status:

    ```{.bash data-prompt="$"}
    $ plm status
    ```

    ??? example "Sample output"
        
        ```{.text .no-copy}
         {
           "ok": false,
           "error": "change replication: bulk write: server selection error: context deadline exceeded, current topology: { Type: ReplicaSetNoPrimary, Servers: [{ Addr: sandra-xps15:28017, Type:          Unknown, Last error: dial tcp 127.0.1.1:28017: connect: connection refused }, ] }",
           "state": "failed",
           "info": "Failed",
           "eventsProcessed": 2301,
           "lastReplicatedOpTime": "1748889570.1",
           "initialSync": {
             "lagTime": 0,
             "estimatedCloneSize": 0,
             "clonedSize": 0,
             "completed": true,
             "cloneCompleted": true
           }
         }
        ```

2. Resume the replication from the last successful checkpoint:
    
    ```{.bash data-prompt="$"}
    $ plm resume --from-failure
    ```

3. Confirm that the replication has resumed:
   
    ```{.bash data-prompt="$"}
    plm status
    ```

    ??? example "Sample output after successful resume"
  
        ```{.text .no-copy}
        {
          "ok": true,
          "state": "running",
          "info": "Replicating Changes",
          "lagTime": 140,
          "eventsProcessed": 2301,
          "lastReplicatedOpTime": "1748889570.1",
          "initialSync": {
            "lagTime": 140,
            "estimatedCloneSize": 0,
            "clonedSize": 0,
            "completed": true,
            "cloneCompleted": true
          }
        }
        ```

!!! note

    If replication still fails after using the `plm resume --from-failure`, even after you restored the connectivity, the target cluster availability or any other underlying issue, you'll need to start over. Refer to the [Recover PLM during initial data clone](#recover-plm-during-initial-data-clone) section and reset the PLM state to begin replication from scratch.
