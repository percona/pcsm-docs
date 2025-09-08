# How to log JSON fields?

When using the `--log-json` option, the logs will be output in JSON format with the following fields:

- `time`: Unix time when the log entry was created.
- `level`: Log level ("debug", "info", "warn", "error").
- `message`: Log message, if any.
- `error`: Error message, if any.
- `s`: Scope of the log entry.
- `ns`: Namespace (database.collection format).
- `elapsed_secs`: The duration in seconds for the specific operation to complete.

Example:

```json
{ "level": "info",
  "s": "clone",
  "ns": "db_1.coll_1",
  "elapsed_secs": 0,
  "time": "2025-02-23 11:26:03.758",
  "message": "Cloned db_1.coll_1" }

{ "level": "info",
  "s": "plm",
  "elapsed_secs": 0,
  "time": "2025-02-23 11:26:03.857",
  "message": "Change replication stopped at 1740335163.1740335163 source cluster time" }
```