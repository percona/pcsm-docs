# Cross-version replication

{{pcsm.full_name}} (PCSM) supports replication only for the MongoDB major-version combinations listed in the compatibility matrix below. In the current release, this includes clusters running the same major version and selected lower-to-higher upgrade paths. This lets you synchronize data during a staged upgrade or maintain replication across clusters that run different versions where support is explicitly provided.

PCSM checks the major version relationship between source and target at startup. If the source major version is higher than the target major version, PCSM blocks startup and exits with an error.

## Supported scenarios

PCSM supports synchronization only for version combinations explicitly marked as supported in the compatibility matrix below.

In the current release, supported scenarios are:

- Both clusters run the same major version.
- The target cluster runs the next supported higher major version shown in the matrix.

PCSM blocks synchronization in all cases where the source major version is higher than the target major version. Non-downgrade combinations that are not listed as supported in the matrix are not supported in the current release.

## Version compatibility matrix

| Source version | Target version | Supported | Notes |
|----------------|----------------|-----------|-------|
| 6.0.x | 6.0.x | **Yes** | — |
| 6.0.x | 7.0.x | **Yes** | — |
| 6.0.x | 8.0.x | **Planned** | Not available in the current release. Use the upgrade path: 6.0 → 7.0 → 8.0 |
| 7.0.x | 7.0.x | **Yes** | — |
| 7.0.x | 8.0.x | **Yes** | — |
| 8.0.x | 7.0.x | **No** | Downgrade replication is not supported. |
| 7.0.x | 6.0.x | **No** | Downgrade replication is not supported. |
| Any higher | Any lower | **No** | All downgrade paths are blocked. |

Use only the version combinations listed as supported in the table above. Unsupported combinations may start successfully but are not tested or officially supported.

## Limitations

- **The version check is major-only**

    PCSM validates only MongoDB major versions. It does not compare patch versions or validate combinations against a certified compatibility list.

    Verify patch-level compatibility before deploying mixed-version environments.

- **Feature Compatibility Version (FCV) is not validated**

    PCSM does not compare the Feature Compatibility Version (FCV) values of the source and target clusters.

    If the target cluster FCV is lower than the source cluster FCV, replication issues may occur and PCSM will not detect the mismatch automatically.

    Before starting replication:

    - Verify the FCV on both clusters
    - Ensure the target cluster FCV is equal to or higher than the source cluster FCV

- **Downgrade replication is not supported**

    PCSM blocks startup if the source major version is higher than the target major version.


- **Version compatibility is checked only at startup** 

    PCSM performs the version check once when the server starts. This check is not repeated when replication is started or resumed.

