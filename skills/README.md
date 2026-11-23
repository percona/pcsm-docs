# PCSM documentation testing skill

[Run Tests for feature documentation](run-tests-for-feature-documentation/SKILL.md)
helps documentation contributors verify a feature from its Jira ticket and implementation PR.
Tracking ticket: [PCSM-434](https://perconadev.atlassian.net/browse/PCSM-434) (fix version 1.2.0).

## Try the skill

Use the files from the PR branch, not the default branch until the PR is merged.
Download the branch archive from GitHub, or check out the PR in a separate documentation checkout.
The skill folder contains `SKILL.md`, `agents/openai.yaml`, and `references/pcsm-environment.md`;
keep all three files and their directory structure together.

From the root of that checkout, install a new local copy:

```sh
pcsm_skill_dir="${CODEX_HOME:-$HOME/.codex}/skills/run-tests-for-feature-documentation"
if [ -e "$pcsm_skill_dir" ]; then
  echo "A copy already exists at $pcsm_skill_dir; compare it with this PR before replacing it."
else
  mkdir -p "$(dirname "$pcsm_skill_dir")"
  cp -R skills/run-tests-for-feature-documentation "$pcsm_skill_dir"
fi
```

Use a Codex/Work session that can load the local skill and access Jira, GitHub,
a terminal, and Docker. A browser-only session without those capabilities cannot
run the local environment. The skill checks the selected revision's build dependencies.

Start with this prompt:

```text
Use $run-tests-for-feature-documentation for
https://perconadev.atlassian.net/browse/PCSM-398.
Review the linked code PR. Create fresh disposable source and target clusters.
Guide me through each test one at a time: explain what it checks, give the command
and expected output, and wait for my result before continuing.
Show the logs and final results. Do not modify the original Jira ticket or
development repository.
```

## Reviewer checklist

- [ ] The session loads this PR's skill and finds the implementation PR.
- [ ] It records the exact code commit and creates only isolated test resources.
- [ ] Commands and expected results are clear enough to follow one at a time.
- [ ] Results include final state and source/target data comparisons, with logs.
- [ ] Source Jira and development repository remain unchanged.
- [ ] Cleanup removes only the run's resources, or retained resources are listed.

Record the tested skill commit, product commit, environment, PASS/FAIL/BLOCKED results,
and any confusing steps in the PR review. Sanitize logs before sharing.
An unavailable tool or skipped test is a limitation, not a passing result.

## Existing evidence

See the [recorded test report and supporting logs](test-results/pcsm-398.md).

The original local skill was exercised with PCSM-398 and
[code PR #302](https://github.com/percona/percona-clustersync-mongodb/pull/302),
at commit `011505c03d6315b64b918b80bf6ffff772677cff`, using two three-member
replica sets with PSMDB 8.0.29-13.

Seven focused unit tests, the full race-enabled unit suite, and a targeted
pause/drain integration test passed. The manual crash/restart check restored
replication settings, resumed replication, and did not repeat the consumed
initial-sync pause during observation. Source and target contained 20,002
documents with matching collection checksums.

These are results from the earlier local run, not a fresh run of this PR.
HA failover, sharding, and other version combinations were not validated.
The repository's documentation CI does not execute the skill or prove its behavior;
use the checklist above for a fresh team evaluation.
