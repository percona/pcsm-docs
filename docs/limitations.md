---
title: Known issues and limitations
author: Radoslaw Szulgo
---
# Known issues and limitations

This page lists known limitations for using {{pcsm.full_name}} (PCSM).

## Versions and topology

* MongoDB versions that reached End-of-Life are not supported
* {{pcsm.short}} connects only to the primary node in the replica set. You cannot force connection to secondary members using the [directConnection :octicons-link-external-16:](https://www.mongodb.com/docs/manual/reference/connection-string/#connection-string-formats) option. This option is ignored.

## Cross-version replication

- **Feature Compatibility Version (FCV) is not automatically checked between your source and target clusters**

    PCSM does not automatically check the Feature Compatibility Version (FCV) between your source and target clusters. Because an incompatible FCV might cause replication failures, it is important to perform this check manually before you begin:

    Confirm the FCV for both your source and target clusters.
    Ensure the target cluster's FCV is equal to or higher than the source cluster's FCV.

- **Downgrade replication is not supported**

    PCSM blocks startup if the source major version is higher than the target major version.

## Sharded clusters

The following limitations apply specifically to sharded cluster replication:

* When both the source and target are sharded clusters, {{pcsm.short}} does not continuously replicate sharding metadata. For ranged shard keys, PCSM uses the source chunk boundaries to initialize the target during the initial sync. Subsequent chunk migrations, splits, and merges aren't reproduced on the target.
* The primary shard assignment is not preserved. The target cluster can use a different primary shard.
* Zone configuration is not replicated. See [Zones for sharded data :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/zone-sharding/).
* Don't reshard a collection during an active synchronization.
  Running `reshardCollection`, `unshardCollection`, or `refineCollectionShardKey` on a collection included in an active synchronization puts PCSM into a failure state. Complete or stop the synchronization first.
* Replica set to sharded cluster migrations do not apply a shard key. PCSM can copy data from a replica set source to a sharded cluster target, but the migrated collections remain unsharded. If you need sharded collections on the target, apply the required shard key separately.

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

The following limitations apply:

* You cannot resume the clone phase after it fails. Resolve the issue and start a new synchronization run from the beginning.
* Arbitrary database upgrades during a sync are not supported. For supported staged upgrades from lower to higher MongoDB major versions, follow the cross-version replication procedure.
* Reverse synchronization, from the target cluster back to the source, is not supported.
* External authentication through Kerberos, LDAP, and AWS IAM is not supported.
