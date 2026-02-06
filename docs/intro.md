# How {{pcsm.full_name}} works

{{pcsm.full_name}} is a binary process that replicates data between MongoDB deployments in real time until you manually finalize it. You can also make a one-time data migration from the source to the target with near-zero downtime.

You operate with {{pcsm.full_name}} using the [set of commands](pcsm-commands.md) or [API calls](api.md). Depending on the request it receives, {{pcsm.full_name}} has several states as shown in the following diagram:

![PCSM states](_images/state-transition-flow.jpg)

* **Idle**: {{pcsm.short}} is up and running but not migrating data
* **Running**: {{pcsm.short}} is replicating data from the source to the target. {{pcsm.short}} enters the running state when you start and resume the replication
* **Paused**: {{pcsm.short}} is not running and data is not replicated
* **Finalizing**: {{pcsm.short}} stops the replication and is doing final checks, creates indexes
* **Finalized**: all checks are complete, data replication is stopped
* **Failed**: {{pcsm.short}} encountered an error

## Replication workflows

The workflow for {{pcsm.short}} depends on your MongoDB deployment topology. Select the tab below that matches your setup:

=== "Replica Sets"

    ### Usage scenario

    Let's use a data migration from MongoDB Atlas to Percona Server for MongoDB as an example to understand how {{pcsm.short}} works with replica sets.

    You run a MongoDB Atlas 8.0 deployed as a replica set. You need to migrate to the latest 8.0 release of Percona Server for MongoDB, which also supports replica sets. You have a strict requirement to migrate with near-zero downtime; therefore, using logical backups with [Percona Backup for MongoDB :octicons-link-external-16:](https://docs.percona.com/percona-backup-mongodb/features/logical.html) is not an option.

    A solution is to use {{pcsm.full_name}}. MongoDB Atlas is your source. The target collections on the Percona Server for MongoDB replica set will be overwritten. Data migration is a resource-intensive task. Therefore, we recommend installing {{pcsm.short}} on a dedicated host closest to the target to reduce the network lag as much as possible.

    ### Workflow steps

    1. **Set up authentication**: Create users for {{pcsm.short}} in both MongoDB deployments. Start and connect {{pcsm.short}} to your source and target using these user credentials and the `mongos` hostname and port. See [Configure authentication in MongoDB](install/authentication.md) for details.

    2. **Start the replication**

        !!! info "Important"
            During the replication startup phase:

            - Only the collections selected for replication are dropped and recreated. 
            - Existing databases and collections on the target that are not part of the sync selection **remain untouched**.
        
        Call the `start` command. {{pcsm.short}} prepares the target collections and begins the replication process. For each selected collection, PCSM performs the following actions:
        { .power-number}

        1. **Drop collection on target**
        
            If the target collection already exists, {{pcsm.short}} drops it to ensure a clean state for incoming data.

        2. **Recreate collection**
        
            The collection is recreated on the target with the same options as the source (such as capped settings, collation, validators, and other collection-level options).

        3. **Create indexes**
            
            Indexes are created on the target to match those defined on the source collection.


        4. **Initial sync**
            
            {{pcsm.short}} copies the documents from the source collection to the target.
    

    See [Start the replication](install/usage.md#start-the-replication) for command details.
       
    3. **Real-time replication**: After the initial data sync, {{pcsm.short}} monitors changes in the source and replicates them to the target at runtime. You don't have to stop your source deployment—it operates as usual, accepting client requests. {{pcsm.short}} uses [change streams :octicons-link-external-16:](https://www.mongodb.com/docs/manual/changeStreams/) to track the changes to your data and replicate them to the target.

    4. **Control replication**: You can `pause` the replication and `resume` it later. When paused, {{pcsm.short}} saves the timestamp when it stops the replication. After you resume {{pcsm.short}}, it starts watching for the changes from the moment when the replication was paused and continues real-time replication. See [Pause the replication](install/usage.md#pause-the-replication) and [Resume the replication](install/usage.md#resume-the-replication) for command details.

    5. **Monitor progress**: Track the migration status in logs and using the `status` command. See [Check the replication status](install/usage.md#check-the-replication-status) for details.

    6. **Finalize**: When the data migration is complete, call the `finalize` command. This makes {{pcsm.short}} finalize the replication, create the required indexes on the target, and stop. Note that finalizing is a one-time operation. If you try to start {{pcsm.short}} again, it will start data copy anew. See [Finalize the replication](install/usage.md#finalize-the-replication) for command details.

    7. **Cutover**: Switch your clients to connect to Percona Server for MongoDB.

    For detailed instructions, see [Use {{pcsm.full_name}}](install/usage.md).

=== "Sharded Clusters (Tech Preview)"

    ### Usage scenario

    Let's use a data migration between two sharded MongoDB clusters as an example to understand how {{pcsm.short}} works with sharded clusters.

    For example, you run a MongoDB Enterprise Advanced 8.0 sharded cluster with 3 shards as your source. You need to migrate to a self-hosted Percona Server for MongoDB 8.0 sharded cluster with 5 shards as your target. You need zero-downtime migration and cannot afford to disable the balancer on either cluster, which makes traditional migration methods challenging.

    A solution is to use {{pcsm.full_name}}. Since {{pcsm.short}} connects to `mongos` instances, the number of shards on source and target can differ. Install {{pcsm.short}} on a dedicated host closer to the target cluster to minimize network latency.

    ### Workflow steps

    1. **Set up authentication**: Create users for {{pcsm.short}} in both MongoDB deployments. Configure connection strings using `mongos` hostname and port for both source and target clusters. See [Configure authentication in MongoDB](install/authentication.md) for details.

    2. **Apply sharding (if applicable)**
            
    If the source collection is sharded, {{pcsm.short}} shards the target collection using the same sharding configuration.

    3. **Start the replication**: 

        !!! info "Important"
            - During the replication startup phase:

            - Only the collections selected for replication are dropped and recreated. 
            - Existing databases and collections on the target that are not part of the sync selection **remain untouched**.
    
        Call the `start` command. You don't have to disable the balancer on the target. Before starting the data copying, {{pcsm.short}} retrieves the information about the shard keys for collections on the source cluster and creates these collections on the target with the same shard key. Then {{pcsm.short}} starts copying all data from the source to the target. First it does the initial sync by cloning the data and then applying all the changes that happened since the clone start. See [Start the replication](install/usage.md#start-the-replication) for command details.

    4. **Real-time replication**: During the replication stage, {{pcsm.short}} captures change stream events from the source cluster through `mongos` and applies them to the target cluster, ensuring real-time synchronization of data changes. The target cluster's balancer handles chunk distribution. For details about sharding-specific behavior, see [Sharding behavior](sharding.md#sharding-specific-behavior).

    5. **Control replication**: You can `pause` the replication and `resume` it later, just like with replica sets. When paused, {{pcsm.short}} saves the timestamp when it stops the replication. See [Pause the replication](install/usage.md#pause-the-replication) and [Resume the replication](install/usage.md#resume-the-replication) for command details.

    6. **Monitor progress**: Track the migration status in logs and using the `status` command. See [Check the replication status](install/usage.md#check-the-replication-status) for details.

    7. **Finalize**: When the data migration is complete and you no longer need to run clusters in sync, call the `finalize` command to complete the migration. This makes {{pcsm.short}} finalize the replication, create the required indexes on the target, and stop. Note that finalizing is a one-time operation. If you try to start {{pcsm.short}} again, it will start data copy anew. See [Finalize the replication](install/usage.md#finalize-the-replication) for command details.

    8. **Cutover**: Switch your clients to connect to the target Percona Server for MongoDB cluster.

    For detailed information about sharded cluster replication, see [Sharding support in {{pcsm.full_name}}](sharding.md).

## Filtered replication

You can replicate the whole data set or only a specific subset of data, which is a filtered replication. You can use filtered replication for various use cases, such as:

* Spin up a new development environment with a specific subset of data instead of the whole data set. 

* Optimize cloud storage costs for hybrid environments where your target MongoDB deployment runs in the cloud.

Specify what namespaces—databases and collections—to include and/or exclude from the replication when you start it. See [Start the filtered replication](install/usage.md#start-the-filtered-replication) for details.

## Index handling

{{pcsm.short}} manages indexes throughout the replication process to ensure data consistency and query performance on the target cluster.

### Replication stage 

During the replication stage, {{pcsm.short}} copies indexes from the source to the target cluster as follows:

* **Unique indexes handling**: Unique indexes are copied as non-unique indexes during replication. This allows {{pcsm.short}} to handle potential duplicate data that may exist during the migration process.

* **Hidden indexes**: {{pcsm.short}} copies hidden indexes as non-hidden. 

* **TTL index handling**: When copying TTL indexes, {{pcsm.short}} temporarily disables TTL expiration and saves the `expireAfterSeconds` property for later restoration. This way {{pcsm.short}} ensures documents won't expire while being copied.

* **Index creation during sync**: If an index is created on the source cluster while the clusters are in sync, {{pcsm.short}} automatically creates the same index on the target cluster.

* **Incomplete indexes**: If the index build is in progress during the replication stage, {{pcsm.short}} records that and will try to recreate the index during the finalization stage.

* **Inconsistent indexes**: {{pcsm.short}} uses the $indexStats aggregation to count index occurrences across shards. If an index exists on fewer shards than the _id_ index, it is considered inconsistent. {{pcsm.short}} skips cloning inconsistent indexes during the replication stage.

* **Failed index creation**: If {{pcsm.short}} cannot create an index during replication, it proceeds with replication and records the failure. The index creation will be retried during the finalization stage.

### Finalization stage

On the finalization stage, {{pcsm.short}} finalizes index index management on the target cluster to match their configuration on the source:

* **Unique index conversion**: Non-unique indexes that were originally unique on the source are converted back to unique indexes.

* **Hidden indexes**: {{pcsm.short}} restores hidden on the target if they were hidden on the source.

* **TTL indexes**: {{pcsm.short}} restores the original `expireAfterSeconds` value for TTL indexes on the target cluster so that documents will expire according to the original configuration.

* **Inconsistent indexes**: {{pcsm.short}} skips creating inconsistent indexes, detected during the replication stage. It reports the warning about such an index in the logs. Check the logs for the information about inconsistent indexes and try to manually recreate them on the target. 

* **Retry failed indexes**: {{pcsm.short}} attempts to create indexes that failed to be created during replication.

* **Warning logs**: If {{pcsm.short}} cannot create an index even during finalization, it records a warning in the logs. Check the logs after finalization to identify any indexes that could not be created.

This approach ensures that replication continues even if some indexes cannot be created immediately, while still attempting to create all indexes during finalization to match the source cluster's index configuration.

## Next steps

Ready to try out {{pcsm.short}}?

[Quickstart](installation.md){.md-button}
