# PCSM documentation events without Codex

This workflow uses GitHub-hosted runners, direct Jira/GitHub/SMTP APIs and the OpenAI
Responses API with an explicitly configured non-Codex model. It does not run Codex,
depend on a Mac, use a ChatGPT subscription/session, or expose a tunnel.

**Deployment status: proposed implementation. Keep the Jira rule disabled.**
Configuration, a merge to `main`, a successful self-test and a controlled live test
are required before calling this deployed and verified. A PR or source-file link
is not a deployed workflow link. Creating the workflow does not supply credentials.

## Event flow

Jira Automation sends an authenticated workflow-dispatch request to GitHub. A
validation job checks the source, current board filter, Needs Doc, Fix version,
existing documentation branch and latest status transition. A separate gated job
researches the ticket and explicitly linked implementation PRs, drafts exact edits,
performs a second model review, builds the baseline and updated docs in a network-isolated
container without service credentials, and opens a draft PR with a claim-to-source map.
It adds a Jira backlink and sends start/end notifications to `rasika.chivate@percona.com`.
It never merges or changes Jira status.

The initial worker only edits existing Markdown pages. New pages/navigation,
missing evidence, ambiguous releases, inaccessible attachments, oversized evidence
or failing strict baseline builds require manual follow-up; it does not publish a
placeholder documentation PR. Markdown rendering can execute Jinja code, so builds
run without service credentials or network access.

## Verified setup facts (25 November 2026)

The Jira API confirms board 141 uses saved filter **13034** (name `PCSM`). Its
stored JQL is `project = 10120 ORDER BY Rank ASC`; project 10120 is PCSM, so this
is equivalent to `project = PCSM ORDER BY Rank ASC`. Board columns confirm
`In QA` = `10045` and `In Doc` = `10043`. The ticket metadata confirms
`Needs Doc` is `customfield_10066`.

PCSM-436 currently has Needs Doc = Yes, Fix version 1.2.0 and status Open.
It needs a fresh, coordinated qualifying transition before event validation can
pass. Its description references PCSM-398; this first worker does not follow
other Jira issues automatically. Add the verified implementation PR URL to the
test ticket before processing, or extend and review evidence collection first.
Do not transition the ticket just to manufacture a payload during setup.

The GitHub API shows only `main.yml` in the default branch's `.github/workflows`
directory. `pcsm-documentation.yml` is prepared locally, not deployed. HD-33020
is the original IT request with the Mac endpoint; this package replaces that
destination with GitHub dispatch. HD-33159 requests a separate Percona PCSM Docs Automation app installed on
`percona/pcsm-docs`, with Contents and Pull requests write permissions and the
`PCSM_DOCS_APP_PRIVATE_KEY` repository secret. Its latest visible status is
Waiting for support; app provisioning is not evidence of workflow deployment.

## IT configuration

Configure repository variables and secrets through the approved IT secret-management
process. Never paste credentials in tickets, chat, source files or dispatch payloads.
The GitHub workflow page is a viewing link; Jira must POST to the API endpoint below.

| Repository variable | Required value |
| --- | --- |
| `PCSM_BOARD_FILTER_ID` | `13034`, verified against board 141 on 25 November 2026 |
| `PCSM_RELEASE_BRANCHES` | JSON mapping of exact Jira Fix versions to reviewed, existing documentation branches |
| `PCSM_DOCS_ENABLED` | Leave `false` or unset during setup |
| `PCSM_DOCS_TEST_ENABLED` | Leave `false` until IT is ready for the PCSM-436 test |
| `PCSM_DOCS_APP_ID` | Percona-owned GitHub App ID, installed on `percona/pcsm-docs` |
| `PCSM_DOCS_MODEL` | Approved non-Codex OpenAI model supporting Responses structured outputs |
| `PCSM_SMTP_HOST`, `PCSM_SMTP_PORT` | Approved SMTP submission host and STARTTLS port (default 587) |
| `PCSM_SMTP_FROM` | Sender address authorized by the SMTP service |
| `PCSM_COPILOT_REVIEWER` | Optional reviewer login supported by the repository; failure is reported separately |

`main` currently advertises release 1.1.0. Branch `1.2.0` exists, but its
`variables.yml` still advertises 1.1.0. Confirm that release mapping with the docs
owner before configuring it. The worker never creates a missing release branch.

| Repository secret | Purpose |
| --- | --- |
| `PCSM_JIRA_EMAIL`, `PCSM_JIRA_API_TOKEN` | Service identity with board/filter/ticket/history/comment access and permission to add a remote link |
| `PCSM_DOCS_APP_PRIVATE_KEY` | App installation token generation for the docs repository only; Contents and Pull requests write permissions |
| `PCSM_SOURCE_TOKEN` | Optional separate read-only credential if the implementation repository requires authentication |
| `PCSM_OPENAI_API_KEY` | Approved API project with billing and permission to process the selected ticket/code evidence |
| `PCSM_SMTP_USER`, `PCSM_SMTP_PASSWORD` | Authorized SMTP sender credentials |

Do not copy the Mac's session files or local keychain credentials. IT must provision
the service identities, API budget and intended access. No live model calls or
emails are performed by the fixture tests. Model usage is limited to two requests
per drafting attempt, each with at most 12,000 output tokens. The workflow timeout
is 45 minutes. Configure a project spending limit independently.

## Jira rule and API destination

Keep the board/status/Needs Doc conditions from HD-33020. Do not enable a schedule.
Use status IDs 10045 (In QA) and 10043 (In Doc), verified against board 141.
Keep the project rule **Trigger PCSM documentation PR** disabled initially.
The rule condition is:

```jql
filter = 13034 AND cf[10066] = "Yes" AND status in ("In QA", "In Doc")
```

For the controlled live test, additionally restrict the rule to `key = PCSM-436`.
No scheduler or separate Jira email action is needed.

Once merged into the default branch, the workflow viewing link is:

`https://github.com/percona/pcsm-docs/actions/workflows/pcsm-documentation.yml`

This is the intended link, not evidence that deployment has happened. Verify it
opens and displays successful runs before sharing it as deployed.

Jira's Send web request destination is:

`POST https://api.github.com/repos/percona/pcsm-docs/actions/workflows/pcsm-documentation.yml/dispatches`

Use `Accept: application/vnd.github+json`, `Content-Type: application/json`, and a
hidden `Authorization: Bearer <IT-managed GitHub dispatch credential>` header.
This credential needs Actions write access to this repository. It is not the old
webhook bearer token. GitHub App installation tokens expire; IT must arrange token
minting/refresh through an approved integration if using them for Jira dispatch.
Do not paste an App private key into Jira's Authorization header.

Create a Jira Automation variable named `eventPayload` from
[`jira-event.json.template`](jira-event.json.template). It preserves the original
HD-33020 event contract, with JSON-escaped status names and a stable event ID.
Use [`jira-dispatch.json.template`](jira-dispatch.json.template) as the Send web
request custom body (shown below). These are Jira templates, not rendered JSON
files; do not dispatch the literal smart values.

Capture the transition values when the rule fires, before any re-fetch or edit
step that might change `issue.updated`. Retried deliveries must reuse that captured
event body and ID. Verify the actual rendered smart values in a controlled Jira
run; local fixture tests cannot verify Jira's runtime template expansion.

Dispatch body:

```json
{
  "ref": "main",
  "inputs": {
    "mode": "validate",
    "event_json": {{eventPayload.asJsonString}}
  }
}
```

Verify the rendered JSON in Jira's audit log. An accepted dispatch only means
GitHub accepted a request; inspect its run to determine the actual outcome.
Do not use the workflow page URL or the old `/v1/pcsm/documentation-events` path
as the request destination. No direct compatibility with the old receiver body
is claimed: the event must be wrapped in `inputs.event_json` as shown.

## IT acceptance test

1. Merge the reviewed workflow and worker to `main`. Keep both activation variables
   false and the Jira rule disabled. Open the workflow page and use **Run workflow**,
   mode `self-test`, event JSON `{}`. The tests must pass; no service credentials,
   draft PRs, model calls or emails are used in this mode.
2. Configure the Jira credentials and confirmed filter/release mapping. Coordinate
   one genuine transition on PCSM-436 and capture its rendered event. Run mode
   `validate` with that event. Check eligibility and history verification pass.
   Wrong-board, Needs Doc No, stale and mismatched events must fail with no writes.
3. Configure the remaining service credentials. Set only `PCSM_DOCS_TEST_ENABLED`
   to `true`; leave `PCSM_DOCS_ENABLED` false. PCSM-436 must contain an explicit link
   to a relevant implementation PR, and its Fix version must have a reviewed base.
4. Run mode `test-pr` with the verified event. This intentionally creates a real
   `[TEST] PCSM-436` **draft documentation PR**, marked **Do not merge**, adds a Jira
   backlink and sends start/end notifications. Inspect its actual documentation
   diff, source map, base branch, build result and notification acceptance.
5. Replay the identical event. The same PR must be returned with no extra email.
   A different legitimate transition for PCSM-436 reuses the existing test PR;
   event-level notifications may occur once for that new event. Other tickets
   are rejected in test-PR mode. A real, non-test PR is not reused as the test PR.
6. For a Jira-driven test, temporarily restrict the disabled rule to `key = PCSM-436`,
   set its request mode to `test-pr`, and coordinate enabling it and performing a
   fresh transition. Verify the audit result and the GitHub run. Disable the rule
   after the test and reset `PCSM_DOCS_TEST_ENABLED` to false. Do not merge the test PR.
7. Production activation is a separate coordinated step: remove the temporary
   ticket restriction, use mode `process`, and set `PCSM_DOCS_ENABLED` true only
   after the test succeeds and the docs owner approves activation.

No test ticket transition, credential installation, email, test PR or Jira rule
activation is performed merely by publishing this implementation PR.

## Replay, failures and recovery

Event checkpoints are committed to `automation/pcsm-event-state`, keyed by an
opaque hash of event ID and mode. Only digests, stages, run IDs and public PR URLs
are persisted there; ticket descriptions and model evidence remain in the runner's
temporary directory and are not uploaded as artifacts or printed to build logs.
Protect this branch from deletion and restrict changes to the automation owners.

An atomic `automation/pcsm-lock-pcsm-<number>` Git ref serializes each ticket across
test and production runs. A concurrent run fails visibly and requires replay; this
implementation is not an automatically retrying durable job queue. Completed events
deduplicate before drafting. Same-ID/different-payload requests are rejected.
Existing PRs are checked in all states, scoped to the exact documentation base.

On interruption or error the lock remains. Do not blindly re-run blocked events.
The operator must inspect the recorded run, deterministic head branch, all-state
PRs, Jira remote links and SMTP delivery logs. Resolve uncertain writes, reconcile
the checkpoint, then remove the stale lock only when no run is active. A blocked
checkpoint is not automatically reset. SMTP `sending`/`unverified` stages are not
resent automatically, because SMTP cannot guarantee exactly-once delivery.

If Copilot review cannot be requested, the verified draft PR remains and the
checkpoint records the limitation. Email acceptance is not proof of inbox delivery.
Never delete state/locks to force a new test PR without reconciling existing work.

References: [workflow dispatch API](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event),
[workflow triggers](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow),
[Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create).
