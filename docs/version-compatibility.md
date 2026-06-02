# Cross-version replication

{{pcsm.full_name}} (PCSM) supports replication only for the MongoDB major-version combinations listed in the compatibility matrix below. In the current release, this includes clusters running the same major version and selected lower-to-higher upgrade paths. This lets you synchronize data during a staged upgrade or maintain replication across clusters that run different versions where support is explicitly provided.

At startup, PCSM compares the source and target major versions. If the source major version is higher than the target's, PCSM rejects startup with `version check: source X > target Y: downgrade not supported` . All other combinations are allowed to start; combinations not listed in the matrix below are untested.

## Supported scenarios

PCSM supports synchronization only for version combinations explicitly marked as supported in the compatibility matrix below.

In the current release, supported scenarios are:

- Both clusters run the same major version.
- The target cluster runs the next supported higher major version shown in the matrix.

Other combinations may start but are not tested or officially supported. PCSM only explicitly rejects downgrades.

## Version compatibility matrix

| Source version | Target version | Supported | Notes |
|----------------|----------------|-----------|-------|
| 6.0.x | 6.0.x | **Yes** | — |
| 6.0.x | 7.0.x | **Yes** | — |
| 6.0.x | 8.0.x | **Yes** | — |
| 7.0.x | 7.0.x | **Yes** | — |
| 7.0.x | 8.0.x | **Yes** | — |
| 8.0.x | 7.0.x | **No** | Downgrade replication is not supported. |
| 7.0.x | 6.0.x | **No** | Downgrade replication is not supported. |
| Any higher version | Any lower version| **No** | Downgrade paths are not supported. |

Use only the version combinations listed as supported in the table above. Unsupported combinations may start successfully but are not tested or officially supported.

## Limitations

- **Feature Compatibility Version (FCV) is not automatically checked between your source and target clusters**

    PCSM does not automatically check the Feature Compatibility Version (FCV) between your source and target clusters. Because an incompatible FCV might cause replication failures, it is important to perform this check manually before you begin:

    Confirm the FCV for both your source and target clusters.
    Ensure the target cluster's FCV is equal to or higher than the source cluster's FCV.

- **Downgrade replication is not supported**

    PCSM blocks startup if the source major version is higher than the target major version.

