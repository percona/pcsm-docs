# Sharding support in {{pcsm.full_name}}

{{pcsm.full_name}} supports replication between sharded MongoDB clusters, enabling you to migrate or synchronize data from one sharded deployment to another. This capability allows you to migrate sharded clusters with minimal downtime and synchronize data between sharded clusters for testing or development purposes.

## Overview

The workflow for sharded clusters is similar to replica sets. See [How {{pcsm.full_name}} works](intro.md#replication-workflows) for the complete workflow overview. The key difference is that {{pcsm.short}} connects to `mongos` instances on both the source and target clusters instead of replica set members.

Since {{pcsm.short}} connects through `mongos`, the cluster topology doesn't matter. This means the source and target clusters can have different numbers of shards.

Also, {{pcsm.short}} replicates data and not metadata. This means chunk distribution as well as the primary shard name for a collection may differ on source and target clusters.

## Prerequisites

* {{pcsm.full_name}} version 0.7.0 or later
* Source and target clusters must be sharded MongoDB deployments
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

Before starting the initial sync, {{pcsm.short}} checks which collections are sharded on the source cluster and creates corresponding sharded collections on the destination cluster. The only sharding configuration preserved from the source cluster is the sharding key; all other sharding details are handled internally by the destination cluster.

### Balancer operation

{{pcsm.full_name}} connects to source and target clusters via a `mongos` instance. Therefore, you do not need to disable the balancer on either the source or target cluster before starting replication. The target cluster's balancer continues to operate normally and manages chunk distribution according to its own sharding configuration and balancer settings.

### Chunk distribution

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
