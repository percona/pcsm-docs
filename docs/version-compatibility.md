# Cross version replication


PCSM supports replication and synchronization from lower MongoDB major versions to higher major versions. This allows you to migrate or synchronize data during staged upgrades without requiring both clusters to run the same MongoDB version.

## Supported replication scenarios

PCSM supports synchronization when:

- The target cluster runs a newer major version than the source cluster
- Both clusters run the same major version and the target patch version is equal to or newer than the source patch version

PCSM blocks synchronization when the source cluster version is newer than the target cluster version.

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
