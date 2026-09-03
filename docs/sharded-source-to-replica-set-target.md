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

















