# System requirements

* At least 1GB RAM is required to operate successfully.
* At least 2 logical CPU cores are recommended to reduce the 100% CPU saturation risk during the synchronization period
* {{plm.short}} process must be able to connect to all replica set nodes that could become a new primary. In non-sharded replica set deployments, this means connecting to all the nodes that could become a new primary node. To become a primary, a node must meet the following criteria:

    * have `priority` greater than `0` and must be able to vote (`votes`: 1)
    * is not an arbiter (`arbiterOnly: false`)
    * is not hidden (`hidden: false`)
    * is not delayed 

Note that networking issues like connection to the remote backup storage can also affect {{plm.short}} performance. 
