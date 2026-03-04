# Logging in Percona ClusterSync for MongoDB

Percona ClusterSync for MongoDB (PCSM) provides a flexible logging system to help you monitor its operations, diagnose issues, and integrate with log management systems. You can control the log verbosity, format, and appearance using command-line flags.

## Configuration

You configure logging when the `pcsm` process starts. The following flags are available:

| Flag          | Description                                       | Default |
|---------------|---------------------------------------------------|---------|
| `--log-level` | Sets the verbosity of the logs.                   | `info`  |
| `--log-json`  | Outputs logs in a structured JSON format.         | `false` |
| `--log-no-color`  | Disables colorized output for text-based logs.    | `false` |

### Environment variables

Alternatively, you can define the following environment variables:

| Variable | Description | Default |
| --- | --- | --- |
| `PCSM_LOG_LEVEL` |Log level used for output (e.g., debug, info, warn, error). Controls the verbosity of logs. | `info` |
| `PCSM_LOG_JSON` | Output logs in JSON format. When enabled, log coloring is automatically disabled. | `false` |
| `PCSM_LOG_NO_COLOR` | Disable ANSI color codes in log output (useful for non-interactive terminals and log aggregation systems). | `false` |

### Log level

The `--log-level` flag controls the minimum level of messages that will be recorded. The supported levels are, in order of severity:

- `trace`: Highly detailed diagnostic information.
- `debug`: Detailed information useful for debugging.
- `info`: General information about the application's state and progress.
- `warn`: Potentially harmful situations or unexpected events.
- `error`: Errors that prevent a specific operation from completing but do not stop the application.
- `fatal`: Severe errors that cause the application to terminate.

**Example:** 

To see detailed debugging messages, start `pcsm` with:

```bash
pcsm --source <source-uri> --target <target-uri> --log-level=debug
```

### Log format

PCSM can output logs in two formats: human-readable text (default) and structured JSON.

#### Text format (default)

By default, logs are printed to the console in a color-coded, human-readable format. This is ideal for interactive use and manual inspection.

??? example "Sample output"

    ```text
    2024-10-26 14:30:01.000 INF s=http Starting HTTP server at http://localhost:2242
    2024-10-26 14:30:05.123 DBG s=repl:watch op=insert ns=test.coll1 op_ts=1729953005,1
    ```

You can disable the colorization with the `--log-no-color` flag (or its alias `--no-color`). This is useful when redirecting log output to a file.

If you are running the PCSM server process and want to capture logs while disabling color codes, use:

```bash
pcsm --source <source-uri> --target <target-uri> --log-no-color > pcsm.log
```

For client subcommands (like start, resume, or finalize), you must redirect `stderr` to ensure the logs are actually saved:

```bash
# To capture only the logs (stderr)
pcsm start 2> pcsm.log

# To capture everything (both stdout and stderr)
pcsm start &> pcsm.log
```

#### JSON format

For automated processing and integration with log aggregation tools (like the ELK stack or Splunk), you can use the `--log-json` flag. This will output each log entry as a single line of JSON.

??? example "Sample output"

    ```json
    {"level":"info","s":"http","time":"2024-10-01 14:30:01.000","message":"Starting HTTP server at http://localhost:2242"}
    {"level":"debug","s":"repl:watch","op":"insert","ns":"test.coll1","op_ts":[1729953005,1],"time":"2024-10-26 14:30:05.123"}
    ```

### JSON field reference

When `--log-json` is enabled, the following fields may appear in the log entries:

| Field          | Type    | Description                                                                |
|----------------|---------|----------------------------------------------------------------------------|
| `level`        | string  | The severity of the log entry (e.g., info, debug).                         |
| `s`	           | string	 | The scope or component where the log originated (e.g., http, clone, repl). |
| `ns`	         | string	 | The MongoDB namespace (database.collection) related to the event.          |
| `elapsed_secs` | float	 | The time taken for an operation to complete, in seconds.                   |
| `time`	       | string  | The timestamp of the log event in YYYY-MM-DD HH:MM:SS.ms format.           |
| `message`	     | string	 | The main log message.                                                      |
| `error`	       | string	 | The error message, if an error occurred.                                   |
| `op`	         | string	 | The type of operation (e.g., insert, createIndexes).                       |
| `op_ts`	       | array	 | The MongoDB operation timestamp as [timestamp, increment].                 |
| `count`	       | integer | A count of items, such as documents in a batch.                            |
| `size_bytes`	 | integer | The size of data in bytes.                                                 |

