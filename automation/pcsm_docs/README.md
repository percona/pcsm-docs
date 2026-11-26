# PCSM documentation events

This workflow runs on GitHub-hosted runners with the Jira, GitHub, and OpenAI Responses APIs.
Configure a non-Codex model for documentation drafts.

## Event flow

Jira Automation dispatches a workflow when a ticket enters an eligible status.
The validation job checks board membership, Needs Doc, Fix version, and the last status transition.
The worker uses the exact Fix version name as the documentation branch.

A separate job researches the ticket and explicitly linked implementation PRs.
Two model passes draft and review edits to existing Markdown pages.
The worker builds baseline and updated documentation in containers without service credentials or network access.
A successful run creates a draft PR with a claim-to-source map and a verified Jira backlink.
The worker never merges PRs or changes Jira status.

Missing evidence, ambiguous releases, inaccessible attachments, and failed strict builds require manual review.
Changes that need additional pages or navigation also require manual review.

## Notifications

The worker posts the outcome on the documentation PR through the GitHub comments API.
The comment contains the Jira link, target release, review-request status, backlink status, and workflow-run link.
A failed run posts a blocked outcome if a verified documentation PR exists.

Progress and failures before PR creation appear in the GitHub Actions run summary.
The worker does not create a placeholder PR just to post a notification.

Each event has a stable comment marker.
The worker checks for that marker before the worker creates a comment.
An outcome change updates the same comment.
Completed-event replay creates no additional comment.
A different eligible event can add its own outcome comment to the same PR.

Subscribe to the PR or watch the repository to receive GitHub notifications.
Email delivery depends on your [GitHub notification settings](https://docs.github.com/en/subscriptions-and-notifications/get-started/configuring-notifications).
The worker requires no SMTP service, mail credentials, sender address, or recipient configuration.
Remove the former `PCSM_SMTP_*` variables and secrets if present.

## Repository configuration

Keep the Jira rule and both activation flags disabled until the acceptance test succeeds.
Configure credentials through your approved secret-management process.
Do not place credentials in tickets, source files, or dispatch payloads.

| Repository variable | Purpose |
| --- | --- |
| `PCSM_BOARD_FILTER_ID` | Saved filter ID for board 141. The worker verifies the match against Jira. |
| `PCSM_DOCS_ENABLED` | Production activation flag. Leave `false` or unset during setup. |
| `PCSM_DOCS_TEST_ENABLED` | Controlled-test activation flag. Leave `false` or unset during setup. |
| `PCSM_DOCS_TEST_ISSUE` | Approved test ticket key, required for `test-pr` mode. All other tickets are rejected in that mode. |
| `PCSM_DOCS_APP_ID` | GitHub App ID, installed on `percona/pcsm-docs`. |
| `PCSM_DOCS_MODEL` | Approved non-Codex OpenAI model with Responses structured-output support. |
| `PCSM_COPILOT_REVIEWER` | Optional reviewer login supported by the repository. The outcome comment reports request status. |

| Repository secret | Purpose |
| --- | --- |
| `PCSM_JIRA_EMAIL`, `PCSM_JIRA_API_TOKEN` | Jira service identity with board, filter, ticket, history, and comment access; permission to add a remote link. |
| `PCSM_DOCS_APP_PRIVATE_KEY` | GitHub App installation token generation. Grant Contents and Pull requests write permissions on this repository. |
| `PCSM_SOURCE_TOKEN` | Optional read-only credential for the implementation repository. |
| `PCSM_OPENAI_API_KEY` | API project with permission to process the selected ticket and code evidence. |

Pull requests write permission covers outcome comments through the GitHub issue-comments API.
Model usage has a limit of two requests per draft attempt, with 12,000 output tokens per request.
The workflow timeout is 45 minutes.
Configure an API project budget separately.

### Release selection

The ticket must have exactly one Fix version.
The worker uses that exact name as the target documentation branch for every release.
No release number or release-to-branch mapping belongs in workflow configuration.
The worker ignores the former `PCSM_RELEASE_BRANCHES` configuration.

The branch owner prepares the matching branch and verifies its release content and metadata before processing.
The worker checks branch existence and uses the returned commit for drafts and builds.
The worker does not create release branches or fall back to `main`.

Missing or multiple Fix versions stop validation.
A missing or inaccessible matching branch also stops validation.
Before publication and PR follow-ups, the worker rechecks eligibility, Fix version, target branch, and commit.
Any change stops the attempt.

The dispatch `ref: main` selects workflow code.
The generated documentation PR targets the ticket's Fix version branch.

## Jira rule and API destination

Use an event rule for board 141 with Needs Doc = Yes.
The worker accepts `In QA` (status ID `10045`) and `In Doc` (status ID `10043`).
The Needs Doc field is `customfield_10066`.
Confirm these IDs and the board filter during provisioning.
The rule needs no schedule or separate email action.

Restrict the controlled-test rule to the ticket configured in `PCSM_DOCS_TEST_ISSUE`.
The ticket must contain an explicit implementation PR link in its description, comments, or remote links.
The worker does not follow related Jira issues to discover implementation PRs.

After the workflow reaches `main`, open the [workflow page](https://github.com/percona/pcsm-docs/actions/workflows/pcsm-documentation.yml).
Jira must send requests to the dispatch API, not the workflow page:

```text
POST https://api.github.com/repos/percona/pcsm-docs/actions/workflows/pcsm-documentation.yml/dispatches
```

Use `Accept: application/vnd.github+json`, `Content-Type: application/json`, and a hidden `Authorization: Bearer <dispatch-credential>` header.
The dispatch credential requires Actions write access to this repository.
For GitHub App tokens, configure token renewal through an approved integration.
Do not paste an App private key into Jira's Authorization header.

Create a Jira Automation variable named `eventPayload` from [jira-event.json.template](jira-event.json.template).
The template includes JSON-escaped status names and a stable event ID.
Use [jira-dispatch.json.template](jira-dispatch.json.template) as the request body:

```json
{
  "ref": "main",
  "inputs": {
    "mode": "validate",
    "event_json": {{eventPayload.asJsonString}}
  }
}
```

Capture transition values before any issue refresh or edit that changes `issue.updated`.
Retries must reuse the captured event body and ID.
Verify the rendered JSON in Jira's audit log during the controlled test.
Local fixtures cannot verify Jira smart-value expansion.
An accepted dispatch confirms request acceptance; inspect the GitHub run for the result.

## Acceptance test

1. Merge the reviewed workflow to `main` with both activation flags false and the Jira rule disabled.
   Select Run workflow, mode `self-test`, and event JSON `{}`.
   Fixture tests require no service credentials or external writes.

2. Configure Jira credentials and the board filter.
   Choose an approved test ticket and set `PCSM_DOCS_TEST_ISSUE` to its key.
   Coordinate a genuine eligible transition and capture its rendered event.
   Run `validate` with that event.
   Wrong-board, Needs Doc No, stale, and mismatched events must fail without writes.

3. Configure the remaining credentials and model.
   Confirm the test ticket contains a relevant implementation PR link and exactly one Fix version.
   Verify that the matching documentation branch exists with appropriate release content.
   Set `PCSM_DOCS_TEST_ENABLED` to `true`; leave `PCSM_DOCS_ENABLED` false.

4. Run `test-pr` with the verified event.
   Inspect the resulting draft PR, source map, target branch, Jira backlink, and outcome comment.
   The PR title includes `[TEST]` and its description says Do not merge.
   Verify that the comment links to the workflow run and reflects the review-request status.

5. Replay the same event.
   Confirm that the worker returns the same PR without another model request or comment.
   Other tickets must fail in `test-pr` mode.
   A production PR must not serve as a test PR.

6. Test the Jira rule with its temporary test-ticket restriction and request mode `test-pr`.
   Coordinate activation and a fresh transition.
   Inspect the Jira audit log and GitHub run.
   Disable the rule and reset `PCSM_DOCS_TEST_ENABLED` to false after the test.
   Do not merge the test PR.

7. Obtain the documentation owner's approval for production activation after the controlled test succeeds.
   Remove the temporary ticket restriction, select `process`, and set `PCSM_DOCS_ENABLED` to true.

Publication of workflow code does not activate the Jira rule or either processing mode.

## Replay and recovery

Event checkpoints use the `automation/pcsm-event-state` branch and a hash of event ID and mode.
Checkpoints contain outcome stages, run IDs, and public PR or comment URLs.
Private ticket descriptions and model evidence stay in the runner's temporary directory.
Protect the state branch from deletion and restrict edits to automation owners.

An atomic `automation/pcsm-lock-pcsm-<number>` Git ref serializes each ticket across test and production modes.
Concurrent runs for the same ticket stop for operator review.
Deterministic checkpoint writes reconcile shared-branch conflicts with bounded retries.
They do not retry PR or comment creation.

The duplicate check requires the ticket key at the start of the PR title, after any `[TEST]` prefix.
A ticket mentioned only in the PR description does not establish ownership.
Matches must use the exact release branch and test mode.
Multiple matches or a matching PR closed without merge require manual review.

An interrupted attempt keeps its lock.
Inspect its workflow run, checkpoint, branch, PRs, Jira links, and event-marked comment before replay.
A timed-out comment write triggers a read to check whether GitHub accepted the comment.
An unverified write requires reconciliation; the worker does not blindly create another comment.
Reconcile the checkpoint before removing a stale lock, and confirm that no run is active.

If no verified PR exists, use the run summary for failure details.
A failed comment request leaves the verified PR intact and the run blocked for review.
A review-request failure appears in the outcome comment and checkpoint.

References:

- [Workflow dispatch API](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event)

- [Issue and PR comments API](https://docs.github.com/en/rest/issues/comments)

- [GitHub Actions job summaries](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#adding-a-job-summary)

- [Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create)
