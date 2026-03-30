# {{pcsm.full_name}} commands

## Overview

Percona ClusterSync for MongoDB is a replication tool for MongoDB clusters. It provides commands to manage and monitor the replication process between source and target MongoDB clusters.

## Commands

### Common flags

The following flag is available on all subcommands:

| Name     | Description                                                                                                                                                            |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--port` | Port number of the running PCSM server to connect to (default: `2242`). Use this when the server is listening on a non-default port (e.g., `pcsm status --port 3000`). |


### version

Display the current version of Percona ClusterSync for MongoDB.

```{.bash data-prompt="$"$}
$ pcsm version
```

### status

Get the status of the replication process.

```{.bash data-prompt="$"$}
$ pcsm status
```

If the PCSM server is running on a non-default port, specify it with `--port` flag:

```{.bash data-prompt="$"}
$ pcsm status --port 3000
```


### start

Starts cluster replication.

```{.bash data-prompt="$"$}
$ pcsm start
```

To start a filtered replication, pass the namespaces (databases and collections) that you want to include/exclude from replication. 

```{.bash data-prompt="$"}
$ pcsm start \
--include-namespaces="db1.collection1,db2.collection2" \
--exclude-namespaces="db3.collection3"
```

To include or exclude a specific database and all collections it includes, pass it in the format `mydb.*`.

Available flags:


| Name | Description|
| -----| -----------|
| `--include-namespaces` | Replicate only the specified namespaces. Multiple namespaces are supported as a comma separated list. The number of namespaces to specify is unlimited|
| `--exclude-namespaces` | Replicate everything except the specified namespaces. Multiple namespaces are supported as a comma separated list. The number of namespaces to specify is unlimited. <br> When both `--include-namespaces` and  `--exclude-namespaces` flags are specified, the exclude filters take precedence. For example, if the `--include-namespaces` includes `db1.*` and `--exclude-namespaces` has `db1.users`, {{pcsm.short}} syncs all collections of `db1` **except** `db1.users`.|
| `--clone-num-parallel-collections` | Number of collections to copy in parallel during clone. | `Auto` |
| `--clone-num-read-workers` | Number of read workers that read collection segments from the source. Shared for all collections.| `NumCPU / 4` |
| `--clone-num-insert-workers` | Number of insert workers that write batches to the target. Shared for all collections.| `NumCPU * 2` |


### reset

Resets the `PCSM` state and deletes the metadata collections from target deployment. After the command execution, you must restart the `PCSM` service and start the data replication from scratch. Read more about the flow in [Troubleshooting guide](troubleshooting.md) 

```{.bash data-prompt="$"$}
$ pcsm reset --target
```

### finalize

Finalize cluster replication.

```{.bash data-prompt="$"$}
$ pcsm finalize
```

### pause

Pause cluster replication.

```{.bash data-prompt="$"$}
$ pcsm pause
```

### resume

Resume cluster replication.

```{.bash data-prompt="$"$}
$ pcsm resume
```

Available flags:

| Name | Description|
| -----| -----------|
| `--from-failure` | Resume replication from the last failure point |
