# {{pcsm.full_name}} commands

## Overview

Percona ClusterSync for MongoDB is a replication tool for MongoDB clusters. It provides commands to manage and monitor the replication process between source and target MongoDB clusters.

## Commands

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
