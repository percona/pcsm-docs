# High availability during replication

!!! admonition "Version added: 0.10.0"

Percona ClusterSync for MongoDB (PCSM) supports active-standby high availability during replication. Run two or more instances against the same source and target, and one of them takes charge while the rest wait. If the active instance becomes unavailable, another takes over and resumes replication from the last checkpoint.

High availability is always enabled and requires no configuration. A single instance behaves the same as in earlier versions. To enable failover, start a second instance with the same source and target.

!!! info "Important"
    High availability applies to the **replication phase after the initial clone completes**.

    The initial clone is not resumable. If the active PCSM instance fails during the clone, a standby becomes active, but the interrupted clone cannot continue. Start a new synchronization run to clone the data again.

## How high availability works

The instances coordinate through a lease stored on the target cluster, so the MongoDB deployment you already have is the only coordinator involved. Exactly one instance holds the lease at a time. That instance is `ACTIVE` and runs replication.

PCSM uses the following mechanisms to ensure safe failover and track instance membership:

### Lease election 

PCSM uses a lease to ensure that only one instance is ACTIVE at a time. Lease acquisition and renewal use atomic single-document operations. If several standby instances try to acquire an expired lease, only one can become active.

PCSM evaluates lease expiration using the target MongoDB server clock. Differences between the clocks on PCSM hosts therefore do not affect the election.

For more information about atomic single-document operations, see [Atomicity and Transactions :octicons-link-external-16:](https://www.mongodb.com/docs/manual/core/write-operations-atomicity/){:target="_blank"} in the MongoDB documentation.

PCSM stores the lease as a single document in the `percona_clustersync_mongodb.lease` collection. For example:

```sh
{ "_id": "lease", 
  "group": "default", 
  "term": 7, 
  "instanceId": "b3f1c2a4-9d7e-4c11-8a2f-1e6b0d5c9a77",         
  "electionDate": { "$date": "2026-07-17T09:14:02.190Z" }, 
  "expiresAt": { "$date": "2026-07-17T09:20:41.882Z" } 
}
```

The document identifies the active instance and records the current lease term, election time, and expiration time.

### Term fencing

Each lease has a `term` value that increases whenever a new `ACTIVE` instance is elected. PCSM includes this value in every checkpoint written by the active instance. 

If a previous active instance resumes after losing its lease, its checkpoint writes contain an outdated term and are rejected. The instance then switches to `STANDBY`, which prevents it from overwriting the current replication state.

### Checkpoint recovery

When a standby becomes `ACTIVE`, PCSM resumes replication from the last persisted checkpoint. Failover uses the existing recovery mechanism and happens automatically.

The timings are fixed:

| **Setting** | **Value** |
|---------|-------|
| Lease TTL | 10 seconds |
| Lease renewal by the active instance | Every 3 seconds |
| Heartbeat interval | Every 3 seconds |
| Stale member threshold | 3 missed heartbeats |

If the active instance stops unexpectedly, a standby can take over after the lease expires and continue replication from the latest checkpoint.

### Instance membership

Each PCSM instance records its identity and liveness information in the `percona_clustersync_mongodb.members` collection on the target cluster. The instance refreshes this information with each heartbeat.


For example:

```sh
{
  "_id": "b3f1c2a4-9d7e-4c11-8a2f-1e6b0d5c9a77",
  "group": "default",
  "host": "pcsm0",
  "port": 2242,
  "role": "ACTIVE",
  "term": 7,
  "pcsmVersion": "0.10.0",
  "startedAt": { "$date": "2026-07-17T09:14:02.113Z" },
  "lastHeartbeat": { "$date": "2026-07-17T09:20:31.882Z" }
}
```

A member that does not send a heartbeat within the stale-member threshold is removed from the current group view.

## Set up high availability

Run at least two PCSM instances on separate hosts, containers, or pods. Configure every instance with the same source and target clusters.

For example, run the following command on each host:

```bash
pcsm \
    --source "<source-mongodb-uri>" \
    --target "<target-mongodb-uri>"
```

No additional HA option is required.

If you run multiple PCSM instances on the same host, configure a different `--port` for each instance. For protection against a host failure, run the instances on separate hosts or pods.

See [Start PCSM](install/start-pcsm.md) for startup options and [Percona ClusterSync for MongoDB startup configuration](install/parameters.md) for the available parameters.

### Identify the HA group

You can use `--group-name` or the `PCSM_GROUP_NAME` environment variable to assign a name that identifies the HA deployment in member information, API responses, metrics, and logs.

For example:

```sh
pcsm \
    --source "<source-mongodb-uri>" \
    --target "<target-mongodb-uri>" \
    --group-name migration-1
```

The default group name is `default`.

!!! info "Important"

    In PCSM 0.10.0, the group name is used for identification and observability. It does not isolate HA coordination between different groups that use the same target cluster.

    Do not rely on different group names to create independent HA deployments against the same target.

## Failover during the initial clone

High availability applies to the replication phase after the initial clone completes. The initial clone is not resumable because PCSM does not persist progress for individual collections.

If the `ACTIVE` instance becomes unavailable during the initial clone, a standby is promoted. During recovery, the new `ACTIVE` detects that the clone was interrupted and stops the synchronization. PCSM reports the reason in the logs and through the /status endpoint:

```sh
initial clone interrupted by failover and is not resumable; start a new run to re-clone from scratch
```

!!! info "Important"

    To recover, start a new synchronization run on the `ACTIVE` instance. PCSM starts the initial clone again from the beginning. Automatic recovery from the last checkpoint becomes available after the initial clone completes and PCSM enters the replication phase.

See the [PCSM HTTP API](api.md) for information about the `/status` endpoint and [Start the replication](install/usage.md#start-the-replication) for information about starting a new synchronization run.

## Operate an HA deployment

During normal operation, you need to know which PCSM instance is active, send replication commands to that instance, and monitor all members of the deployment. PCSM exposes the information you need through its API and `/metrics` endpoint.

### Check the active instance

Use the `percona_clustersync_mongodb_ha_active` metric to check the role of a PCSM instance:

```bash
curl -sS http://localhost:2242/metrics | grep percona_clustersync_mongodb_ha_active
```

A value of `1` identifies the active instance. A value of `0` identifies a standby.

When PCSM sees more than one live member, API responses can also include the `me`, `role`, and `group` fields. These fields identify the instance that handled the request and list the live PCSM instances and their current roles.

For example, an operational request sent to a standby returns HTTP `409` with `error: "not_active"`:

```{.json .no-copy}
{
  "ok": false,
  "error": "not_active",
  "me": {
    "instanceId": "<instance-id>"
  },
  "role": "STANDBY",
  "group": {
    "term": 7,
    "members": [
      {
        "instanceId": "<instance-id>",
        "host": "pcsm0",
        "port": 2242,
        "role": "ACTIVE"
      },
      {
        "instanceId": "<instance-id>",
        "host": "pcsm1",
        "port": 2243,
        "role": "STANDBY"
      }
    ]
  }
}
```
The response shows which instance handled the request and identifies the current active member.

!!! info "Important"

    The `me`, `role`, and `group` fields are included only when the instance observes more than one live member. Applications that consume the PCSM API must therefore treat these fields as optional.

    A single PCSM instance continues to return API responses in the same format as earlier releases.

See the [PCSM HTTP API](api.md) for endpoint details.

###  Send operational commands to the active instance

Replication commands must be sent to the active PCSM instance.

The following endpoints return HTTP `409` with `error: "not_active"` when called on a standby:

* `/status`
* `/start`
* `/pause`
* `/resume`
* `/finalize`

When group information is available, the 409 response includes the member list so you can locate the active instance.

See [PCSM commands](pcsm-commands.md) for information about managing a synchronization run.

## Configure health probes

Use `/metrics` for liveness and readiness probes in an HA deployment. This endpoint is available regardless of whether an instance is active or standby.

Do not use `/status` for a readiness probe. A healthy standby returns HTTP `409` from this endpoint because replication status is available only from the active instance.

!!! warning

    A healthy standby returns HTTP `409` from this endpoint because replication status is available only from the active instance. A probe pointed there marks every standby unhealthy. For Kubernetes deployments, see [Configure Liveness, Readiness and Startup Probes :octicons-link-external-16:](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/){:target="_blank"}.


## High availability metrics

PCSM exposes the following HA metrics through `/metrics`:

| Metric                                                  | Description                                                                                                             |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `percona_clustersync_mongodb_ha_active`                 | Shows the current role. `1` means ACTIVE and `0` means STANDBY.                                                         |
| `percona_clustersync_mongodb_ha_term`                   | Shows the current HA lease term.                                                                                        |
| `percona_clustersync_mongodb_ha_role_transitions_total` | Counts role changes for the PCSM instance.                                                                              |
| `percona_clustersync_mongodb_ha_info`                   | Reports instance information. The metric has a constant value of `1` and includes the `instance_id` and `group` labels. |

You can use these metrics to identify the active instance, detect role changes, and monitor failover behavior.

## Reset HA state

PCSM provides commands to clear the stored HA membership or lease state.

!!! warning
    Stop all PCSM server instances that use the target cluster before running these commands. Do not reset HA state while PCSM is running.

Clear the recorded member information:

```bash
pcsm reset members --target "<target-mongodb-uri>"
```

Clear the HA lease:

```bash
pcsm reset lease --target "<target-mongodb-uri>
```

Use these commands only when you need to clear HA coordination state. To clear all PCSM state, use `pcsm reset`.

## Upgrade from PCSM 0.9.0

Replication state created by PCSM 0.9.0 is not compatible with PCSM 0.10.0.

Before starting PCSM 0.10.0:
{.power-number}

1. Stop all PCSM 0.9.0 instances that use the target cluster.

2. Reset the stored PCSM state on the target:

    ```bash
    pcsm reset --target "<target-mongodb-uri>"
    ```

3. Start PCSM 0.10.0
4. Start a new synchronization run.

!!! info "Important"
    Do not run PCSM 0.9.0 and PCSM 0.10.0 against the same target at the same time.

## Next steps

[Use the PCSM HTTP API](api.md){.md-button}

[Manage synchronization with PCSM commands](pcsm-commands.md){.md-button}

[Set up observability with Percona Monitoring and Management](pmm-setup.md){.md-button}


