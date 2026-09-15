# Replicate from a sharded cluster to a replica set

!!! admonition "Version added: 0.10.0"

{{pcsm.full_name}} (PCSM) supports replication from a sharded MongoDB cluster to a replica set. This lets you migrate data from a sharded deployment without having to recreate the source sharding configuration on the target.

For example, you can use this topology when moving data from a sharded MongoDB Atlas or MongoDB Enterprise deployment to a Percona Server for MongoDB replica set.

For information about sharded cluster support, see [Sharding support in Percona ClusterSync for MongoDB](sharding.md).

## Overview

When the PCSM server starts, it detects that the source is sharded and the target is a replica set.

During the initial sync, PCSM creates every source collection on the target, including the sharded ones, as a regular collection. It doesn't carry over the source shard key, because a replica set has no shards to distribute documents across and doesn't support [`shardCollection` :octicons-link-external-16:](https://www.mongodb.com/docs/manual/reference/command/shardCollection/){:target="_blank"}.

During change replication, PCSM skips `shardCollection` events coming from the source [change stream :octicons-link-external-16:](https://www.mongodb.com/docs/manual/changeStreams/){:target="_blank"} and keeps applying the data changes it supports. No additional configuration is required.

!!! note
    A collection that is sharded on the source is created as a regular collection on the replica set target. The collection data is copied, but the target collection isn't sharded.

## What is replicated

| **On the source** | **On the replica set target** |
|---|---|
| Sharded collection | Created as a regular collection. All documents are copied. The shard key isn't applied because it doesn't apply to a replica set. |
| Unsharded collection | Created and copied as in a replica set to replica set sync. |
| Chunk distribution and primary shard | Not preserved. PCSM replicates data, not cluster metadata. |

## Before you start

* Ensure the source and target MongoDB versions meet the version requirements.
* Configure authentication for both deployments.
* Configure the source connection string with the `mongos` hostname and port. Configure the target connection string with the replica set members.
* Verify that PCSM can connect to both the source sharded cluster and the target replica set.

## Connection string format

Point the source URI at the `mongos` hostname and port. Point the target URI at the replica set members and name the replica set:

**Example**

```sh
PCSM_SOURCE_URI="mongodb://source-user:password@mongos-source:27017/admin" 

PCSM_TARGET_URI="mongodb://target-user:password@target1:27017,target2:27017,target3:27017/admin?replicaSet=rs0"
```

In this example, `mongos-source:27017` is the `mongos` endpoint for the source sharded cluster. The target URI lists the replica set members and identifies the replica set as `rs0`.

## usage

The commands and API endpoints are the same as for any other topology. See, [Percona ClusterSync for MongoDB commands](pcsm-commands.md) for the command reference. 

??? example "Walkthrough: sharded source to replica set target"

    Follow these steps:
    {.power-number}

    1. Create two clusters: one sharded source cluster and one target replica set.

    2. Create two collections on the sharded cluster:
    
        1. `sharded_coll` (sharded)
        2. `plain_collection` (unsharded)

    3. Add documents to both the collections.

    4. Start replication:

        ```sh
        pcsm start
        ```

    5. Check the replication status. `clonedSizeBytes` matches `estimatedCloneSizeBytes`, and the state is `running`:

        ```{.text .no-copy}
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

    6. Run the same query against both deployments and compare the results to confirm that both collections are present and that document counts match:

        ```javascript
        db.sharded_coll.countDocuments()
        db.plain_collection.countDocuments()
        ```

        The collection that was sharded on the source appears here as a regular collection. That is expected.

    7. Finalize the sync:

        ```{.bash data-prompt="$"}
        $ pcsm finalize
        ```

    8. Check the status again until the state is `finalized`:

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

    9. Check the replication logs and confirm that no errors were recorded. For details, see [Logging in Percona ClusterSync for MongoDB](logging.md).

    10. Confirm that the documents for both `plain_collection` and `sharded_coll` got copied to the destination cluster.


## Next steps

* [Install {{pcsm.full_name}}](installation.md)
* [Configure authentication](install/authentication.md)
* [Start replication](install/usage.md)
* [Monitor replication status](install/usage.md#check-the-replication-status)
* [Monitor PCSM performance with Percona Monitoring and Management](pmm-setup.md)


## Learn more

[Shard Keys :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/sharding-shard-key/){:target="_blank"}


















