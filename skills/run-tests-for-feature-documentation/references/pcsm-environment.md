# PCSM environment notes

Checked against repository `main` on 2026-11-23. Re-read the selected PR revision before executing; flags, versions, paths, and behavior can differ across releases.

## Sources to inspect

- [CONTRIBUTING.md](https://github.com/percona/percona-clustersync-mongodb/blob/main/CONTRIBUTING.md): setup, hostname resolution, version selection, tests and CI scope.
- [Makefile](https://github.com/percona/percona-clustersync-mongodb/blob/main/Makefile): build/test targets.
- `go.mod`, `pyproject.toml`, `poetry.lock`: dependency versions.
- `hack/AGENTS.md`, `hack/util`, `hack/rs/`, `hack/sh/`, `hack/ha/`: topology and teardown.
- `tests/AGENTS.md`, `tests/conftest.py`, `tests/pcsm.py`, `tests/testing.py`: fixtures, options, process lifecycle, data comparisons.
- `pcsm/README.md`, `ha/README.md`: pipeline and HA behavior.
- `.github/workflows/go.yml`, `e2etests.yml`, `ci.yml`: versions and selections. External QA partitions are not MongoDB shard counts.

## Build and tests

At the observed revision, `make build` creates `bin/pcsm`; verify with `./bin/pcsm version`. `make test` runs race-enabled Go tests. `make test-integration` requires Docker and runs uncached integration tests. Focused fresh Go runs may use `go test -race -count=1 -run '<observed-test-name>' ./<package>`, adding the integration tag when needed. Replace placeholders with names discovered in the selected revision.

For Python E2E, install from the repository lockfile with `poetry install`. Select relevant modules/test IDs after inspecting their fixtures. Unqualified local pytest includes sharded tests, so it is not automatically suitable for replica sets. Slow tests require `--runslow` at the observed revision; HA tests also require the binary.

## Topology and connectivity

Observed topology entry points are `./hack/rs/run.sh` and `./hack/sh/run.sh`. `MONGO_VERSION` supplies a common image version; `SRC_MONGO_VERSION` and `TGT_MONGO_VERSION` override each side. Choose explicit versions from the selected revision and ticket rather than an evergreen version embedded in this skill.

For host-run PCSM at the observed revision:

| Topology | Source URI | Target URI |
| --- | --- | --- |
| Replica sets | `mongodb://rs00:30000` | `mongodb://rs10:30100` |
| Sharded | `mongodb://src-mongos:27017` | `mongodb://tgt-mongos:29017` |

Hostnames must resolve from the PCSM/test process and match advertised replica-set members. Target mongos uses host port 29017 but port 27017 within its container. Do not reuse host URIs inside a container without checking the network context. Source and target binary major versions and FCVs must satisfy the revision's compatibility checks.

Topology scripts use overlapping ports and fixed resources. Inspect existing containers before starting or switching topology. `./hack/cleanup.sh` can remove disposable data across multiple topologies and suppress teardown errors: inspect scope and verify removal. Stop owned HA/PCSM processes before clusters/networks. A new checkout does not prove cleanup targets belong to this run.

## E2E process management

Set `TEST_SOURCE_URI` and `TEST_TARGET_URI` to the verified disposable cluster URIs, `TEST_PCSM_URL` to the test server URL (normally `http://localhost:2242`), and `TEST_PCSM_BIN` to the absolute path of the binary built for this run. Verify current options and precedence in `tests/conftest.py`.

`TEST_PCSM_BIN` enables pytest-managed server startup and does not replace the required URL. Do not start a competing manual server. The autouse fixture drops non-system databases on both clusters; restrict this suite to owned disposable clusters. Record skips as unverified behavior.

## Readiness and evidence pitfalls

- Startup logging can precede socket binding. At the observed revision `/metrics` checks HTTP readiness on every HA role; `/status` can return 409 on STANDBY. Check the active role separately before feature operations.
- Pause acceptance may mean draining (`pausing`); wait for `paused` when that is the assertion. Finalization needs completion evidence as defined by the revision's lifecycle reference.
- Use deterministic data ordering/content comparison. A checkpoint alone does not prove all changes were applied.
- Never invoke `pcsm reset`, hidden resets, or `--reset-state` while any PCSM process using that target state is running. A fresh disposable environment usually avoids the need for resets.
- Existing CI success supplements evidence but does not prove a documentation example was exercised or that other versions/topologies are supported.
