# Replicate from a sharded cluster to a replica set

Percona ClusterSync for MongoDB (PCSM) supports replication from a sharded MongoDB cluster to a replica set. This lets you migrate data from a sharded deployment without having to recreate the source sharding configuration on the target.

!!! info "Important"
    Sharding support in PCSM is a technical preview. We recommend that early adopters use this release for testing purposes only and not in production environments.

For example, you can use this topology when moving data from a sharded MongoDB Atlas or MongoDB Enterprise deployment to a Percona Server for MongoDB replica set.

For information about sharded cluster support, see [Sharding support in Percona ClusterSync for MongoDB](sharding.md).

