# PCSM-398 test results

Recorded on **23 November 2026**. These results come from the earlier local
evaluation of the skill, before this documentation PR. Publishing the evidence
does not rerun the tests or demonstrate a fresh team evaluation.

- Requirement: [PCSM-398](https://perconadev.atlassian.net/browse/PCSM-398).
- Implementation: [PR #302](https://github.com/percona/percona-clustersync-mongodb/pull/302).
- Product commit: `011505c03d6315b64b918b80bf6ffff772677cff`.
- Environment: Linux ARM64 containers on Docker Desktop, Go 1.27.0,
  two three-member replica sets, PSMDB 8.0.29-13, FCV 8.0.
- Release context: Jira targets 1.2.0. The source-built binary identifies itself
  as v1.1.0 plus commit 011505c; it is not a released 1.2.0 package.

## Results

| Check | Result | Evidence |
| --- | --- | --- |
| Seven focused feature unit tests | PASS | [Unit log](pcsm-398/linux-feature-unit-tests.log) |
| Full Go unit suite with race detection | PASS | [Suite log](pcsm-398/linux-all-unit-tests.log) |
| HTTP pause waits for the target write to finish | PASS | [Integration log](pcsm-398/pause-integration.log) |
| Automated live scenario, 13 assertions | PASS | [Results and observed values](pcsm-398/live-results.json) |
| Subsequent guided manual crash/restart | PASS for observed recovery and data checks | [Recovery log excerpt](pcsm-398/manual-recovery-excerpt.log) |
| Build and automated test process exit codes | All 0 | [Exit codes](pcsm-398/execution-exit-codes.txt) |

The seven focused tests are also included in the full unit suite.
Packages marked `[no test files]` or `[no tests to run]` are not additional test passes.

## Automated test commands

Run these from a disposable checkout of the product commit with its required
Go toolchain. The recorded execution used a read-only source mount and external
build caches. Integration execution also required access to Docker; its container
used `TESTCONTAINERS_HOST_OVERRIDE=host.docker.internal`.

```sh
# Focused feature tests
go test -race -count=1 -timeout=5m -v ./pcsm \
  -run 'Test(RecoverRunOptions|CheckpointKeepsAutoTuning|RunOptionsKeepEveryOption|RecoverOldCheckpointUsesDefaults|StatusReportsPauseOnInitialSync|PauseOnInitialSync)'

# Full unit suite
go test -race -count=1 -timeout=5m ./...

# Targeted integration test
MONGO_VERSION=8.0.29-13 go test -race -count=1 -tags=integration \
  -timeout=5m -v . -run '^TestPauseHTTPReportsDrainingUntilTargetWriteCompletes$'
```

The focused log records these seven tests:

- `TestRecoverRunOptions`
- `TestCheckpointKeepsAutoTuning`
- `TestRecoverOldCheckpointUsesDefaults`
- `TestRunOptionsKeepEveryOption`
- `TestStatusReportsPauseOnInitialSync`
- `TestPauseOnInitialSyncPausesOnce`
- `TestPauseOnInitialSync_DoesNotJoinOwnExecution`

## Live behavior

1. Seeded 20,000 synthetic documents on the source.
2. Started PCSM with 2 replication workers, bulk size 100,
   collection bulk writes enabled, and `pauseOnInitialSync: true`.
3. Observed initial sync finish and state `paused`; the pending-pause flag disappeared.
4. Resumed replication and inserted a document before the crash.
5. Killed PCSM with SIGKILL and restarted without the original worker environment
   setting, a new `/start` request, or a state reset.
6. Observed recovery restore 2 workers, bulk size 100, and collection bulk writes.
7. Inserted another document after restart and verified it reached the target.

The automated scenario observed no repeated automatic pause during its
12-second post-recovery observation window. The later guided manual run also
restored the settings and replicated the `after-restart` document.

| Final collection evidence | Source | Target |
| --- | --- | --- |
| Document count | 20,002 | 20,002 |
| Collection checksum | `36bdb31c133a2543c8b7396be33d43e7` | `36bdb31c133a2543c8b7396be33d43e7` |

Counts represent 20,000 original documents plus one before and one after restart.
Matching collection checksums establish more than matching counts. The automated
JSON contains the recorded comparison; the manual run independently produced
the same counts and checksum.

## Documentation finding

The automatic-pause flag disappears when PCSM accepts the pause. Wait for
`state: "paused"` to confirm that draining has finished. The live automatic-pause
sample did not capture the short intermediate state; the separate integration
test held a target write to verify `pausing` before `paused`.

## Limits and provenance

- Not run locally: multi-instance HA takeover, sharding, lease/network failures,
  cross-version upgrades, the complete Python E2E suite, or the full version matrix.
- Existing PR CI results are separate historical evidence, not new local tests.
- Initial compiler/toolchain and HTTP readiness setup errors were resolved before
  the successful runs. The selected logs show the successful attempts.
- The original ticket, product PR, and tracked development source remained unchanged.
- The automated run's disposable clusters were removed. A later manual session
  recreated the lab; this report does not claim that session has been cleaned up.
- Published evidence removes terminal color escapes and redacts the local username
  path in the integration log. The manual recovery file is an excerpt; other
  included test logs preserve their recorded output.
