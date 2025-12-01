# Oplog sizing for Percona ClusterSync for MongoDB

Percona ClusterSync for MongoDB synchronizes data between MongoDB replica sets using change streams. For the sync to complete successfully, the required operations must remain in the source's oplog until they are applied. If operations expire from the oplog before being processed, the sync will fail.

## Source cluster oplog requirements

After the initial data copy, PCSM applies ongoing changes using the oplog from the source cluster. If the oplog window is too short, PCSM may fall behind and lose access to required changes. To avoid this, increase the oplog retention window using the `replSetResizeOplog` command.

This is especially important when:

- migrating large datasets
- pausing the sync
- experiencing slow sync performance

## Destination storage considerations

The destination cluster must have enough space to store both the full dataset and the oplog entries that represent applied changes. To reduce the disk usage on the destination, you can:

- Lower the oplog retention window using the [`storage.oplogMinRetentionHours` :octicons-link-external-16:](https://www.mongodb.com/docs/manual/reference/configuration-options/#mongodb-setting-storage.oplogMinRetentionHours) configuration option in MongoDB
- Keep the oplog size minimal if no extended retention is needed. You can manage the oplog size using the [`replication.oplogSizeMB` :octicons-link-external-16:](https://www.mongodb.com/docs/manual/reference/configuration-options/#mongodb-setting-replication.oplogSizeMB) option.

## Track the data sync progress

During the initial data clone, PCSM clones data and then applies oplog entries on top. You track the sync progress and fine-tune PCSM. Here's how:

### Extend the oplog window if the lag approaches its limit  

1. Evaluate the oplog size required for initial data clone with the following command: 
      
    ```{.json data-prompt=">"}
    > db.getReplicationInfo().timeDiff
    ```

    The value you get is the minimum oplog window, in seconds.

2. Compare this value to the current sync lag using the `pcsm status` command and the `lagTime` field.  If the `lagTime` approaches the oplog window, extend the window using the `replSetResizeOplog` with a higher `minRetentionHours` value.

### Improve the sync performance to reduce lag  

If the oplog is large enough but the lag is still high, optimize performance by:

- Running PCSM closer to the destination to reduce network latency
- Increasing CPU and memory on PCSM host
- Using faster hardware on the destination to improve write performance