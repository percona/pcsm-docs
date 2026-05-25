# Cross version replication

{{pcsm.full_name}} (PCSM) supports replication between clusters running the same MongoDB major version, and from clusters running an older major version to clusters running a newer one. This lets you synchronize data during a staged upgrade or maintain replication across clusters that run different versions.

PCSM checks the major version relationship between source and target at startup. If the source major version is higher than the target major version, PCSM blocks startup and exits with an error.

## Supported scenarios

PCSM allows synchronization when either of the following conditions is met:

- The target cluster runs a higher major version than the source cluster (lower-to-higher replication).
- Both clusters run the same major version.

PCSM blocks synchronization in all cases where the source major version is higher than the target major version. Downgrade replication is not supported and cannot be overridden.

## Version compatibility matrix

| Source version | Target version | Supported | Notes |
|----------------|----------------|-----------|-------|
| 6.0.x | 6.0.x | **Yes** | — |
| 6.0.x | 7.0.x | **Yes** | — |
| 6.0.x | 8.0.x | **Planned** | Not available in the current release. Use a two-hop path instead: replicate from 6.0 to 7.0, then from 7.0 to 8.0. |
| 7.0.x | 7.0.x | **Yes** | — |
| 7.0.x | 8.0.x | **Yes** | — |
| 8.0.x | 7.0.x | **No** | Downgrade replication is not supported. Startup is blocked. |
| 7.0.x | 6.0.x | **No** | Downgrade replication is not supported. Startup is blocked. |
| Any higher | Any lower | **No** | All downgrade paths are blocked. |

Only run the combinations listed as **Yes** above. PCSM does not validate version combinations against a known-good list, so an unsupported pairing may start without error but will not behave reliably and is not tested. Downgrade paths cannot be overridden.

## Limitations

- Downgrade replication is not supported. {{pcsm.full_name}} blocks startup if the source major version is higher than the target major version.

- PCSM checks major versions only. It does not compare patch versions or validate the combination against a list of known-good pairings, so an unsupported combination can start without error. Only run the combinations listed in the version compatibility matrix.

- PCSM does not validate the Feature Compatibility Version (FCV) between source and target clusters. If the target's FCV is lower than the source's (e.g., after a rollback), {{pcsm.full_name}} will not recognize the mismatch. Manually verify FCV alignment before starting replication.

- Cross version replication on sharded clusters is not fully tested. Before using this combination in production, verify behavior in a staging environment that mirrors your production topology.

- Version compatibility is only checked at startup. PCSM performs the version check once when the server starts. This check is not repeated when replication is started or resumed.


