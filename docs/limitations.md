---
title: Known issues and limitations
author: Radoslaw Szulgo
---
# Known issues and limitations

This page lists known limitations for using {{pcsm.full_name}}.

## Versions and topology

* MongoDB versions that reached End-of-Life are not supported
* {{pcsm.short}} connects only to the primary node in the replica set. You cannot force connection to secondary members using the [directConnection :octicons-link-external-16:](https://www.mongodb.com/docs/manual/reference/connection-string/#connection-string-formats) option. This option is ignored.

## Sharded clusters

The following limitations apply specifically to sharded cluster replication:

* {{pcsm.short}} replicates the data and doesn't replicate metadata. This means that the following information is not preserved from the source cluster:

   * The primary shard name for a collection. The target cluster may have a different primary shard name.
   * The chunk distribution information. The target cluster manages chunk distribution according to its own sharding configuration. See [Sharding support](sharding.md#limitations) for more information.
  * The configuration of [zones for sharded data :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/zone-sharding/).

* During data replication, the following commands are not supported: `movePrimary`, `reshardCollecton`, `unshardCollection`, `refineCollectionShardKey`. Running them results in failed replication and you must start it anew, from the initial data sync stage.

## Data types

* Queryable encryption is not supported
* Users and roles are not synchronized
* Timeseries collections are not supported
* `system.*` collections are not replicated
* [Clustered collections :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/clustered-collections/) with indexes that have the `expireAfterSeconds` field defined are not supported because the change stream does not provide a Time-to-Live (TTL) value for the index
* Capped collections created or converted as the result of `cloneCollectionAsCapped` and `convertToCapped` commands are not supported. These operations don't change the event and are not captured by the change streams.
* [Percona Memory Engine :octicons-link-external-16:](https://docs.percona.com/percona-server-for-mongodb/8.0/inmemory.html) is not supported
* Persistent Query Settings (added in MongoDB 8) are not supported 
* Documents that have [field names with periods and dollar signs :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/dot-dollar-considerations/) are not supported

## Other

The following functionalities are not supported:

* Multiple source or multiple target clusters 
* You cannot resume initial synchronization if an issue occurred. You must start it from scratch.
* Database upgrade during the sync, even in the paused state.
* Reverse synchronization
* External authentication via Kerberos, AWS and LDAP
* [GridFS :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/gridfs/)
