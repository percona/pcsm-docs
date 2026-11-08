# Upgrade Percona ClusterSync for MongoDB

Choose the upgrade procedure for your current Percona ClusterSync for MongoDB (PCSM) version. This page covers upgrading PCSM itself, not upgrading MongoDB on the source or target cluster.

| Current PCSM version | Upgrade path |
| --- | --- |
| Earlier than 1.0.0, including 0.9.0 | [Reset the stored replication state and start a new synchronization run](#upgrade-from-pcsm-earlier-than-100). This also applies when upgrading directly to 1.1.0. |
| 1.0.0 or later | [Retain replication state when the target release has no incompatible changes](#upgrade-from-pcsm-100-or-later). Review the release notes before each upgrade. |

## Before you start

1. Check your current PCSM version:

    ```{.bash data-prompt="$"}
    $ pcsm version
    ```

2. Read the [release notes](release-notes.md) for the target version and any versions you skip. Check for changes that require a reset or additional upgrade steps.
3. Save your PCSM startup parameters and the parameters used to start the synchronization run, including connection settings for both clusters, namespace filters, and any other run options. Reuse these parameters after the upgrade unless the target release requires a change.
4. Plan an interruption to synchronization. Non-disruptive upgrades are not tested or recommended. Stop all PCSM instances that use the target cluster before replacing them, including standby instances in a high-availability deployment.

## Upgrade from PCSM earlier than 1.0.0

PCSM 1.0.0 introduced a replication-state compatibility boundary. State created by an earlier version must not be reused when upgrading across that boundary. For example, upgrading directly from PCSM 0.9.0 to 1.1.0 requires the same reset as upgrading from 0.9.0 to 1.0.0.

A reset removes the stored PCSM replication state. The next synchronization run begins with a full initial clone.

!!! warning "A new run overwrites selected target collections"

    Starting the new synchronization run drops and recreates the target collections selected for replication. Preserve any data you need before starting the run. Do not run the earlier and newer PCSM versions against the same target cluster at the same time.

To upgrade:
{.power-number}

1. Stop all PCSM instances that use the target cluster. For a systemd service, run the following command on each PCSM host:

    ```{.bash data-prompt="$"}
    $ sudo systemctl stop pcsm
    ```

    For containers or manually started processes, stop every instance using your deployment's process manager.

2. Install the target PCSM version using your installation method: [packages](install/repos.md), [Docker](install/docker.md), [binary tarballs](install/tarball.md), or [source](install/source.md). Keep all instances stopped until the reset is complete.

3. Use the new PCSM binary to [reset the stored state](pcsm-commands.md#reset) on the target cluster:

    ```{.bash data-prompt="$"}
    $ pcsm reset --target "<target-mongodb-uri>"
    ```

    Replace `<target-mongodb-uri>` with your target connection string. Run the reset only while every PCSM instance using that target is stopped.

4. [Start the upgraded PCSM instances](install/start-pcsm.md) with the same startup parameters you saved before the upgrade.
5. [Start a new synchronization run](install/usage.md#start-the-replication) with the same run parameters you used before the upgrade, including namespace filters and any other run options. The following example is only for an unfiltered run with default options:

    ```{.bash data-prompt="$"}
    $ pcsm start
    ```

    In a high-availability deployment, send the command to the active instance.

6. Check progress with `pcsm status` on the active instance. Expect a full initial clone before ongoing replication resumes.

## Upgrade from PCSM 1.0.0 or later

Upgrades that do not introduce incompatible replication-state changes are expected to retain the existing state. In particular, upgrading from PCSM 1.0.0 to 1.1.0 does not require the reset needed for versions earlier than 1.0.0. This does not guarantee state compatibility for every future release; follow the target release's upgrade requirements.

State compatibility does not make an upgrade non-disruptive. Non-disruptive upgrades are not tested or recommended. Use a planned stop and restart, and verify the recovered synchronization state.

To upgrade while retaining state:
{.power-number}

1. If a synchronization run is in progress, wait for the initial clone to finish. An interrupted initial clone cannot resume from its partial progress. See [recovery during the initial clone](troubleshooting.md#recover-pcsm-during-initial-data-clone).
2. Ensure that the [source oplog retains enough history](oplog-sizing.md) for the interruption. Replication cannot resume from a checkpoint whose required source history is no longer available.
3. Stop all PCSM instances that use the target cluster, including standby instances. For systemd deployments, run `sudo systemctl stop pcsm` on each host.
4. Install the target PCSM version on every instance. Keep the existing connection settings and stored replication state. **Do not run `pcsm reset`** for this upgrade path.
5. [Restart PCSM](install/start-pcsm.md) with the same startup parameters you saved before the upgrade. If the checkpoint records a running replication phase, PCSM resumes it automatically. `pcsm start` does not resume an existing run and is rejected while that run is running, paused, or finalizing.
6. Check `pcsm status` on the active instance and inspect the [logs](logging.md). If the recovered run is paused, use [`pcsm resume`](pcsm-commands.md#resume) when you are ready to continue. If the recovered state is `finalizing`, run `pcsm finalize` again to complete the interrupted finalization. If recovery fails, follow the [troubleshooting guide](troubleshooting.md) before deciding whether a reset and full clone are necessary.
