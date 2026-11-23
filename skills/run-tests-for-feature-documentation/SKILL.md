---
name: run-tests-for-feature-documentation
description: Create a disposable Percona ClusterSync for MongoDB (PCSM) test environment from a supplied Jira ticket and its linked development PR, run feature-focused tests, and capture verified behavior for feature documentation. Use for PCSM documentation testing and reproductions, not product-code fixes or documentation publication.
---

# Run Tests for feature documentation

Turn a Jira ticket into a reproducible PCSM test run and documentation evidence. Development repository: https://github.com/percona/percona-clustersync-mongodb/. Obtain the implementation PR from the ticket rather than asking the user to supply an already discoverable link.

## Input and scope

The required input is a Jira ticket key or URL. If absent, ask for it. Optional inputs are a documentation draft/example, desired MongoDB versions/topology, or an environment explicitly identified as disposable. Infer reasonable test choices from the ticket, implementation, and repository guidance.

Creating this skill is distinct from invoking it: do not provision an environment until a ticket is supplied for a test run.

Treat the original Jira ticket as read-only throughout this workflow. Do not edit its description or fields, change its status or assignee, add comments, attachments, links, labels, or work logs, or make any other ticket update. Keep test results and documentation findings in the chat and run artifacts, never on the original ticket.

Treat the development repository as read-only too. Do not edit its source, tests, documentation, configuration, or dependency/lock files; do not commit, push, create or change remote branches/tags, open or modify PRs/issues, post comments/reviews, or trigger repository workflows. Read/fetch the selected revision and run its existing build/tests in a disposable local copy. Keep custom reproductions, environment overrides, logs, and reports outside that copy. Generated binaries and caches may exist only as disposable execution artifacts; they must not change tracked files or be committed or uploaded to the repository. Report defects rather than fixing the development repository.

Use connected Jira and GitHub tools for discovery and the available execution host for builds and tests. If the host cannot run the required environment, complete source review and a concrete setup/test plan, report the missing capability, and ask only for the environment decision needed to proceed. Do not describe source inspection or existing CI results as tests executed in this run.

## Resolve the implementation

1. Read the ticket description, acceptance criteria, comments, linked issues, development links, and release fields. Separate intended behavior from unresolved discussion.
2. Follow development PR links targeting `percona/percona-clustersync-mongodb`. If links are absent, search that repository's PR titles and bodies for the exact ticket key and corroborate candidates against the ticket and changed code. Do not mistake a documentation PR for the implementation.
3. Always review the actual code PR alongside Jira before testing: read the implementation diff and affected code, added/changed tests, review comments and their resolutions, PR state, base/head refs and SHAs, and CI results. A PR title or description alone is insufficient. Map the implemented behavior to the ticket requirements and documentation claims, recording discrepancies and coverage gaps. If the user supplies a code PR, inspect it directly and verify its relationship to the ticket. Choose the backport matching the requested or ticket release. Ask only when ambiguity materially changes the test target. If multiple PRs jointly implement the feature, identify a revision containing them; do not silently combine unmerged branches.
4. Record ticket URL, PR URL, release, and exact commit under test. Use the observed head commit for an open PR. For a merged PR, use an available integration commit containing its changes and identify it explicitly. A closed unmerged PR is exploratory behavior, not a released feature.
5. Use a disposable local copy of the selected revision, leaving the user's existing development checkout untouched. Follow the host's worktree tools when applicable. Verify `git rev-parse HEAD` against the selected commit and record the initial tracked-file state. If the PR advances during testing, attribute results to the tested SHA rather than claiming coverage of the new head.

## Plan documentation checks

Read the selected revision's `AGENTS.md`, `CONTRIBUTING.md`, `Makefile`, dependency manifests, relevant CI workflows, and applicable nested guidance. Read [PCSM environment notes](references/pcsm-environment.md) before selecting and starting the topology. Revalidate those notes against the selected revision; release branches can differ.

Create a compact test matrix linking each documentation claim or acceptance criterion to preconditions, topology/versions, the exact user action, expected observable result, and the automated test or manual reproduction that verifies it.

Cover the normal path and feature-relevant defaults, option boundaries, error behavior, and limitations. Exercise cloning and ongoing replication when the feature affects both. Use sharding, HA, authentication/TLS, upgrades, or multiple version combinations when the ticket or documentation requires them. Do not infer support for untested combinations.

## Create the test environment

1. Check Git, make, the Go version required by `go.mod`, Docker daemon/Compose availability, and Python/Poetry requirements when using E2E tests. Check architecture, resources, and port/container-name conflicts. Use project-specific dependencies rather than changing unrelated projects.
2. Build the selected commit using the repository-supported target, normally `make build`, and verify `./bin/pcsm version`. Record build output and revision. Never silently substitute a released binary for the PR build.
3. Prefer repository topology tooling. Default to source and target replica sets; select sharding or HA when needed. Pin explicit MongoDB image versions appropriate to the release and record actual server versions and FCVs.
4. Inspect scripts, Compose configuration, fixtures, and resets before running them. Scripts can use fixed names and ports: a separate checkout does not isolate Docker resources. Use a dedicated host or verified collision-free resources. Do not stop or delete unrelated containers to make space.
5. Use synthetic data in disposable clusters created for this run. The Python E2E fixture can drop all non-system databases on source and target. Never point it at production, shared, or unverified user-provided URIs. If disposability is unclear, create new clusters or ask before destructive tests.
6. Configure hostname resolution and URIs for the actual process location. Prefer container/network-local resolution when practical. Preserve unrelated host settings if scoped host entries are needed. Bind test services locally or within the private test network.
7. Wait with diagnostic timeouts for MongoDB primaries and PCSM HTTP readiness. A process start message is insufficient. Verify the test binary and target connections, then seed small deterministic feature-specific data.

Keep a run directory outside the development checkout containing the environment manifest, exact commands, matrix, and sanitized output. Use external configuration overrides rather than editing repository files. Record resource names/IDs and ownership for scoped teardown. Keep credentials out of reports.

## Execute and investigate

- Run relevant existing unit, integration, and E2E tests supported by the revision. Begin with focused cases and honor applicable required repository checks. Report the chosen scope; focused tests are not a full regression pass.
- Exercise documented CLI/API steps against the PR build. Capture commands, meaningful output, state transitions, and source/target data or metadata comparisons. Compare actual contents, indexes, or options where relevant; counts alone are insufficient.
- For asynchronous behavior, use bounded waits. An accepted request does not prove the final state was reached.
- Mark each check PASS, FAIL, BLOCKED, or NOT RUN with evidence and a reason. Report skips separately. Preserve exit codes when logging through pipelines and use uncached runs when claiming fresh Go test execution.
- Preserve failure logs and distinguish environment errors from product behavior and documentation discrepancies. Fix routine setup problems and rerun affected checks. Stop repeating commands without new evidence or changed prerequisites.
- Create a minimal temporary reproduction outside the development checkout when existing tests miss the feature. Keep it with run artifacts. Do not modify product behavior or repository tests to force a pass. Both the original Jira ticket and the development repository remain read-only.

## Deliver and clean up

Return a concise report containing:

1. Ticket, implementation PR, tested commit, and release context.
2. Environment: host type, topology, PCSM build, MongoDB image/server versions and FCVs, relevant configuration.
3. Expected versus observed results and links to commands/output artifacts.
4. Documentation findings: verified steps/examples, prerequisites, defaults, limits, corrections, unresolved questions. Distinguish observation from source-based expectation.
5. Reproduction commands, cleanup status, remaining resources, and blocked checks.

Verify that build/test execution left tracked repository files unchanged. If a command unexpectedly changes them, report it and discard the disposable copy after preserving evidence externally; do not propagate those changes. Stop only processes and containers created for this run. Inspect cleanup scope before using repository helpers and verify teardown succeeded. Preserve reports/evidence and remove disposable cluster data by default. If the user asks to retain the environment, provide exact connection/start/stop details and resource ownership. Never reset state while a PCSM server using it is running.
