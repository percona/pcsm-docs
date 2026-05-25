# Cross version replication

{{pcsm.full_name}} supports replication and synchronization from lower MongoDB major versions to higher major versions. This allows you to migrate or synchronize data during staged upgrades without requiring both clusters to run the same MongoDB version.

## Supported replication scenarios

{{pcsm.full_name}} supports synchronization when:

- The target cluster runs a newer major version than the source cluster
- Both clusters run the same major version and the target patch version is equal to or newer than the source patch version

## Version compatibility matrix

| Source version | Target version | Supported | Description|
| -------------- | -------------- | --------- | -----|
| 6.0.x          | 6.0.x          | Yes       | Supported when the target patch version is equal to or later than the source patch version |
| 6.0.x          | 7.0.x          | Yes       | Supported lower-to-higher major version replication                                        |
| 6.0.x          | 8.0.x          | Planned   | Future support for direct major-version upgrade replication                                |
| 7.0.x          | 7.0.x          | Yes       | Supported when the target patch version is equal to or later than the source patch version |
| 7.0.x          | 8.0.x          | Yes       | Supported lower-to-higher major version replication                                        |
| 8.0.x          | 7.0.x          | No        | Downgrade replication is not supported |
| 7.0.x          | 6.0.x          | No        | Downgrade replication is not supported|
| Higher version | Lower version  | No        | Synchronization is blocked automatically|

## Limitations

- Downgrade replication is not supported. {{pcsm.full_name}} blocks startup if the source major version is higher than the target major version.

- {{pcsm.full_name}} checks major versions only. It does not compare patch versions or validate the combination against a list of known-good pairings, so an unsupported combination can start without error. Only run the combinations listed in the version compatibility matrix.

- PCSM does not validate the Feature Compatibility Version (FCV) between source and target clusters. If the target's FCV is lower than the source's (e.g., after a rollback), {{pcsm.full_name}} will not recognize the mismatch. Manually verify FCV alignment before starting replication.

- Cross version replication on sharded clusters is not fully tested. Before using this combination in production, verify behavior in a staging environment that mirrors your production topology.

- Version compatibility is only checked at startup. PCSM performs the version check once when the server starts. This check is not repeated when replication is started or resumed.


