# Sharding support in {{pcsm.full_name}}

{{pcsm.full_name}} supports replication between sharded MongoDB clusters. You can use it to migrate data from one sharded deployment to another with minimal downtime, or to keep data synchronized for testing and development.

## Overview

The replication workflow for sharded clusters is similar to the workflow for replica sets. See [How {{pcsm.full_name}} works](intro.md#replication-workflows) for an overview of the replication stages.

For a sharded source, {{pcsm.short}} connects to `mongos` instead of connecting directly to individual shard members. When the target is also sharded, {{pcsm.short}} connects to the target `mongos` as well. The source and target can have different numbers of shards.

{{pcsm.short}} does not continuously replicate sharding metadata. By default, for collections with a ranged shard key, it uses the source chunk boundaries to prepare the target before the initial clone begins. You can [skip pre-splitting](#skip-pre-splitting) to keep the initial chunk layout created by MongoDB on the target. Changes to the chunk layout that occur later on the source are not replicated to the target.

The primary shard assignment can also differ between the source and target clusters.

## Prerequisites

* If the target is a sharded MongoDB deployment, {{pcsm.full_name}} version 0.7.0 or later.
* If the target is a replica set, {{pcsm.full_name}} version 1.0.0 or later.
* The source must be a sharded MongoDB deployment.
* The target can be either a sharded MongoDB deployment or a replica set.
* The source and target clusters must use a supported version combination. See [Cross-version replication](version-compatibility.md) for supported source and target versions.

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

During the initial sync, {{pcsm.short}} checks which collections are sharded on the source cluster and shards the corresponding collections on the target with the same shard key before copying their documents.

By default, for collections with a ranged shard key, {{pcsm.short}} uses the source chunk boundaries to pre-split the collection on the target before copying any documents. If the source and target have the same number of shards, PCSM preserves the source chunk ownership pattern. If the shard counts differ, PCSM uses the source boundaries and determines the chunk placement across the available target shards.

Collections with a hashed shard key keep the initial chunk layout created by MongoDB when `shardCollection` runs on the target.

{{pcsm.short}} does not continuously replicate sharding metadata after the initial preparation. See [Chunk distribution](#chunk-distribution).

### Balancer operation

{{pcsm.full_name}} connects to the sharded source through a `mongos` instance. When the target is also sharded, {{pcsm.full_name}} connects to it through `mongos`. You do not need to disable the balancer on either sharded cluster before starting replication. The target balancer continues to operate normally and manages chunk distribution according to the target cluster's sharding configuration and balancer settings.

By default, for collections that use ranged sharding, {{pcsm.short}} pre-splits each collection on the target using the source chunk boundaries before the clone begins. After that, chunk migrations, splits, and merges aren't replicated between the clusters, and each cluster manages its own chunk layout. To learn how MongoDB balances chunks across shards, see [Manage sharded cluster balancer :octicons-link-external-16:](https://www.mongodb.com/docs/manual/tutorial/manage-sharded-cluster-balancer/){:target="_blank"} in the MongoDB documentation.

### If the pre-split fails

If {{pcsm.short}} cannot prepare the chunk layout for a collection, it logs a warning such as `Pre-split of "<database>.<collection>" failed, keeping the native chunk layout` and continues the clone. The collection keeps the layout it has on the target at that point, which can be partially split. The target balancer can redistribute data according to its configuration and balancing thresholds. The initial sync doesn't fail because of it.

## Chunk distribution

!!! admonition "Version added: 1.0.0"

During the initial sync, {{pcsm.short}} prepares the chunk distribution of each sharded collection before copying its documents. For collections that use ranged sharding, pre-splitting runs right after {{pcsm.short}} shards the collection on the target. Starting with version 1.1.0, you can [skip pre-splitting](#skip-pre-splitting).

For an empty collection with a ranged shard key, MongoDB initially creates a single chunk that covers the full shard key range. If the clone starts with this layout, writes can be concentrated on one shard and the target balancer may need to redistribute the data later. See [Data partitioning with chunks :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/sharding-data-partitioning/){:target="_blank"} in the MongoDB documentation.

To avoid this, {{pcsm.short}} recreates the source chunk boundaries on the target before copying the data. How those chunks are placed depends on whether the source and target have the same number of shards.

Collections with a hashed shard key use the initial chunk layout created by MongoDB. See [Hashed shard keys](#hashed-shard-keys).

!!! note
    {{pcsm.short}} uses the source chunk layout to prepare the target before the clone. It does not keep the chunk layouts on the two clusters synchronized. Chunk migrations, splits, or merges that happen later on the source are not reproduced on the target. The layouts can therefore change independently as each cluster's balancer runs. This is expected and does not indicate a replication problem. See [Balancer operation](#balancer-operation).

### Skip pre-splitting

!!! admonition "Version added: 1.1.0"

If the source has an uneven chunk distribution that you do not want to copy, you can skip pre-splitting on the target. {{pcsm.short}} still shards each target collection with the source shard key, but keeps the initial chunk layout created by MongoDB. The target balancer manages distribution according to its configuration and balancing thresholds.

Use one of the following options when [starting replication](install/usage.md#start-the-replication):

=== "Command line"

    ```{.bash data-prompt="$"}
    $ pcsm start --clone-skip-presplit
    ```

=== "HTTP API"

    ```{.bash data-prompt="$"}
    $ curl -X POST http://localhost:2242/start \
        -H "Content-Type: application/json" \
        --data '{"cloneSkipPresplit": true}'
    ```

=== "Environment variable"

    ```{.bash data-prompt="$"}
    $ export PCSM_CLONE_SKIP_PRESPLIT=true
    $ pcsm start
    ```

The default is `false`, so pre-splitting stays enabled unless you skip it. To keep pre-splitting for a single run when `PCSM_CLONE_SKIP_PRESPLIT` is `true`, use `pcsm start --clone-skip-presplit=false` or set `cloneSkipPresplit` to `false` in the `/start` request.

!!! note
    Skipping pre-splitting doesn't guarantee that data is evenly distributed across shards during the initial clone. At first, writes can concentrate on a single shard while the balancer redistributes the data. For details, see [Data partitioning with chunks :octicons-link-external-16:](https://www.mongodb.com/docs/v8.0/core/sharding-data-partitioning/){:target="_blank"} in the MongoDB documentation and [Balancer operation](#balancer-operation). 
    
    Collections with [hashed shard keys](#hashed-shard-keys) already use the initial chunk layout that MongoDB creates, so this option doesn't change how they're distributed.

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

    Target layout:
    [-∞, 100)  -> tgt-a
    [100, +∞)  -> tgt-b
    ```
    In this example, `src-a` is paired with `tgt-a` and `src-b` with `tgt-b`. The target keeps the same chunk boundaries and ownership pattern as the source.

### Different number of shards

For a source collection with more than one chunk, if the source and target have different numbers of shards, {{pcsm.short}} cannot map source chunk ownership directly to the target.

Instead, {{pcsm.short}} estimates the size of each source chunk and processes the largest chunks first. It places each chunk on the target shard that currently has the smallest estimated amount of assigned data. Chunks with no estimated data go to the target shard with the fewest assigned chunks.

{{pcsm.short}} keeps track of the estimated total for each target shard as it assigns chunks, and those totals carry across every collection in the run. It then recreates the source chunk boundaries on the target using the calculated placement.

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

{{pcsm.short}} does not pre-split a collection whose shard key contains a hashed field. The target keeps the initial chunk layout MongoDB creates when `shardCollection` runs, and the target balancer manages it from there.

### Check the chunk distribution

To check how a replicated collection is distributed, connect to the target `mongos` and run:

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
