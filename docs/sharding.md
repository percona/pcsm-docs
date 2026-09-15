# Sharding support in {{pcsm.full_name}} (Technical Preview)

!!! warning "Technical Preview"

    Sharding support is available starting with {{pcsm.full_name}} 0.7.0 and is currently in technical preview stage. We encourage you to try it out and share your feedback. This will help us improve the feature in future releases.

{{pcsm.full_name}} supports replication between sharded MongoDB clusters. You can use it to migrate data from one sharded deployment to another with minimal downtime, or to keep data synchronized for testing and development.

## Overview

The replication workflow for sharded clusters is similar to the workflow for replica sets. See [How {{pcsm.full_name}} works](intro.md#replication-workflows) for an overview of the replication stages.

For sharded deployments, {{pcsm.short}} connects to `mongos` on both the source and target clusters instead of connecting directly to individual shard members. The source and target can have different numbers of shards.

{{pcsm.short}} does not continuously replicate sharding metadata. For collections with a ranged shard key, it uses the source chunk boundaries to prepare the target before the initial clone begins. Changes to the chunk layout that occur later on the source are not replicated to the target.

The primary shard assignment can also differ between the source and target clusters. See [Chunk distribution](#chunk-distribution).

## Prerequisites

* If the target is a sharded MongoDB deployment, use {{pcsm.full_name}} 0.7.0 or later.
* If the target is a replica set, use {{pcsm.full_name}} 0.10.0 or later.
* The source must be a sharded MongoDB deployment.
* Both clusters must be running the same MongoDB version. Check [Version requirements](deployment.md#version-requirements) for more information about supported versions.

## Connection string format

When connecting to sharded clusters, use the standard MongoDB connection string format but specify `mongos` hostname and port instead of replica set members:

```{.text .no-copy}
mongodb://user:pwd@mongos-host:port/[authdb]?[options]
```

Since {{pcsm.short}} connects through `mongos`, you don't need to specify individual shard members or config servers in the connection string. The `mongos` router handles routing to the appropriate shards.

For detailed information about authentication and connection string configuration, see [Configure authentication in MongoDB](install/authentication.md).

## Sharding-specific behavior

### Initial sync preparation

For collections with a ranged shard key, {{pcsm.short}} uses the source chunk boundaries to pre-split the collection on the target before copying any documents. If the source and target have the same number of shards, PCSM preserves the source chunk ownership pattern. If the shard counts differ, PCSM uses the source boundaries and determines the chunk placement across the available target shards.

Collections with a hashed shard key keep the initial chunk layout created by MongoDB when shardCollection runs on the target.

{{pcsm.short}} does not continuously replicate sharding metadata after the initial preparation. See [Chunk distribution](#chunk-distribution).

### Replica set source to sharded target

PCSM replicates data from a replica set source to a sharded cluster target, but it does not shard anything on the way in. Collections arrive on the target as unsharded collections on the primary shard, exactly as they existed on the source.

There is no warning about this while it happens. The run completes normally, `pcsm status` reports success, and the logs show nothing unusual. The only way to notice is to check the collections on the target afterwards.

!!! warning

    If you are moving to a sharded cluster in order to distribute a large collection, this migration alone does not get you there. Shard the collections yourself on the target once replication is finalized, using [sh.shardCollection() :octicons-link-external-16:](https://www.mongodb.com/docs/manual/reference/method/sh.shardCollection/){:target="_blank"}.

    Sharding a collection that already holds data means the balancer has to redistribute it afterwards, which takes time and I/O on a cluster you have just finished filling. Factor that into your cutover plan rather than discovering it on the day.

### Balancer operation

{{pcsm.full_name}} connects to source and target clusters via a `mongos` instance. Therefore, you do not need to disable the balancer on either the source or target cluster before starting replication. The target cluster's balancer continues to operate normally and manages chunk distribution according to its own sharding configuration and balancer settings.

For ranged shard keys, PCSM prepares the target using the source chunk boundaries before the clone begins. Chunk migrations, splits, and merges that occur later are not replicated between the clusters. Each cluster continues to manage its own chunk layout. See [Manage sharded cluster balancer :octicons-link-external-16:](https://www.mongodb.com/docs/manual/tutorial/manage-sharded-cluster-balancer/){:target="_blank"} in the MongoDB documentation.

### If the pre-split fails

If {{pcsm.short}} cannot prepare the chunk layout on the target, the initial sync fails. PCSM does not fall back to copying the data into an unsplit collection.

Check the PCSM logs and resolve the reported problem on the target. Then start a new synchronization run from the initial sync stage.

## Chunk distribution

!!! admonition "Version added: 0.10.0"

During the initial sync, {{pcsm.short}} prepares the chunk distribution of a sharded collection before copying its documents. This happens automatically for every sharded collection, immediately after the collection is sharded on the target. There is no flag and nothing to configure.

For an empty collection with a ranged shard key, MongoDB initially creates a single chunk that covers the full shard key range. If the clone starts with this layout, writes can be concentrated on one shard and the target balancer may need to redistribute the data later. See [Data partitioning with chunks :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/sharding-data-partitioning/){:target="_blank"} in the MongoDB documentation.

To avoid this, {{pcsm.short}} recreates the source chunk boundaries on the target before copying the data. How those chunks are placed depends on whether the source and target have the same number of shards.

Collections with a hashed shard key use the initial chunk layout created by MongoDB. See [Hashed shard keys](#hashed-shard-keys).

!!! note
    {{pcsm.short}} uses the source chunk layout to prepare the target before the clone. It does not keep the chunk layouts on the two clusters synchronized. Chunk migrations, splits, or merges that happen later on the source are not reproduced on the target. The layouts can therefore change independently as each cluster's balancer runs. This is expected and does not indicate a replication problem. See [Balancer operation](#balancer-operation).

### Same number of shards

When the source and target have the same number of shards, PCSM sorts the shard IDs in each cluster and pairs them by their position in the sorted lists. For example, the first source shard is paired with the first target shard, the second source shard with the second target shard, and so on. 

PCSM then recreates each source chunk boundary on the target and places the corresponding target chunk on the shard paired with the source shard that owns that chunk.

??? example "Same number of shards"

    ```{.text .no-copy}
    Source shards: src-a, src-b
    Target shards: tgt-a, tgt-b

    Source layout:
    [-∞, 100)  -> src-a
    [100, +∞)  -> src-b

    Target layout:
    [-∞, 100)  -> tgt-a
    [100, +∞)  -> tgt-b
    ```
    In this example, `src-a` is paired with `tgt-a` and `src-b` with `tgt-b`. The target keeps the same chunk boundaries and ownership pattern as the source.

### Different number of shards

When the source and target have different numbers of shards, the source chunk ownership cannot be mapped one-to-one to the target. 

Instead, {{pcsm.short}} estimates the size of each source chunk and processes the largest chunks first. It places each chunk on the target shard that currently has the smallest estimated amount of assigned data.

{{pcsm.short}} keeps track of the estimated total for each target shard as it assigns chunks. It then recreates the source chunk boundaries on the target using the calculated placement.

??? example "Different number of shards"

    ```{.text .no-copy}
    Target shards: tgt-a, tgt-b
    Source chunk sizes: 100 MB, 60 MB, 40 MB

    100 MB -> tgt-a
    60 MB -> tgt-b
    40 MB -> tgt-b

    Final estimated placement:
    tgt-a: 100 MB
    tgt-b: 100 MB
    ```
    Here, the 100 MB chunk is placed on `tgt-a` first. The 60 MB chunk goes to `tgt-b`, which has no data assigned yet. When the 40 MB chunk is processed, `tgt-b` still has less estimated data than `tgt-a`, so the chunk is also placed there.

### Hashed shard keys

{{pcsm.short}} does not pre-split hashed collections. MongoDB already spreads the initial chunks evenly across the shards for a hashed shard key, so {{pcsm.short}} keeps that layout. See [Hashed sharding :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/hashed-sharding/){:target="_blank"} in the MongoDB documentation.

### If the pre-split fails

If {{pcsm.short}} cannot prepare the chunk layout on the target, the clone fails. It does not fall back to copying the data into an unsplit collection.

Check the PCSM logs for the reported error and resolve the issue on the target cluster. Then resume replication:

```sh
pcsm resume --from-failure
```
See [Resume the replication](install/usage.md#resume-the-replication), [Logging in {{pcsm.full_name}}](logging.md), and the [Troubleshooting guide](troubleshooting.md).

### Check the chunk distribution

To check how a replicated collection is distributed, connect to the target mongos and run:

```javascript
db.getSiblingDB('<database>').getCollection('<collection>').getShardDistribution()
```

The command shows the data distribution across the target shards.

## Usage

The commands and API endpoints for sharded cluster replication are the same as for replica set replication. The workflow follows the same stages as replica set replication. See [How {{pcsm.full_name}} works](intro.md#replication-workflows) for the complete workflow overview and [Use {{pcsm.full_name}}](install/usage.md) for detailed command instructions.

## Next steps

* [Install {{pcsm.full_name}}](installation.md)
* [Configure authentication](install/authentication.md)
* [Start replication](install/usage.md)
* [Monitor replication status](install/usage.md#check-the-replication-status)
* [Monitor PCSM performance with Percona Monitoring and Management](pmm-setup.md)
