# System requirements

* At least 1GB RAM is required to operate successfully.
* At least 2 logical CPU cores are recommended to reduce the 100% CPU saturation risk during the synchronization period
* {{pcsm.short}} process must be able to connect to all replica set nodes that could become a new primary. In non-sharded replica set deployments, this means connecting to all the nodes that could become a new primary node. To become a primary, a node must meet the following criteria:

  * have `priority` greater than `0` and must be able to vote (`votes`: 1)
  * is not an arbiter (`arbiterOnly: false`)
  * is not hidden (`hidden: false`)
  * is not delayed 

## Docker requirements

When running {{plm.short}} in Docker:

* Ensure the Docker container has sufficient resources allocated (at least 1GB RAM and 2 CPU cores)
* The container must have network connectivity to all MongoDB cluster nodes (source and target)
* If MongoDB clusters also run in Docker, use Docker networks or host networking to ensure connectivity
* See the [Run {{pcsm.short}} in Docker](install/docker.md) guide for steps 
