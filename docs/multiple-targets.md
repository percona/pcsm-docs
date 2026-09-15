# Replicate from one source to multiple targets

!!! admonition "Version added: 0.10.0"

You can run multiple {{pcsm.full_name}} (PCSM) instances against the same source cluster and replicate different namespaces to different target clusters at the same time. This lets you split one cluster across several destinations in a single pass, with each instance moving only the data you assign to it.

## How it works

Each PCSM instance has:

- The same source cluster
- Its own target cluster
- Its own namespace filter

Every instance runs the full replication workflow on its own: clone, replication, and finalization. See [How PCSM works](intro.md) for what happens at each stage.

!!! note

    Run each PCSM server in a separate container or host, or assign a unique `--port` when servers share a network namespace. Run every `start`, `status`, and `finalize` command in the corresponding container or host; for a shared host, pass that instance's `--port` to every subcommand. The examples below assume separate environments, where all instances can use the default port `2242`. See [Percona ClusterSync for MongoDB startup configuration](install/parameters.md) for the available options.

## Before you begin

Map out which instance owns which namespaces and which target before you start. You need that mapping again for every command you run, and it is the only record of which instance owns which data.

!!! warning "Starting replication overwrites target collections"
    `pcsm start` drops and recreates the collections that match your filter on the target, discarding any data already in them. Collections outside the filter stay as they are. Review each filter first, since a mistyped pattern affects only the target and leaves no trace on the source.

The examples below use target clusters with no pre-existing application namespaces. They replicate `db_0` to the first target and `db_1` to the second. Select the tab that matches your deployment.

=== "Replica set"

    ## Replicate from a replica set to two targets

    This example uses a source replica set `rs1` and two target replica sets, `rs2` and `rs3`.

    | **PCSM instance** | **Source** | **Target** | **Included namespaces** |
    |-------------------|------------|------------|-------------------------|
    | csync-a           | rs1        | rs2        | `db_0.*`                |
    | csync-b           | rs1        | rs3        | `db_1.*`                |

    Follow these steps:
    {.power-number}

    1. Start `csync-a` with `rs1` as the source and `rs2` as the target:

        ```bash
        pcsm \
        --source "mongodb://csync:<password>@rs101:27017,rs102:27017,rs103:27017/?replicaSet=rs1" \
        --target "mongodb://csync:<password>@rs201:27017,rs202:27017,rs203:27017/?replicaSet=rs2"
        ```

    2. Start `csync-b` against the same source, with `rs3` as the target:

        ```bash
        pcsm \
        --source "mongodb://csync:<password>@rs101:27017,rs102:27017,rs103:27017/?replicaSet=rs1" \
        --target "mongodb://csync:<password>@rs301:27017,rs302:27017,rs303:27017/?replicaSet=rs3"
        ```

    3. Start replication on `csync-a`, filtered to the namespaces it replicates:

        ```bash
        pcsm start --include-namespaces="db_0.*"
        ```

        ??? example "Expected output"

            ```{.json .no-copy}
            {
            "ok": true
            }
            ```

    4. Start replication on `csync-b` with its own filter:

        ```bash
        pcsm start --include-namespaces="db_1.*"
        ```

        For information on how include and exclude filters interact, see [Start the filtered replication](install/usage.md#start-the-filtered-replication). For the full flag list, see [PCSM commands](pcsm-commands.md). You can also drive every step through the [PCSM HTTP API](api.md).

    5. Check each instance and wait for the clone to complete and replication lag to reach an acceptable value. Look for `initialSync.completed` set to `true` and a low `lagTimeSeconds`:

        ```bash
        pcsm status
        ```

    6. Finalize each instance. PCSM stops replication, creates the remaining indexes on the target, and exits:

        ```bash
        pcsm finalize
        ```

        !!! warning "Finalization cannot be undone"
            You cannot resume an instance after you finalize it. Running `start` again begins a fresh initial sync and overwrites the target collections a second time. For a migration cutover, stop application writes to the namespaces the instance owns, wait for `lagTimeSeconds` to reach `0`, and finalize only then. Instances you are not cutting over yet keep replicating and are unaffected.

    7. Check the status of each instance after finalization. The following output is from `csync-a`. The `csync-b` output has the same structure with its own operation time and finalization timestamps:

        ```bash
        pcsm status
        ```

        ??? example "Expected output"

            ```{.json .no-copy}
            {
                "ok": true,
                "state": "finalized",
                "info": "Finalized",
                "lagTimeSeconds": 0,
                "eventsRead": 0,
                "eventsApplied": 0,
                "lastReplicatedOpTime": {
                    "ts": "1787298593.1",
                    "isoDate": "2026-08-21T07:49:53Z"
                },
                "initialSync": {
                    "estimatedCloneSizeBytes": 9877780,
                    "clonedSizeBytes": 9877780,
                    "completed": true,
                    "cloneCompleted": true
                },
                "finalization": {
                    "completed": true,
                    "startedAt": "2026-08-21T07:49:53.633159569Z",
                    "completedAt": "2026-08-21T07:49:53.759444616Z"
                }
            }
            ```       

    If the `finalization` object contains an `unsuccessfulIndexes` array, review it before you send traffic to that target. See [Unsuccessful indexes](install/usage.md#unsuccessful-indexes).

    ### Verify the result on replica set targets

    Connect to each target and confirm it holds only the namespaces that its instance replicated.

    ```sh
    show databases
    ```

    You see `db_0` next to `admin`, `config`, and `percona_clustersync_mongodb`, which is where PCSM keeps its own replication metadata. The `db_1` database is absent, because `csync-a` never replicated it.


    Counting documents confirms the same thing from the data side:

    ```javascript
    db.getSiblingDB('db_0').docs.countDocuments({})
    db.getSiblingDB('db_1').docs.countDocuments({})
    ```

    The first count matches the source. The second returns `0` rather than an error.


    PCSM recreates the source indexes on the target during finalization, so check that they arrived:

    ```javascript
    db.getSiblingDB('db_0').docs.getIndexes().map(i => i.name)
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
        [
            '_id_',
            'value_1',
            'value_1_uid_-1',
            'uid_1',
            'tag_text',
            '_id_hashed',
            'created_at_1',
            'value_partial',
            'tag_sparse'
        ]
        ```

    The collection replicated to the other target does not exist here, so querying it returns an error.

    ```javascript
    db.getSiblingDB('db_1').docs.getIndexes().map(i => i.name)
    ```

    ```{.text .no-copy}
    MongoServerError[NamespaceNotFound]: ns does not exist: db_1.docs
    ```

    Repeat the same three checks on `rs3` with the databases reversed. There, `db_1` holds the data and its indexes, and `db_0.docs` returns `ns does not exist: db_0.docs`.

=== "Sharded cluster"

    !!! warning "Technical preview"

        Sharding support in PCSM is a technical preview and is not recommended for production. See [Sharding support in Percona ClusterSync for MongoDB](sharding.md).

    ## Replicate from a sharded cluster to two targets

    This example uses three sharded clusters, each with its own [mongos :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/sharded-cluster-query-router/){:target="_blank"}, config server, and two shards. One cluster is the source and two are targets.

    | **PCSM instance** | **Source** | **Target** | **Included namespaces** |
    |-------------------|------------|------------|-------------------------|
    | csync-a           | mongos1    | mongos2    | `db_0.*`                |
    | csync-b           | mongos1    | mongos3    | `db_1.*`                |

    !!! note "Requirements for sharded deployments"
        The source and both targets must be sharded clusters running the same MongoDB version, unless you are using [cross-version replication](version-compatibility.md). You do not need to disable the balancer on any of them. See [Sharding support in Percona ClusterSync for MongoDB](sharding.md).

    PCSM connects through `mongos` on both the source and the target, so you do not need to list individual shard members or config servers in the connection strings.
    {.power-number}

    1. Start `csync-a` against the source `mongos` and the first target `mongos`:

        ```bash
        pcsm \
        --source "mongodb://csync:<password>@mongos1:27017" \
        --target "mongodb://csync:<password>@mongos2:27017"
        ```

    2. Start `csync-b` against the same source `mongos` and the second target `mongos`:

        ```bash
        pcsm \
        --source "mongodb://csync:<password>@mongos1:27017" \
        --target "mongodb://csync:<password>@mongos3:27017"
        ```

    3. Start replication on `csync-a`:

        ```bash
        pcsm start --include-namespaces="db_0.*"
        ```

        ??? example "Expected output"

            ```{.json .no-copy}
            {
            "ok": true
            }
            ```

        Before the clone begins, PCSM checks which of the selected collections are sharded on the source and creates matching sharded collections on the target, carrying over the shard key.


    4. Start replication on `csync-b`:

        ```bash
        pcsm start --include-namespaces="db_1.*"
        ```
    
        For information on how include and exclude filters interact, see [Start the filtered replication](install/usage.md#start-the-filtered-replication). For the full flag list, see [PCSM commands](pcsm-commands.md). You can also drive every step through the [PCSM HTTP API](api.md).


    5. Check each instance and wait for the clone to complete and replication lag to reach an acceptable value. Look for `initialSync.completed` set to `true` and a low `lagTimeSeconds`:

        ```bash
        pcsm status
        ```

    6. Finalize each instance:

        ```bash
        pcsm finalize
        ```

        !!! warning "Finalization cannot be undone"
            You cannot resume an instance after you finalize it. Running `start` again begins a fresh initial sync and overwrites the target collections a second time. For a migration cutover, stop application writes to the namespaces the instance owns, wait for `lagTimeSeconds` to reach `0`, and finalize only then.

    7. Check the status of each instance after finalization. The following output is from `csync-a`:

        ```bash
        pcsm status
        ```

        ??? example "Expected output"

            ```{.json .no-copy}
            {
                "ok": true,
                "state": "finalized",
                "info": "Finalized",
                "lagTimeSeconds": 0,
                "eventsRead": 6,
                "eventsApplied": 5,
                "lastReplicatedOpTime": {
                    "ts": "1787301347.3",
                    "isoDate": "2026-08-21T08:35:47Z"
                },
                "initialSync": {
                    "estimatedCloneSizeBytes": 9877780,
                    "clonedSizeBytes": 9877780,
                    "completed": true,
                    "cloneCompleted": true
                },
                "finalization": {
                    "completed": true,
                    "startedAt": "2026-08-21T08:35:47.949454942Z",
                    "completedAt": "2026-08-21T08:35:48.21823288Z"
                }
            }
            ```   
            
    ### Verify the result on sharded targets

    Connect to the `mongos` of each target cluster, not to the shards directly. On `mongos2`, list the databases:


    ```javascript
    show databases
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
        admin                        172.00 KiB
        config                         2.11 MiB
        db_0                          31.56 MiB
        percona_clustersync_mongodb  168.00 KiB
        ```

    Count the documents. The `db_0` database returns the full count and `db_1` returns zero:

    ```javascript
    db.getSiblingDB('db_0').docs.countDocuments({})
    db.getSiblingDB('db_1').docs.countDocuments({})
    ```

    Check that the indexes PCSM recreated during finalization are present:

    ```javascript
    db.getSiblingDB('db_0').docs.getIndexes().map(i => i.name)
    ```

    ??? example "Expected output"

        ```{.text .no-copy}
        [
            '_id_',
            'value_1',
            'value_1_uid_-1',
            'uid_1',
            'tag_text',
            '_id_hashed',
            'created_at_1',
            'value_partial',
            'tag_sparse'
        ]
        ```

    The collection replicated to the other target does not exist here, so querying it returns an error. This is the expected result:

    ```javascript
    db.getSiblingDB('db_1').docs.getIndexes().map(i => i.name)
    ```

    ```{.text .no-copy}
    MongoServerError[NamespaceNotFound]: ns does not exist: db_1.docs
    ```

    If the source collection was sharded, confirm that the target collection is sharded too.


!!! note
    For a ranged shard key, PCSM recreates the source chunk boundaries on the target before the clone. Later sharding metadata changes are not replicated, so the layouts diverge as each balancer works. That is expected. See [Chunk distribution](sharding.md#chunk-distribution).

    Run the same checks on `mongos3` with the databases reversed. There, `db_1` holds the data and its indexes, and `db_0.docs` returns `ns does not exist: db_0.docs`.

## Check the logs

Every instance logs separately, so check each one for errors before you decommission the source or send traffic to a target. Command responses go to `stdout` and logs and errors go to `stderr`. See [Logging in Percona ClusterSync for MongoDB](logging.md).

If an instance stops because of lost connectivity or a similar failure after `initialSync.completed` becomes `true` and before finalization, bring it back with `pcsm resume --from-failure`. An interruption during initial synchronization cannot be resumed; restart the clone as described in [Recover PCSM during initial data clone](troubleshooting.md#recover-pcsm-during-initial-data-clone). See [Resume the replication](pcsm-commands.md#resume) for command details.

## Next steps

- [Use Percona ClusterSync for MongoDB](./install/usage.md)
- [Sharding support in Percona ClusterSync for MongoDB](./sharding.md)