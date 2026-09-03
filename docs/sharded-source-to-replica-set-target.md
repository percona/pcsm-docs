# Replicate from a sharded cluster to a replica set

Percona ClusterSync for MongoDB (PCSM) supports replication from a sharded MongoDB cluster to a replica set. This lets you migrate data from a sharded deployment without having to recreate the source sharding configuration on the target.

For example, you can use this topology when moving data from a sharded MongoDB Atlas or MongoDB Enterprise deployment to a Percona Server for MongoDB replica set.

For information about sharded cluster support, see [Sharding support in Percona ClusterSync for MongoDB](sharding.md).

## How PCSM handles the topology difference

When replication starts, PCSM detects that the source is sharded and the target is a replica set.

If a source collection is sharded, PCSM skips sharding operations such as `shardCollection` on the target. These operations apply only to sharded clusters.

PCSM then continues with the standard clone and replication workflow. No additional configuration is required.

!!! note
    A collection that is sharded on the source is created as a regular collection on the replica set target. The collection data is copied, but the target collection isn't sharded.

## What is replicated

| **On the source** | **On the replica set target** |
|---|---|
| Sharded collection | Created as a regular collection. All documents are copied. The shard key isn't applied because it doesn't apply to a replica set. |
| Unsharded collection | Created and copied as in a replica set to replica set sync. |
| Chunk distribution and primary shard | Not preserved. PCSM replicates data, not cluster metadata. |

## Before you start

- Ensure the source and target MongoDB versions meet the [version requirements](version-compatibility.md#version-compatibility-matrix).
- Configure authentication for both deployments. Refer to [Configure authentication in MongoDB](./install/authentication.md).
- Verify that PCSM can connect to the source sharded cluster and the target replica set.

## Replication before and after cross-topology support

=== "Before cross-topology support"

    Without cross-topology handling, PCSM attempts to apply the source collection's sharding configuration to the replica set. The clone fails because the target doesn't support `shardCollection`.

    ??? example "Example"

        Follow these steps:
        {.power-number}

        1. Create two clusters, one sharded (source) and the other replica set (destination).

        2. Create two collections on the sharded cluster:

            1. `sharded_coll` (sharded)
            2. `plain_collection` (unsharded)

        3. Add documents to both the collections.

        4.  Start replication:

            ```sh
            pcsm start
            ```
        5. Check the replication status:

            ```{.text .no-copy}
            pcsm status
            {
                "ok": false,
                "error": "clone: copy: clone_shard_test_db.sharded_coll: shard collection: (CommandNotFound) no such command: 'shardCollection'",
                "state": "failed",
                "info": "Failed",
                "lagTimeSeconds": 0,
                "eventsRead": 0,
                "eventsApplied": 0,
                "initialSync": {
                    "estimatedCloneSizeBytes": 7490,
                    "clonedSizeBytes": 1490,
                    "completed": false,
                    "cloneCompleted": true
                }
            }
            Error: clone: copy: clone_shard_test_db.sharded_coll: shard collection: (CommandNotFound) no such command: 'shardCollection'
            2026-08-25T07:51:17.586Z FTL error="clone: copy: clone_shard_test_db.sharded_coll: shard collection: (CommandNotFound) no such command: 'shardCollection'"
            ```
        
        6. Check the logs:

            `pcsm start 2> pcsm.log`

            Output:

            ```json
            2026-08-25T07:56:21.508Z ERR Data Clone has failed: 0 B in 0s error="copy: clone_shard_test_db.sharded_coll: shard collection: shard collection: (CommandNotFound) no such command: 'shardCollection'" elapsed_secs=0.114 s=clone 
            2026-08-25T07:56:21.508Z ERR Cluster Replication has failed error="clone: copy: clone_shard_test_db.sharded_coll: shard collection: shard collection: (CommandNotFound) no such command: 'shardCollection'" s=pcsm
            ```

        7. Confirm that neither collection reached the target. The clone stops at the first failure, so even the unsharded collection is missing.

=== "After cross-topology support"

    With cross-topology support, PCSM detects the replica set target and skips the unsupported sharding operations.

    ??? example "Example"

        Follow these steps:
        {.power-number}

        1. Create two clusters, one sharded (source) and the other replicaset (destination).

        2. Create two collections on the sharded cluster:

            1. Sharded_collection (sharded) 
            2. Plain_collection (non-sharded)

        3. Add documents to both the collections.

        4.  Start replication:

            ```sh
            pcsm start
            ```
        5. Check the replication status. `clonedSizeBytes` matches `estimatedCloneSizeBytes`, and the state is `running`:

            ```json
            pcsm status
            { 
                "ok": true, 
                "state": "running", 
                "info": "Replicating Changes", 
                "lagTimeSeconds": 0, 
                "eventsRead": 0, 
                "eventsApplied": 0, 
                "lastReplicatedOpTime": { 
                    "ts": "1787645813.1", 
                    "isoDate": "2026-08-25T08:16:53Z" 
                }, 
            "initialSync": { 
                    "estimatedCloneSizeBytes": 7490, 
                    "clonedSizeBytes": 7490, 
                    "completed": true, 
                    "cloneCompleted": true 
                } 
            }
            ```

        6. Confirm that both collections are present on the target and that document counts match:

            ```javascript
                db.<collection>.countDocuments()
            ```
        
            The collection that was sharded on the source appears here as a regular collection. That is expected.


        7. Finalize the sync:

            ```{.bash data-prompt="$"}
            $ pcsm finalize
            ```

        8. Check the status again:

            ```{.bash data-prompt="$"}
            $ pcsm status
            ```

            ```{.json .no-copy}
            {
              "ok": true,
              "state": "finalized",
              "info": "Finalized",
              "lagTimeSeconds": 1,
              "eventsRead": 0,
              "eventsApplied": 0,
              "lastReplicatedOpTime": {
                "ts": "1787645817.1",
                "isoDate": "2026-08-25T08:16:57Z"
              },
              "initialSync": {
                "estimatedCloneSizeBytes": 7490,
                "clonedSizeBytes": 7490,
                "completed": true,
                "cloneCompleted": true
              },
              "finalization": {
                "completed": true,
                "startedAt": "2026-08-25T08:16:57.539447026Z",
                "completedAt": "2026-08-25T08:16:57.539557888Z"
              }
            }
            ```

        8. Check the logs and confirm that no errors were recorded.

            `pcsm start 2> pcsm.log`

        9. Confirm that the documents for both `plain_collection` and `sharded_collection` got copied to the destination cluster. 

To learn how MongoDB uses shard keys to distribute documents across shards, see [Shard Keys octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/sharding-shard-key/){:target="_blank"} in the MongoDB documentation.
















