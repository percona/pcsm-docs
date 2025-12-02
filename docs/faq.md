# FAQ

## What are the typical use cases for {{plm.full_name}}?

{{plm.full_name}} is a data migration tool that you can use for various use cases. Among them are:

- Migration from MongoDB Atlas or MongoDB Enterprise to Percona Server for MongoDB.
- Cluster synchronization across environments, such as staging to production.
- Setup of live replication for backup, testing, or audit environments.
- Downtime minimization during a migration by using continuous sync until cutover.

## Which MongoDB versions are supported?

- Source clusters: MongoDB 6.0.17 and later, including Atlas and MongoDB Enterprise editions.
- Target clusters: Percona Server for MongoDB 6.0.17 and later.

Check [Supported deployments](deployment.md) to learn more.

## Can I sync from Atlas to a self-hosted Percona Server for MongoDB?

Yes. {{plm.full_name}} is explicitly built to support Atlas to Percona Software migrations with minimal effort.

## Does {{plm.full_name}} require a replica set on the source or target?

Yes. Both the source and target must be replica sets. Sharded clusters are not yet supported, but planned.

## Does {{plm.full_name}} support bidirectional sync?

No. {{plm.full_name}} currently supports one-way synchronization only (source → target). However, you can re-run Percona {{plm.full_name}} with a reversed connection strings to do the other direction sync.

## Is there a way to monitor sync progress?

Yes. {{plm.full_name}} provides Prometheus metrics exposed at the `/metrics` endpoint and provides detailed logging for sync status, lag, and errors. See how you can [configure monitoring with PMM](pmm-setup.md). You can also use a monitoring tool of your choice.

## Can I filter which databases or collections to sync?

Yes. {{plm.full_name}} allows you to include/exclude filters for specific databases or collections. You can do it both via the API and using the CLI. To learn more, see [PLM usage](install/usage.md#start-the-filtered-replication).

## How does {{plm.full_name}} handle failures?

{{plm.full_name}} is designed with resilience in mind:

- It supports automatic retries on transient errors.
- It uses checkpointing to resume from the last known sync point after restart.
- Logs include detailed error reporting for troubleshooting.

## What features are planned for future releases?

Sharded cluster support and high availability are the next features we are working on.   
