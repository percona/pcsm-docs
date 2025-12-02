# Sharding support in PCSM

Percona ClusterSync for MongoDB (PCSM) supports replication between sharded MongoDB clusters, enabling you to migrate or synchronize data from one sharded deployment to another. This ability allows you to:

* offload manual operations to PCSM, letting it migrate sharded clusters with minimal downtime, 
* maintain disaster recovery setups across sharded environments, 
* synchronize data between sharded clusters for testing or development purposes.

## How it works

When replicating between sharded clusters, PCSM connects to `mongos` instances on both the source and target clusters. Install and configure PCSM closer to the target cluster to minimize network latency and improve replication performance.

When you start replication, PCSM performs the following steps:

1. **Collection analysis and creation**: PCSM analyzes collections on the source cluster and creates the same collections on the target cluster. If a collection already exists on the target, it will be dropped and overwritten with data from the source.

2. **Initial data clone**: PCSM clones all data from the source to the target cluster. After the initial data clone completes, PCSM recreates indexes on the target to match the source.

3. **Real-time replication**: During the replication stage, PCSM captures change stream events from the source cluster and applies them to the target cluster, ensuring real-time synchronization of data changes.

4. **Finalization**: When you no longer need replication, you finalize the process to complete the migration.

## Supported features

PCSM supports the following capabilities for sharded cluster replication:

* **Sharded to sharded migration**: Replicate data between two sharded MongoDB clusters
* **Filtered replication**: Replicate specific databases or collections using include/exclude filters
* **No load balancer downtime**: You do not need to disable load balancers on either the source or target cluster before starting replication
* **Flexible shard configuration**: The number of shards on the source and target clusters can differ

## Implementation specifics

Sharding is supported with a single PCSM instance. Support for multiple PCSM instances is planned in future releases.

## Known limitations

PCSM does not save chunk distribution information during replication. The target cluster manages chunk distribution according to its own sharding configuration and balancer settings.

