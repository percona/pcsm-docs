# {{pcsm.full_name}} HTTP API documentation

## Quick start guide

To get started with {{pcsm.full_name}} API:

1. Ensure the service is running on `http://localhost:2242`
2. Use the `/start` endpoint to begin replication
3. Monitor progress using the `/status` endpoint
4. Use `/pause` and `/resume` to control the replication process
5. Call `/finalize` when replication is complete

## Authentication

Currently, the API does not require authentication. However, it's recommended to run the service behind a reverse proxy with proper authentication in production environments.

## API endpoints

### POST /start

Starts the replication process.

#### Request 

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `includeNamespaces` | string[] | No | List of namespaces to include in replication (for example, ["db.*", "db.collection"]) |
| `excludeNamespaces` | string[] | No | List of namespaces to exclude from replication |
| `replNumWorkers` | int | No | Controls how many concurrent replication worker goroutines PCSM uses to apply DML (insert/update/replace/delete) events to the target cluster.|
| `replChangeStreamBatchSize` | int | No | Sets the maximum number of change stream events PCSM will request and read from MongoDB per batch while streaming changes from the source cluster. |
| `replEventQueueSize` | int | No | Controls the size of the internal event queue used by the replication subsystem. |
| `replWorkerQueueSize` | int | No | Defines the maximum number of replication events that each replication worker thread can queue before processing.  |
| `replBulkOpsSize` | int | No | Defines the maximum number of operations that can be grouped together into a single bulk apply batch during replication. |


Examples:

```bash
curl -X POST http://localhost:2242/start -d '{
    "includeNamespaces": ["dbName.*", "anotherDB.collName1", "anotherDB.collName2"],
    "excludeNamespaces": ["dbName.collName"],
    "replWorkerFlushInterval": "1s",
    "replWorkerBulkQueueSize": 3
}'
```

```bash
curl -X POST "http://localhost:2242/start" \
  -H "Content-Type: application/json" \
  --data '{
    "replChangeStreamBatchSize": 10000,
    "replEventQueueSize": 5000,
    "replWorkerQueueSize": 5000,
    "replBulkOpsSize": 5000
  }'
```

#### Response

- `ok`: Boolean indicating if the operation was successful.
- `error` (optional): Error message if the operation failed.

Example:

```json
{ "ok": true }
```

### POST /finalize

Finalizes the replication process.

#### Request 

Example:

```bash
curl -X POST http://localhost:2242/finalize
```

#### Response

- `ok`: Boolean indicating if the operation was successful.
- `error` (optional): Error message if the operation failed.

Example:

```json
{ "ok": true }
```

### POST /pause

Pauses the replication process.

#### Request 

Example:

```bash
curl -X POST http://localhost:2242/pause
```

#### Response

- `ok`: Boolean indicating if the operation was successful.
- `error` (optional): Error message if the operation failed.

Example:

```json
{ "ok": true }
```

### POST /resume

Resumes the replication process.

#### Request

Example:

```bash
curl -X POST http://localhost:2242/resume
```

Resume from failure:

```bash
curl -X POST http://localhost:2242/resume -d '{
  "fromFailure": true
}'
```

#### Response

- `ok`: Boolean indicating if the operation was successful.
- `error` (optional): Error message if the operation failed.

Example:

```json
{ "ok": true }
```

### GET /status

The /status endpoint provides the current state of the Percona ClusterSync for MongoDB replication process, including its progress, lag, and event processing details.

#### Request

Example:

```bash
curl -X GET http://localhost:2242/status
```

#### Response

The following are response fields:

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | Operation success status |
| `state` | string | Current replication state |
| `info` | string | Additional information about the current state|
| `error`| string | (optional): The error message if the operation failed.
| `lagTimeSeconds` | number | Current lag time in logical seconds between source and target clusters. |
| `eventsRead` | number | Total number of events read from the source |
| `eventsApplied` | number | Total number of events applied to the target |
| `lastReplicatedOpTime.ts` | string | The timestamp of the last replicated operation time.  |
| `lastReplicatedOpTime.isoDate` | date.Time | The human-readable representation of the last replicated operation time.  |
| `initialSync.completed` | boolean | Initial sync completion status |
| `initialSync.lagTime` | number | The lag time in logical seconds until the initial sync completed|
| `initialSync.cloneCompleted` | boolean | Clone process completion status |
| `initialSync.estimatedCloneSizeBytes` | number | Estimated total size to clone (bytes) |
| `initialSync.clonedSizeBytes` | number | Current cloned size (bytes) |
| `finalization.completed` | boolean | Finalization completion status |
| `finalization.startedAt` | date.Time | RFC3339 timestamp when finalization started |
| `finalization.completedAt` | date.Time | RFC3339 timestamp when finalization completed |
| `finalization.unsuccessfulIndexes` | array | List of indexes that were not finalized successfully (omitted when empty) |
| `finalization.unsuccessfulIndexes[].namespace` | string | MongoDB namespace in `database.collection` format |
| `finalization.unsuccessfulIndexes[].indexName` | string | Index name |
| `finalization.unsuccessfulIndexes[].type` | string | Machine-readable failure category (`failed`, `incomplete`, `inconsistent`) |
| `finalization.unsuccessfulIndexes[].reason` | string | Human-readable reason why finalization failed for this index |
| `finalization.unsuccessfulIndexes[].keys` | object | Index key specification |


Example:

```json
{
  "ok": true,
  "state": "finalized",
  "info": "Finalized",
  "lagTimeSeconds": 0,
  "eventsRead": 0,
  "eventsApplied": 0,
  "lastReplicatedOpTime": {
    "ts": "1779199363.1",
    "isoDate": "2026-05-19T14:02:43Z"
  },
  "initialSync": {
    "estimatedCloneSizeBytes": 328116,
    "clonedSizeBytes": 328116,
    "completed": true,
    "cloneCompleted": true
  },
  "finalization": {
    "completed": true,
    "startedAt": "2026-05-07T10:30:00Z",
    "completedAt": "2026-05-07T10:30:42Z",
    "unsuccessfulIndexes": [
      {
        "namespace": "mydb.users",
        "indexName": "email_unique_idx",
        "type": "failed",
        "reason": "recreate index mydb.users.email_unique_idx: duplicate key error",
        "keys": {
          "email": 1
        }
      }
    ]
  }
}
```

## Error handling

The API uses standard HTTP status codes and returns error messages in the following format:

```json
{
    "ok": false,
    "error": "Detailed error message"
}
```

Common error scenarios:

- 400 Bad Request: Invalid request parameters
- 404 Not Found: Endpoint not found
- 500 Internal Server Error: Server-side issues


