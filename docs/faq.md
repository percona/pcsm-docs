# FAQ

## What are the typical use cases for {{pcsm.full_name}}?

{{pcsm.full_name}} is a data migration tool that you can use for various use cases. Among them are:

- Migration from MongoDB Atlas or MongoDB Enterprise to Percona Server for MongoDB.
- Cluster synchronization across environments, such as staging to production.
- Setup of live replication for backup, testing, or audit environments.
- Downtime minimization during a migration by using continuous sync until cutover.

## Which MongoDB versions are supported?

- Source clusters: MongoDB 6.0.17 and later, including Atlas, MongoDB Enterprise Server, and Percona Server for MongoDB
- Target clusters: Percona Server for MongoDB 6.0.17 and later.

!!! note
    PCSM supports MongoDB 6.0.17+, 7.0.13+, 8.0.0+, but the source and target must be on the same major version during sync.

Check [Supported deployments](deployment.md) to learn more.

## Can I sync from Atlas to a self-hosted Percona Server for MongoDB?

Yes. {{pcsm.full_name}} is explicitly built to support Atlas to Percona Server for MongoDB migrations with minimal effort.

## Does {{pcsm.full_name}} require a replica set on the source or target?

Yes. Both the source and target must be replica sets. 

## Does {{pcsm.full_name}} support sharded clusters?

Yes. Sharded MongoDB clusters are supported as both sources and targets. Note: this feature is currently in technical preview. Support for shard-to-shard replication is planned for a future release.

## Does {{pcsm.full_name}} support bidirectional sync?

No. {{pcsm.full_name}} currently supports one-way synchronization only (source → target). However, you can rerun Percona {{pcsm.full_name}} with reversed connection strings to perform the other-direction sync.

## Is there a way to monitor sync progress?

Yes. {{pcsm.full_name}} provides Prometheus metrics exposed at the `/metrics` endpoint and provides detailed logging for sync status, lag, and errors. See how you can [configure monitoring with PMM](pmm-setup.md). You can also use a monitoring tool of your choice.

## Can I filter which databases or collections to sync?

Yes. {{pcsm.full_name}} allows you to include/exclude filters for specific databases or collections. You can do it both via the API and using the CLI. To learn more, see [PCSM usage](install/usage.md#start-the-filtered-replication).

## How does {{pcsm.full_name}} handle failures?

{{pcsm.full_name}} is designed with resilience in mind:

- It supports automatic retries on transient errors.
- It uses checkpointing to resume from the last known sync point after a restart.
- Logs include detailed error reporting for troubleshooting.

## What database read and write concerns are used?
By default, Percona ClusterSync for MongoDB uses the `"majority"` read concern level for reads on the source cluster. For writes to the destination cluster, the tool uses a write concern level of `"majority"` with `j: true`.




## What features are planned for future releases?

 We're currently working on high availability with multiple PCSM instances and shard-to-shard replication.   
