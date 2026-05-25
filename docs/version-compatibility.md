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
| 6.0.x | 8.0.x | **Planned** | Not available in the current release. Use the upgrade path: 6.0 → 7.0 → 8.0 |
| 7.0.x | 7.0.x | **Yes** | — |
| 7.0.x | 8.0.x | **Yes** | — |
| 8.0.x | 7.0.x | **No** | Downgrade replication is not supported.|
| 7.0.x | 6.0.x | **No** | Downgrade replication is not supported. |
| Any higher | Any lower | **No** | All downgrade paths are blocked. |

Use only the version combinations listed as supported in the table above. Unsupported combinations may start successfully but are not tested or officially supported.

## Limitations

- **Major-version validation only**

    PCSM validates only MongoDB major versions. It does not compare patch versions or validate combinations against a certified compatibility list.

    For example:

       - 7.0.5 → 7.0.12 is allowed
       - 7.0.5 → 7.0.2 is also allowed

    Verify patch-level compatibility before deploying mixed-version environments.

- **Feature Compatibility Version (FCV) is not validated**

    PCSM does not compare the Feature Compatibility Version (FCV) values of the source and target clusters.

    If the target cluster FCV is lower than the source cluster FCV, replication issues may occur and PCSM will not detect the mismatch automatically.

    Before starting replication:
    - Verify the FCV on both clusters
    - Ensure the target cluster FCV is equal to or higher than the source cluster FCV

- **Downgrade replication is not supported**

    {{pcsm.full_name}} blocks startup if the source major version is higher than the target major version.

- Cross version replication on sharded clusters 

    Cross version replication on sharded clusters is not fully tested. Before deploying this configuration in production, verify setup in a staging environment that mirrors your production topology.

- **Version compatibility is only checked at startup** 

    PCSM performs the version check once when the server starts. This check is not repeated when replication is started or resumed.


