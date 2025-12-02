# {{plm.full_name}} commands

## Overview

Percona Link for MongoDB is a replication tool for MongoDB clusters. It provides commands to manage and monitor the replication process between source and target MongoDB clusters.

## Commands

### version

Display the current version of Percona Link for MongoDB.

```{.bash data-prompt="$"$}
$ plm version
```

### status

Get the status of the replication process.

```{.bash data-prompt="$"$}
$ plm status
```

### start

Starts cluster replication.

```{.bash data-prompt="$"$}
$ plm start
```

To start a filtered replication, pass the namespaces (databases and collections) that you want to include/exclude from replication. 

```{.bash data-prompt="$"}
$ plm start \
--include-namespaces="db1.collection1,db2.collection2" \
--exclude-namespaces="db3.collection3"
```

To include or exclude a specific database and all collections it includes, pass it in the format `mydb.*`.

Available flags:


| Name | Description|
| -----| -----------|
| `--include-namespaces` | Replicate only the specified namespaces. Multiple namespaces are supported as a comma separated list. The number of namespaces to specify is unlimited|
| `--exclude-namespaces` | Replicate everything except the specified namespaces. Multiple namespaces are supported as a comma separated list. The number of namespaces to specify is unlimited|


### reset

Resets the `PLM` state and deletes the metadata collections from target deployment. After the command execution, you must restart the `PLM` service and start the data replication from scratch. Read more about the flow in [Troubleshooting guide](troubleshooting.md) 

```{.bash data-prompt="$"$}
$ plm reset --target
```

### finalize

Finalize cluster replication.

```{.bash data-prompt="$"$}
$ plm finalize
```

### pause

Pause cluster replication.

```{.bash data-prompt="$"$}
$ plm pause
```

### resume

Resume cluster replication.

```{.bash data-prompt="$"$}
$ plm resume
```

Available flags:

| Name | Description|
| -----| -----------|
| `--from-failure` | Resume replication from the last failure point |
