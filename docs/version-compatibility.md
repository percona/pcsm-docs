# Cross-version replication

{{pcsm.full_name}} (PCSM) supports replication only for the MongoDB binary major-version combinations listed in the compatibility matrix below. The matrix covers binary versions; PCSM also checks the feature compatibility version (FCV) on both clusters when it starts. A supported binary-version pair must also meet the FCV requirements in the [FCV section](#feature-compatibility-version-fcv).

At startup, PCSM rejects a binary-version downgrade, where the source major version is higher than the target's. It also rejects startup when the source FCV is higher than the target FCV, or when either cluster is changing its FCV.

## Supported scenarios

The compatibility matrix lists the MongoDB binary major-version combinations supported for synchronization.

In the current release, supported scenarios are:

- Both clusters run the same major version.
- The target cluster runs the next supported higher major version shown in the matrix.

Other combinations may start but are not tested or officially supported. PCSM rejects binary-version downgrade paths.

## Version compatibility matrix

| Source version | Target version | Supported | Notes |
|----------------|----------------|-----------|-------|
| 6.0.x | 6.0.x | **Yes** | The minimum supported version is 6.0.17 |
| 6.0.x | 7.0.x | **Yes** | — |
| 6.0.x | 8.0.x | **Yes** | — |
| 7.0.x | 7.0.x | **Yes** | — |
| 7.0.x | 8.0.x | **Yes** | — |
| 8.0.x | 8.0.x | **Yes** | — |
| 8.0.x | 7.0.x | **No** | Downgrade replication is not supported. |
| 7.0.x | 6.0.x | **No** | Downgrade replication is not supported. |
| Any higher version | Any lower version | **No** | Downgrade paths are not supported. |

Use only the version combinations listed as supported in the table above. Unsupported binary-version combinations may start successfully, but they are not tested or officially supported.

## Feature compatibility version (FCV)

Starting with PCSM 1.2.0, PCSM checks the FCV of both clusters when each PCSM process starts:

- The source FCV must be equal to or lower than the target FCV. PCSM rejects startup if the source FCV is higher.
- If the source FCV is lower than the target FCV, PCSM starts and logs a warning. You cannot reverse replication from the target to the source unless you raise the source FCV to the target FCV.
- PCSM rejects startup while either cluster is upgrading or downgrading its FCV. Complete the FCV change before starting PCSM. If the FCV change failed, resolve the MongoDB error and rerun the FCV command.
- PCSM compares FCV values numerically. For example, FCV 8.10 is higher than FCV 8.2.

PCSM checks FCV only when a process starts. It does not recheck running processes or repeat the check when an HA standby is promoted. If a PCSM process restarts while the source FCV is higher than the target FCV, it cannot start until the target FCV catches up.

## Limitations

For a full list of constraints that apply to this feature, see the [limitations](./limitations.md#cross-version-replication) section.
