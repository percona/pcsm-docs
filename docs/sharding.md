# Sharding support in {{pcsm.full_name}}

{{pcsm.full_name}} supports replication between sharded MongoDB clusters. You can use it to migrate data from one sharded deployment to another with minimal downtime, or to keep data synchronized for testing and development.

## Overview

The replication workflow for sharded clusters is similar to the workflow for replica sets. See [How {{pcsm.full_name}} works](intro.md#replication-workflows) for an overview of the replication stages.

For sharded deployments, {{pcsm.short}} connects to `mongos` on both the source and target clusters instead of connecting directly to individual shard members. The source and target can have different numbers of shards.

{{pcsm.short}} does not continuously replicate sharding metadata. For collections with a ranged shard key, it uses the source chunk boundaries to prepare the target before the initial clone begins. Changes to the chunk layout that occur later on the source are not replicated to the target.

The primary shard assignment can also differ between the source and target clusters.

## Prerequisites

* If the target is a sharded MongoDB deployment, {{pcsm.full_name}} version 0.7.0 or later.
* If the target is a replica set, {{pcsm.full_name}} version 1.0.0 or later.
* The source must be a sharded MongoDB deployment.
* The target can be either a sharded MongoDB deployment or a replica set.
* Both clusters must be running the same MongoDB version. Check [Version requirements](deployment.md#version-requirements) for more information about supported versions.

## Connection string format

When connecting to a sharded source or a sharded target, use the standard MongoDB connection string format but specify the `mongos` hostname and port instead of replica set members:

```{.text .no-copy}
mongodb://user:pwd@mongos-host:port/[authdb]?[options]
```

When the target is a replica set, specify the target replica set members in the target connection string instead of a `mongos` URI. {{pcsm.short}} does not require a target `mongos` instance in that topology.

For detailed information about authentication and connection string configuration, see [Configure authentication in MongoDB](install/authentication.md).

## Sharding-specific behavior

The following behavior applies when both the source and target are sharded MongoDB deployments. For replica set targets, see [Replicate from a sharded cluster to a replica set](sharded-source-to-replica-set-target.md).

### Initial sync preparation

Before starting the initial sync, {{pcsm.short}} checks which collections are sharded on the source cluster and creates corresponding sharded collections on the target sharded cluster. The only sharding configuration preserved from the source cluster is the sharding key. All other sharding details are handled internally by the target sharded cluster.

### Balancer operation

{{pcsm.full_name}} connects to the sharded source through a `mongos` instance. When the target is also sharded, {{pcsm.full_name}} connects to it through `mongos`. You do not need to disable the balancer on either sharded cluster before starting replication. The target balancer continues to operate normally and manages chunk distribution according to the target cluster's sharding configuration and balancer settings.

For ranged shard keys, PCSM prepares the target using the source chunk boundaries before the clone begins. Chunk migrations, splits, and merges that occur later are not replicated between the clusters. Each cluster continues to manage its own chunk layout. See [Manage sharded cluster balancer :octicons-link-external-16:](https://www.mongodb.com/docs/manual/tutorial/manage-sharded-cluster-balancer/){:target="_blank"} in the MongoDB documentation.

## Chunk distribution

!!! admonition "Version added: 1.0.0"

During the initial sync, {{pcsm.short}} prepares the chunk distribution of a sharded collection before copying its documents. This happens automatically for every sharded collection, immediately after the collection is sharded on the target. There is no flag and nothing to configure.

For an empty collection with a ranged shard key, MongoDB initially creates a single chunk that covers the full shard key range. If the clone starts with this layout, writes can be concentrated on one shard and the target balancer may need to redistribute the data later. See [Data partitioning with chunks :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/sharding-data-partitioning/){:target="_blank"} in the MongoDB documentation.

To avoid this, {{pcsm.short}} recreates the source chunk boundaries on the target before copying the data. How those chunks are placed depends on whether the source and target have the same number of shards.

Collections with a hashed shard key use the initial chunk layout created by MongoDB. See [Hashed shard keys](#hashed-shard-keys).

!!! note
    {{pcsm.short}} uses the source chunk layout to prepare the target before the clone. It does not keep the chunk layouts on the two clusters synchronized. Chunk migrations, splits, or merges that happen later on the source are not reproduced on the target. The layouts can therefore change independently as each cluster's balancer runs. This is expected and does not indicate a replication problem. See [Balancer operation](#balancer-operation).

### Same number of shards

For a source collection with more than one chunk, if the source and target have the same number of shards, {{pcsm.short}} sorts the shard IDs in each cluster and pairs them by their position in the sorted lists. For example, the first source shard is paired with the first target shard, the second source shard with the second target shard, and so on.
 
PCSM then recreates each source chunk boundary on the target and places the corresponding target chunk on the shard paired with the source shard that owns that chunk.

??? example "Same number of shards"

    ```{.text .no-copy}
    Source shards: src-a, src-b
    Target shards: tgt-a, tgt-b

    Source layout:
    [-∞, 100)  -> src-a
    [100, +∞)  -> src-b
    ```

For migrations between sharded clusters, {{pcsm.short}} prepares the target chunk layout before cloning data. For ranged shard keys, it uses source chunk boundaries to pre-split the target. Collections with a hashed shard key keep the initial layout created by MongoDB.

The target cluster's balancer continues to manage chunk placement. This means chunk distribution may still differ between source and target after replication, which is expected behavior.

## Usage

The commands and API endpoints for sharded cluster replication are the same as for replica set replication. The workflow follows the same stages as replica set replication. See [How {{pcsm.full_name}} works](intro.md#replication-workflows) for the complete workflow overview and [Use {{pcsm.full_name}}](install/usage.md) for detailed command instructions.

## Next steps

* [Install {{pcsm.full_name}}](installation.md)
* [Configure authentication](install/authentication.md)
* [Start replication](install/usage.md)
* [Monitor replication status](install/usage.md#check-the-replication-status)
* [Monitor PCSM performance with Percona Monitoring and Management](pmm-setup.md)