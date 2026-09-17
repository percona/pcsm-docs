# Sharding support in {{pcsm.full_name}} (Technical Preview)

!!! warning "Technical Preview"

    Sharding support is available starting with {{pcsm.full_name}} 0.7.0 and is currently in technical preview stage. We encourage you to try it out and share your feedback. This will help us improve the feature in future releases.

{{pcsm.full_name}} supports replication from a sharded MongoDB cluster to another sharded cluster or to a replica set. 

With a sharded target, you can migrate or synchronize data between sharded deployments with minimal downtime. With a replica set target, {{pcsm.full_name}} copies the data and skips the source sharding configuration.

For details about using a replica set as the target, see [Replicate from a sharded cluster to a replica set](sharded-source-to-replica-set-target.md).

## Overview

The workflow for sharded clusters is similar to replica sets. See [How {{pcsm.full_name}} works](intro.md#replication-workflows) for the complete workflow overview. The key difference is the target topology: when the target is a sharded cluster, {{pcsm.short}} connects through `mongos` on both the source and target. When the target is a replica set, it connects through the source `mongos` and then the target replica set members instead of a target `mongos`.

In both cases, the source must be a sharded MongoDB deployment. When the target is a sharded cluster, the source and target can have different numbers of shards. A replica set target does not require a target `mongos` instance.

Also, {{pcsm.short}} replicates data and not metadata. This means chunk distribution as well as the primary shard name for a collection may differ on source and target clusters.

## Prerequisites

* If the target is a sharded MongoDB deployment, {{pcsm.full_name}} version 0.7.0 or later.
* If the target is a replica set, {{pcsm.full_name}} version 0.10.0 or later.
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

### Chunk distribution

For ranged shard keys, {{pcsm.short}} uses the source chunk boundaries to pre-split a sharded target before the clone begins. Collections with a hashed shard key keep the layout MongoDB creates. From there each cluster's balancer manages its own placement, so the layouts can differ.

The target sharded cluster already knows which collections are sharded and manages their chunk distribution. {{pcsm.short}} does not interfere with the target cluster's sharding configuration or chunk distribution.

## Usage

The commands and API endpoints for sharded cluster replication are the same as for replica set replication. The workflow follows the same stages as replica set replication. See [How {{pcsm.full_name}} works](intro.md#replication-workflows) for the complete workflow overview and [Use {{pcsm.full_name}}](install/usage.md) for detailed command instructions.

## Next steps

* [Install {{pcsm.full_name}}](installation.md)
* [Configure authentication](install/authentication.md)
* [Start replication](install/usage.md)
* [Monitor replication status](install/usage.md#check-the-replication-status)
* [Monitor PCSM performance with Percona Monitoring and Management](pmm-setup.md)
