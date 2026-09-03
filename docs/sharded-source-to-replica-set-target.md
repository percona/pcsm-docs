# Replicate from a sharded cluster to a replica set

Percona ClusterSync for MongoDB (PCSM) supports replication from a sharded MongoDB cluster to a replica set. This lets you migrate data from a sharded deployment without having to recreate the source sharding configuration on the target.

For example, you can use this topology when moving data from a sharded MongoDB Atlas or MongoDB Enterprise deployment to a Percona Server for MongoDB replica set.

For information about sharded cluster support, see [Sharding support in Percona ClusterSync for MongoDB](sharding.md).

## How PCSM handles the topology difference

When replication starts, PCSM detects that the source is sharded and the target is a replica set.

If a source collection is sharded, PCSM skips sharding operations such as `shardCollection` on the target. These operations apply only to sharded clusters.

PCSM then continues with the standard clone and replication workflow. No additional configuration is required.

!!! note
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

    ??? example "Example"

        Follow these steps:
        {.power-number}

        1. Create two clusters, one sharded (source) and the other replicaset (destination).

        2. Set up PCSM.

            ```text
            pcsm version 
            Version:   v0.9.0 
            Platform:  linux 
            GitCommit: 33567da 
            GitBranch: HEAD 
            BuildTime: 2026-08-25_07:48_UTC
            ```
        3. Create two collections on the sharded cluster:

            1. Sharded_collection (sharded) 
            2. Plain_collection (non-sharded)

        4. Add documents to both the collections.

        5.  Start replication:

            ```sh
            pcsm start
            ```
        6. Check the replication status:

            ```json
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
        
        7. Check the logs:

            `pcsm start 2> pcsm.log`

            Output:

            ```json
            2026-08-25T07:56:21.508Z ERR Data Clone has failed: 0 B in 0s error="copy: clone_shard_test_db.sharded_coll: shard collection: shard collection: (CommandNotFound) no such command: 'shardCollection'" elapsed_secs=0.114 s=clone 
        2026-08-25T07:56:21.508Z ERR Cluster Replication has failed error="clone: copy: clone_shard_test_db.sharded_coll: shard collection: shard collection: (CommandNotFound) no such command: 'shardCollection'" s=pcsm
        ```

        8. Confirm that the documents for both `plain_collection` and `sharded_collection` did not copy to the destination cluster. 

        Replication fails when PCSM attempts to run `shardCollection` against the replica set target. Before cross-topology support, PCSM attempted to run `shardCollection` on the replica set target when the source collection had a shard key. Because `shardCollection` is only valid on a sharded cluster, the migration failed.


=== "After cross-topology support"

    ??? example "Example"

        Follow these steps:
        {.power-number}

        1. Create two clusters, one sharded (source) and the other replicaset (destination).

        2. Set up PCSM.

            ```text
            pcsm version 
            Version:   v0.9.0 
            Platform:  linux 
            GitCommit: f12f81 
            GitBranch: main 
            BuildTime: 2026-08-25_08:14_UTC
            GoVersion: go1.27.0
            ```
        3. Create two collections on the sharded cluster:

            1. Sharded_collection (sharded) 
            2. Plain_collection (non-sharded)

        4. Add documents to both the collections.

        5.  Start replication:

            ```sh
            pcsm start
            ```
        6. Check the replication status:

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
        7. Check if if it has successfully finalized 

            ```json
            pcsm status 
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

        8. Check the logs:

            `pcsm start 2> pcsm.log`

        8. Confirm that the documents for both `plain_collection` and `sharded_collection` did not copy to the destination cluster. 

        Replication is successful when PCSM runs `shardCollection` against the replica set target.



















