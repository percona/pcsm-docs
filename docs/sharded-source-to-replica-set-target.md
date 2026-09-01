# Replicate from a sharded cluster to a replica set

Percona ClusterSync for MongoDB (PCSM) supports replication from a sharded MongoDB cluster to a replica set. This lets you migrate data from a sharded deployment without having to recreate the source sharding configuration on the target.

For example, you can use this topology when moving data from a sharded MongoDB Atlas or MongoDB Enterprise deployment to a Percona Server for MongoDB replica set.

For information about sharded cluster support, see [Sharding support in Percona ClusterSync for MongoDB](sharding.md).

## How PCSM handles the topology difference

When replication starts, PCSM detects that the source is sharded and the target is a replica set.

If a source collection is sharded, PCSM skips sharding operations such as shardCollection on the target. These operations apply only to sharded clusters.

PCSM then continues with the standard clone and replication workflow. No additional configuration is required.

!!! note
    !!! note
        A collection that is sharded on the source is created as a regular collection on the replica set target. The collection data is copied, but the target collection isn't sharded.



