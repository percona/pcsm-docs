# Percona Link for MongoDB startup configuration

When [starting the `plm` process](start-plm.md), you can use the following options:

- `--port`: The port on which the server will listen (default: 2242)
- `--source`: The MongoDB connection string for the source cluster
- `--target`: The MongoDB connection string for the target cluster
- `--log-level`: The log level (default: "info")
- `--log-json`: Output log in JSON format with disabled color
- `--no-color`: Disable log ASCI color

Example:

```{.bash data-prompt="$"}
$ plm \
    --source <source-mongodb-uri> \
    --target <target-mongodb-uri> \
    --port 2242 \
    --log-level debug \
    --log-json
```

## Environment variables

Alternatively, you can define the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PLM_SOURCE_URI` | MongoDB connection string for the source cluster | - |
| `PLM_TARGET_URI` | MongoDB connection string for the target cluster | - |
| `PLM_PORT` | Server port number | `2242` |
| `PLM_CLONE_NUM_PARALLEL_COLLECTIONS` | Number of collections cloned in parallel | `2` |
| `PLM_CLONE_NUM_READ_WORKERS` | Number of read workers for cloning | `NumCPU / 4` |
| `PLM_CLONE_NUM_INSERT_WORKERS` | Number of insert workers for cloning | `NumCPU * 4` |
