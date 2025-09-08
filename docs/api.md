# {{plm.full_name}} HTTP API documentation

## Quick start guide

To get started with {{plm.full_name}} API:

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

Example:

```json
curl -X POST http://localhost:2242/start -d '{
    "includeNamespaces": ["dbName.*", "anotherDB.collName1", "anotherDB.collName2"],
    "excludeNamespaces": ["dbName.collName"]
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

```json
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

```json
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

```json
curl -X POST http://localhost:2242/resume
```

Resume from failure:

```json
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

The /status endpoint provides the current state of the Percona Link for MongoDB replication process, including its progress, lag, and event processing details.

#### Request

Example:

```json
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
| `lagTime` | number | Current lag time in logical seconds between source and target clusters. |
| `eventsProcessed` | number | Total events processed |
| `lastReplicatedOpTime` | string | The last replicated operation time.|
| `initialSync.completed` | boolean | Initial sync completion status |
| `initialSync.lagTime` | number | The lag time in logical seconds until the initial sync completed|
| `initialSync.cloneCompleted` | boolean | Clone process completion status |
| `initialSync.estimatedCloneSize` | number | Estimated total size to clone (bytes) |
| `initialSync.clonedSize` | number | Current cloned size (bytes) |


Example:

```json
{
    "ok": true,
    "state": "running",
    "info": "Initial Sync",

    "lagTime": 22,
    "eventsProcessed": 5000,
    "lastReplicatedOpTime": "1740335200.5",

    "initialSync": {
        "completed": false,
        "lagTime": 5,

        "cloneCompleted": false,
        "estimatedCloneSize": 5000000000,
        "clonedSize": 2500000000
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


