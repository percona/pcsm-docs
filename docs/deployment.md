# Supported MongoDB deployments

{{pcsm.full_name}} supports the following deployment topologies:

* **Replica Set to Replica Set**: The source and target replica sets can have different numbers of nodes.
* **Sharded cluster to Sharded cluster**: The source and target sharded clusters can have different numbers of shards. This functionality is in tech preview stage. See [Sharding support in {{pcsm.full_name}}](sharding.md) for details.

## Version requirements

* You can synchronize from Percona Server for MongoDB, MongoDB Community, MongoDB Enterprise Advanced, or MongoDB Atlas source clusters to a Percona Server for MongoDB target cluster when both run the same major version (e.g., 6.0 to 6.0, 7.0 to 7.0, or 8.0 to 8.0).
* {{pcsm.short}} supports selected cross-version replication paths (e.g., 6.0 to 7.0, 6.0 to 8.0, and 7.0 to 8.0). See [Cross-version replication](version-compatibility.md) and [limitations](limitations.md#cross-version-replication).
* Minimal supported MongoDB versions are: 6.0.17, 7.0.13, 8.0.0

## Supported architectures

* {{pcsm.full_name}} is supported on both ARM64 and x86_64 architectures.

## Supported MongoDB deployments

You can connect the following MongoDB deployments:

   | Source | Target |
   | --- | --- |
   | Percona Server for MongoDB | Percona Server for MongoDB |
   | MongoDB Community | Percona Server for MongoDB |
   | MongoDB Enterprise Advanced | Percona Server for MongoDB |
   | MongoDB Atlas | Percona Server for MongoDB |
