import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import worker as w


def event():
    return {'schema_version': 1, 'event_id': 'pcsm-12345-1795608000000-10045',
            'event_type': 'jira.issue.status_changed', 'site_url': w.SITE, 'board_id': 141,
            'issue_key': 'PCSM-436', 'occurred_at_ms': '1795608000000',
            'transition': {'from_id': '10001', 'to_id': '10045', 'from_name': 'In Progress', 'to_name': 'In QA'}}


class Guards(unittest.TestCase):
    def verification_fixture(self, event):
        issue = {'key': 'PCSM-436', 'id': '12345', 'fields': {
            'customfield_10066': {'value': 'Yes'}, 'status': {'id': '10045'},
            'fixVersions': [{'name': '1.2.0'}], 'issuetype': {'name': 'Task', 'subtask': False}}}
        from datetime import datetime, timezone
        created = datetime.fromtimestamp(int(event['occurred_at_ms']) / 1000, timezone.utc).isoformat()
        history = {'id': '42', 'created': created, 'items': [{'field': 'status',
            'from': '10001', 'to': '10045', 'fromString': 'In Progress', 'toString': 'In QA'}]}
        return issue, history

    def verify_fixture(self, issue, history, event=None, filter_id=13034):
        with patch.dict(os.environ, {'PCSM_BOARD_FILTER_ID': '13034'}), \
                patch.object(w, 'jira', side_effect=[{'filter': {'id': filter_id}}, {'issues': [issue]}]), \
                patch.object(w, 'gh', return_value={'commit': {'sha': 'base'}}), \
                patch.object(w, 'paged_jira', return_value=[history]):
            return w.verify(event or globals()['event']())

    def test_authoritative_jira_verification(self):
        e = event()
        issue, history = self.verification_fixture(e)
        verified = self.verify_fixture(issue, history)
        self.assertEqual((verified['base'], verified['history_id']), ('1.2.0', '42'))

    def test_fix_version_is_the_exact_target_branch(self):
        issue, history = self.verification_fixture(event())
        for release in ['1.2.0', '1.3.0', 'release/1.4']:
            issue['fields']['fixVersions'] = [{'name': release}]
            with self.subTest(release=release), \
                    patch.dict(os.environ, {'PCSM_BOARD_FILTER_ID': '13034',
                                            'PCSM_RELEASE_BRANCHES': '{"1.2.0":"wrong-branch"}'}), \
                    patch.object(w, 'jira', side_effect=[{'filter': {'id': 13034}}, {'issues': [issue]}]), \
                    patch.object(w, 'gh', return_value={'commit': {'sha': 'selected-sha'}}) as github, \
                    patch.object(w, 'paged_jira', return_value=[history]):
                info = w.verify(event())
                self.assertEqual((info['release'], info['base'], info['sha']),
                                 (release, release, 'selected-sha'))
                github.assert_called_once_with('branches/' + w.quote(release, safe=''))

    def test_invalid_fix_version_blocks_without_branch_lookup(self):
        for versions in [None, [], [{'name': '1.2.0'}, {'name': '1.3.0'}],
                         [None], [{}], [{'name': None}], [{'name': ''}],
                         [{'name': '../main'}], [{'name': ' 1.2.0 '}]]:
            with self.subTest(versions=versions), patch.object(w, 'gh') as github:
                with self.assertRaises(w.Blocked):
                    w.fix_version_branch(versions)
                github.assert_not_called()

    def test_missing_fix_version_branch_has_no_fallback_or_creation(self):
        with patch.object(w, 'gh', side_effect=w.ApiError(404)) as github:
            with self.assertRaisesRegex(w.Blocked, 'no branch is created'):
                w.fix_version_branch([{'name': '1.2.0'}])
            github.assert_called_once_with('branches/1.2.0')

    def test_changed_fix_version_blocks_publication(self):
        info = {'release': '1.2.0', 'base': '1.2.0', 'sha': 'same'}
        with patch.object(w, 'verify', return_value={**info, 'release': '1.3.0', 'base': '1.3.0'}), \
                patch.object(w, 'gh') as github:
            with self.assertRaises(w.Blocked):
                w.publish(info, {}, {}, True, None, event())
            github.assert_not_called()

    def test_wrong_board_needs_doc_and_stale_history(self):
        e = event()
        issue, history = self.verification_fixture(e)
        with self.assertRaises(w.Blocked):
            self.verify_fixture(issue, history, filter_id=999)
        issue['fields']['customfield_10066']['value'] = 'No'
        with self.assertRaises(w.Blocked):
            self.verify_fixture(issue, history)
        issue['fields']['customfield_10066']['value'] = 'Yes'
        history['items'][0]['from'] = '999'
        with self.assertRaises(w.Blocked):
            self.verify_fixture(issue, history)

    def test_missing_or_ambiguous_fix_version(self):
        issue, history = self.verification_fixture(event())
        for versions in [[], [{'name': '1.1.0'}, {'name': '1.2.0'}]]:
            issue['fields']['fixVersions'] = versions
            with self.assertRaises(w.Blocked):
                self.verify_fixture(issue, history)

    def test_malformed_event_types_are_rejected(self):
        for key, value in [('issue_key', None), ('event_id', 42),
                           ('transition', None), ('transition', []),
                           ('transition', {'to_id': []})]:
            malformed = event()
            malformed[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(w.Blocked):
                w.validate_event(malformed)

    def test_canceling_edits_are_rejected(self):
        proposal = self.proposal()
        proposal['edits'].append({'path': 'docs/start.md', 'old': 'New text.', 'new': 'Old text.'})
        with self.assertRaises(w.Blocked):
            w.apply_edits({'docs/start.md': 'Old text.'}, proposal, {'https://evidence.example'})

    def test_valid_event(self):
        self.assertEqual(w.validate_event(event())['issue_key'], 'PCSM-436')

    def test_reject_bad_source_status_and_injection(self):
        cases = [('site_url', 'https://evil.example'), ('board_id', 142),
                 ('issue_key', 'PCSM-436; touch /tmp/bad'), ('event_id', '../event'),
                 ('event_type', 'arbitrary'), ('occurred_at_ms', 'now')]
        for key, value in cases:
            with self.subTest(key=key):
                e = event()
                e[key] = value
                with self.assertRaises(w.Blocked):
                    w.validate_event(e)
        e = event()
        e['transition']['to_id'] = '10001'
        with self.assertRaises(w.Blocked):
            w.validate_event(e)

    def test_non_configured_test_ticket_cannot_write(self):
        e = event()
        e['issue_key'] = 'PCSM-437'
        with patch.dict(os.environ, {'PCSM_DOCS_TEST_ENABLED': 'true', 'PCSM_DOCS_TEST_ISSUE': 'PCSM-436'}), patch.object(w, 'gh') as github:
            with self.assertRaises(w.Blocked):
                w.process(e, test=True)
            github.assert_not_called()

    def test_disabled_processing_cannot_write(self):
        with patch.dict(os.environ, {'PCSM_DOCS_ENABLED': 'false'}), patch.object(w, 'gh') as github:
            with self.assertRaises(w.Blocked):
                w.process(event())
            github.assert_not_called()

    def proposal(self):
        return {'blocker': '', 'summary': 'Clarify timeout.',
                'edits': [{'path': 'docs/start.md', 'old': 'Old text.', 'new': 'New text.'}],
                'claims': [{'claim': 'Behavior', 'source': 'https://evidence.example', 'locator': 'Test timeout'}]}

    def test_apply_preserves_unrelated_text(self):
        files = {'docs/start.md': '# Title\nOld text.\nUntouched.\n'}
        result = w.apply_edits(files, self.proposal(), {'https://evidence.example'})
        self.assertEqual(result['docs/start.md'], '# Title\nNew text.\nUntouched.\n')

    def test_reject_unsafe_edit_paths_and_sources(self):
        for path in ['.github/workflows/main.yml', 'docs/../../secret.md', '/tmp/test.md', 'docs/new.md']:
            p = self.proposal()
            p['edits'][0]['path'] = path
            with self.assertRaises(w.Blocked):
                w.apply_edits({'docs/start.md': 'Old text.'}, p, {'https://evidence.example'})
        with self.assertRaises(w.Blocked):
            w.apply_edits({'docs/start.md': 'Old text.'}, self.proposal(), set())

    def test_reject_ambiguous_replacement_and_blocker(self):
        with self.assertRaises(w.Blocked):
            w.apply_edits({'docs/start.md': 'Old text. Old text.'}, self.proposal(), {'https://evidence.example'})
        p = self.proposal()
        p['blocker'] = 'Missing source'
        with self.assertRaises(w.Blocked):
            w.apply_edits({'docs/start.md': 'Old text.'}, p, {'https://evidence.example'})

    def test_publication_rechecks_base_before_writes(self):
        info = {'release': '1.2.0', 'base': '1.2.0', 'sha': 'old'}
        with patch.object(w, 'verify', return_value={**info, 'sha': 'new'}), patch.object(w, 'gh') as github:
            with self.assertRaises(w.Blocked):
                w.publish(info, {}, {}, True, None, event())
            github.assert_not_called()

    def test_same_id_different_payload_rejected(self):
        prior = {'digest': w.digest(event()), 'status': 'completed', 'stages': {}}
        import base64
        saved = {'sha': 'blob', 'content': base64.b64encode(json.dumps(prior).encode()).decode()}
        changed = event()
        changed['transition']['from_name'] = 'Changed'
        with patch.object(w, 'gh', return_value=saved):
            with self.assertRaises(w.Blocked):
                w.State(changed, True)

    def test_state_save_reconciles_bounded_branch_conflicts(self):
        import base64
        prior = {'digest': w.digest(event()), 'status': 'new', 'stages': {}}
        saved = {'sha': 'blob-old', 'content': base64.b64encode(json.dumps(prior).encode()).decode()}
        with patch.object(w, 'gh', side_effect=[
                saved, w.ApiError(409), saved, {'content': {'sha': 'blob-new'}}]) as github:
            state = w.State(event(), True)
            state.data['status'] = 'running'
            state.save()
        self.assertEqual(state.blob_sha, 'blob-new')
        self.assertEqual(state.saved_data, state.data)
        self.assertEqual(github.call_count, 4)
        self.assertEqual(github.call_args_list[-1].args[2]['sha'], 'blob-old')

    def test_state_save_does_not_overwrite_concurrent_checkpoint(self):
        import base64
        prior = {'digest': w.digest(event()), 'status': 'new', 'stages': {}}
        changed = {**prior, 'status': 'completed'}
        saved = {'sha': 'blob-old', 'content': base64.b64encode(json.dumps(prior).encode()).decode()}
        concurrent = {'sha': 'blob-other', 'content': base64.b64encode(json.dumps(changed).encode()).decode()}
        with patch.object(w, 'gh', side_effect=[saved, w.ApiError(409), concurrent]) as github:
            state = w.State(event(), True)
            state.data['status'] = 'running'
            with self.assertRaisesRegex(w.Blocked, 'changed concurrently'):
                state.save()
        self.assertEqual(github.call_count, 3)

    def test_state_save_stops_after_bounded_conflicts(self):
        import base64
        prior = {'digest': w.digest(event()), 'status': 'new', 'stages': {}}
        saved = {'sha': 'blob', 'content': base64.b64encode(json.dumps(prior).encode()).decode()}
        actions = [saved]
        for attempt in range(w.STATE_SAVE_ATTEMPTS):
            actions.append(w.ApiError(409))
            if attempt < w.STATE_SAVE_ATTEMPTS - 1:
                actions.append(saved)
        with patch.object(w, 'gh', side_effect=actions) as github:
            state = w.State(event(), True)
            state.data['status'] = 'running'
            with self.assertRaises(w.ApiError):
                state.save()
        self.assertEqual(github.call_count, 2 * w.STATE_SAVE_ATTEMPTS)

    def test_initial_checkpoint_failure_uses_failure_handler(self):
        state = type('StateFixture', (), {})()
        state.data = {'digest': w.digest(event()), 'status': 'new', 'stages': {}}
        attempts = []

        def save():
            attempts.append(state.data['status'])
            if len(attempts) == 1:
                raise w.ApiError(500)

        state.save = save
        env = {'PCSM_DOCS_ENABLED': 'true', 'OPENAI_API_KEY': 'key',
               'PCSM_DOCS_MODEL': 'model'}
        with patch.dict(os.environ, env), \
                patch.object(w, 'ensure_state_branch'), patch.object(w, 'verify', return_value={'sha': 'base'}), \
                patch.object(w, 'State', return_value=state), patch.object(w, 'gh'), \
                patch.object(w, 'notify') as notify:
            with self.assertRaises(w.ApiError):
                w.process(event())
        self.assertEqual(attempts, ['running', 'blocked'])
        notify.assert_not_called()

    def test_all_pr_states_and_test_reuse(self):
        normal = {'title': 'PCSM-436: docs', 'body': '', 'base': {'ref': '1.2.0'}, 'state': 'open'}
        test = copy.deepcopy(normal)
        test['body'] = '<!-- pcsm-automation-test -->'
        with patch.object(w, 'gh_pages', return_value=[normal, test]) as pages:
            info = {'issue': {'key': 'PCSM-436'}, 'base': '1.2.0'}
            self.assertIs(w.existing_pr(info), normal)
            self.assertIs(w.existing_pr(info, True), test)
            self.assertEqual(pages.call_args.args[0], 'pulls?state=all')

    def test_build_environment_excludes_secrets(self):
        with patch.dict(os.environ, {'GH_TOKEN': 'secret', 'OPENAI_API_KEY': 'secret', 'JIRA_API_TOKEN': 'secret'}):
            self.assertFalse({'GH_TOKEN', 'OPENAI_API_KEY', 'JIRA_API_TOKEN'} & w.clean_env().keys())

    def test_documentation_build_isolated_from_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / 'docs'
            site = Path(directory) / 'site'
            checkout.mkdir()
            with patch.object(w, 'command') as run:
                w.build_docs(checkout, site, 'pcsm-docs-build:test')
            args = run.call_args.args[0]
            self.assertIn('--network=none', args)
            self.assertIn('--read-only', args)
            self.assertIn('--cap-drop=ALL', args)
            self.assertIn('--security-opt=no-new-privileges', args)

    def test_codex_model_rejected_before_network(self):
        with patch.dict(os.environ, {'PCSM_DOCS_MODEL': 'some-codex-model'}), patch.object(w, 'api') as api:
            with self.assertRaises(w.Blocked):
                w.model_response({}, '')
            api.assert_not_called()


class FixtureState:
    def __init__(self):
        self.key = w.digest(event())
        self.data = {'digest': w.digest(event()), 'status': 'new', 'stages': {}}
        self.saves = 0

    def save(self):
        self.saves += 1


class Notifications(unittest.TestCase):
    def setUp(self):
        self.state = FixtureState()
        self.info = {'issue': {'key': 'PCSM-436'}, 'release': '3.7.9', 'base': '3.7.9', 'sha': 'base'}
        self.pr = {'number': 42, 'html_url': 'https://github.com/percona/pcsm-docs/pull/42'}
        self.comments = []
        self.writes = []
        self.timeout_after_write = False
        self.fail_write = False

    def github(self, path, method='GET', body=None):
        if path.startswith('git/'):
            return {}
        if method in {'POST', 'PATCH'}:
            self.writes.append((path, method))
            if self.fail_write:
                raise w.ApiError(403)
            comment = {'id': 321, 'body': body['body'],
                       'html_url': self.pr['html_url'] + '#issuecomment-321'}
            self.comments[:] = [comment]
            if self.timeout_after_write:
                raise TimeoutError('private transport detail')
            return comment
        return self.comments[0]

    def notification(self, outcome='completed'):
        with patch.object(w, 'gh', side_effect=self.github), \
                patch.object(w, 'gh_pages', side_effect=lambda path: self.comments), \
                patch.dict(os.environ, {'GITHUB_RUN_ID': '1234'}):
            return w.notify(self.state, self.info, self.pr, outcome)

    def test_comment_has_verified_context_and_replay_deduplicates(self):
        self.state.data['stages'].update(review='requested', backlink='verified')
        url = self.notification()
        self.assertEqual(url, self.comments[0]['html_url'])
        self.assertIn('3.7.9', self.comments[0]['body'])
        self.assertIn('actions/runs/1234', self.comments[0]['body'])
        self.assertIn('Review request: requested', self.comments[0]['body'])
        self.assertIn('Jira backlink: verified', self.comments[0]['body'])
        self.notification()
        self.assertEqual(len(self.writes), 1)
        self.assertEqual(self.state.data['stages']['notification_comment'], 'verified')

    def test_timeout_after_successful_post_is_reconciled_without_resend(self):
        self.timeout_after_write = True
        self.notification()
        self.assertEqual(len(self.writes), 1)
        self.assertEqual(self.state.data['stages']['notification_comment'], 'verified')

    def test_failure_changes_same_comment_instead_of_creating_another(self):
        self.notification()
        self.notification('blocked')
        self.assertEqual([method for _, method in self.writes], ['POST', 'PATCH'])
        self.assertEqual(len(self.comments), 1)
        self.assertIn('automation: blocked', self.comments[0]['body'])

    def test_unverified_post_never_blindly_resends(self):
        self.fail_write = True
        with self.assertRaisesRegex(w.Blocked, 'could not be verified'):
            self.notification()
        with self.assertRaisesRegex(w.Blocked, 'Previous comment write'):
            self.notification()
        self.assertEqual(len(self.writes), 1)

    def test_readback_mismatch_blocks(self):
        with patch.object(w, 'gh_pages', return_value=[]), \
                patch.object(w, 'gh', side_effect=[{'id': 321}, {'body': 'different'}]):
            with self.assertRaisesRegex(w.Blocked, 'could not be verified'):
                w.notify(self.state, self.info, self.pr, 'completed')
        self.assertEqual(self.state.data['stages']['notification_comment'], 'unverified')

    def test_duplicate_event_markers_block_without_write(self):
        self.notification()
        self.comments.append(dict(self.comments[0]))
        with self.assertRaisesRegex(w.Blocked, 'Multiple event comments'):
            self.notification()
        self.assertEqual(len(self.writes), 1)

    def test_new_event_gets_distinct_comment_marker(self):
        self.notification()
        previous_body = self.comments[0]['body']
        self.state = FixtureState()
        self.state.key = w.digest('another event')
        with patch.object(w, 'gh_pages', return_value=[{'body': previous_body}]), \
                patch.object(w, 'gh', side_effect=self.github):
            w.notify(self.state, self.info, self.pr, 'completed')
        self.assertEqual([method for _, method in self.writes], ['POST', 'POST'])

    def test_comment_failure_handler_preserves_original_error(self):
        env = {'PCSM_DOCS_ENABLED': 'true', 'PCSM_DOCS_MODEL': 'model', 'OPENAI_API_KEY': 'key'}
        with tempfile.TemporaryDirectory() as directory:
            summary = Path(directory) / 'summary.md'
            env['GITHUB_STEP_SUMMARY'] = str(summary)
            with patch.dict(os.environ, env, clear=True), \
                    patch.object(w, 'ensure_state_branch'), patch.object(w, 'State', return_value=self.state), \
                    patch.object(w, 'verify', return_value=self.info), \
                    patch.object(w, 'gh', side_effect=self.github), \
                    patch.object(w, 'existing_pr', return_value=self.pr), \
                    patch.object(w, 'followups', side_effect=w.Blocked('Jira backlink was not verified.')), \
                    patch.object(w, 'notify', side_effect=TimeoutError('private response')):
                with self.assertRaisesRegex(w.Blocked, 'Jira backlink was not verified'):
                    w.process(event())
            text = summary.read_text()
            self.assertIn('Jira backlink was not verified', text)
            self.assertIn('notification could not be verified', text)
            self.assertNotIn('private response', text)
        self.assertEqual(self.state.data['status'], 'blocked')

    def test_new_and_reused_prs_notify_without_mail_configuration(self):
        env = {'PCSM_DOCS_ENABLED': 'true', 'PCSM_DOCS_MODEL': 'model', 'OPENAI_API_KEY': 'key'}
        for reuse in (False, True):
            with self.subTest(reuse=reuse):
                self.state = FixtureState()
                self.comments = []
                self.writes = []
                with patch.dict(os.environ, env, clear=True), \
                        patch.object(w, 'ensure_state_branch'), patch.object(w, 'State', return_value=self.state), \
                        patch.object(w, 'verify', return_value=self.info), \
                        patch.object(w, 'gh', side_effect=self.github), \
                        patch.object(w, 'gh_pages', side_effect=lambda path: self.comments), \
                        patch.object(w, 'existing_pr', return_value=self.pr if reuse else None), \
                        patch.object(w, 'collect_sources', return_value={}), \
                        patch.object(w, 'draft_and_build', return_value=({}, {})) as draft, \
                        patch.object(w, 'publish', return_value=self.pr), \
                        patch.object(w, 'followups') as followups:
                    result = w.process(event())
                    self.assertEqual(result['status'], 'completed')
                    followups.assert_called_once()
                    self.assertEqual(draft.call_count, 0 if reuse else 1)
                    self.assertEqual(len(self.writes), 1)
                    w.process(event())
                    self.assertEqual(len(self.writes), 1)
                    self.assertEqual(draft.call_count, 0 if reuse else 1)

    def test_failure_before_pr_uses_summary_without_comment(self):
        env = {'PCSM_DOCS_ENABLED': 'true', 'PCSM_DOCS_MODEL': 'model', 'OPENAI_API_KEY': 'key'}
        with tempfile.TemporaryDirectory() as directory:
            summary = Path(directory) / 'summary.md'
            env['GITHUB_STEP_SUMMARY'] = str(summary)
            with patch.dict(os.environ, env, clear=True), \
                    patch.object(w, 'ensure_state_branch'), patch.object(w, 'State', return_value=self.state), \
                    patch.object(w, 'verify', return_value=self.info), patch.object(w, 'gh'), \
                    patch.object(w, 'existing_pr', return_value=None), \
                    patch.object(w, 'collect_sources', side_effect=w.Blocked('Incomplete evidence.')), \
                    patch.object(w, 'notify') as notify:
                with self.assertRaisesRegex(w.Blocked, 'Incomplete evidence'):
                    w.process(event())
                notify.assert_not_called()
            self.assertIn('No verified documentation PR', summary.read_text())

    def test_changed_eligibility_blocks_followups_on_reused_pr(self):
        env = {'PCSM_DOCS_ENABLED': 'true', 'PCSM_DOCS_MODEL': 'model', 'OPENAI_API_KEY': 'key'}
        with patch.dict(os.environ, env, clear=True), \
                patch.object(w, 'ensure_state_branch'), patch.object(w, 'State', return_value=self.state), \
                patch.object(w, 'verify', side_effect=[self.info, w.Blocked('Ticket is stale.')]), \
                patch.object(w, 'gh'), patch.object(w, 'existing_pr', return_value=self.pr), \
                patch.object(w, 'followups') as followups:
            with self.assertRaisesRegex(w.Blocked, 'Ticket is stale'):
                w.process(event())
            followups.assert_not_called()

    def test_configured_test_ticket_accepts_future_ticket(self):
        e = event()
        e['issue_key'] = 'PCSM-999'
        info = {**self.info, 'issue': {'key': e['issue_key']}}
        env = {'PCSM_DOCS_TEST_ENABLED': 'true', 'PCSM_DOCS_TEST_ISSUE': e['issue_key'],
               'PCSM_DOCS_MODEL': 'model', 'OPENAI_API_KEY': 'key'}
        with patch.dict(os.environ, env, clear=True), \
                patch.object(w, 'ensure_state_branch'), patch.object(w, 'State', return_value=self.state), \
                patch.object(w, 'verify', return_value=info), patch.object(w, 'gh'), \
                patch.object(w, 'existing_pr', return_value=self.pr), patch.object(w, 'followups'), \
                patch.object(w, 'notify'):
            self.assertEqual(w.process(e, test=True)['status'], 'completed')


class EvidenceAndMatching(unittest.TestCase):
    def test_related_ticket_in_body_does_not_match(self):
        pr = {'title': 'PCSM-111: docs', 'body': 'Related: PCSM-436', 'base': {'ref': '1.2.0'}, 'state': 'open'}
        info = {'issue': {'key': 'PCSM-436'}, 'base': '1.2.0'}
        with patch.object(w, 'gh_pages', return_value=[pr]):
            self.assertIsNone(w.existing_pr(info))

    def test_closed_unmerged_and_ambiguous_matches_block(self):
        pr = {'title': 'PCSM-436: docs', 'body': '', 'base': {'ref': '1.2.0'}, 'state': 'closed'}
        info = {'issue': {'key': 'PCSM-436'}, 'base': '1.2.0'}
        with patch.object(w, 'gh_pages', return_value=[pr]):
            with self.assertRaisesRegex(w.Blocked, 'closed without merge'):
                w.existing_pr(info)
            pr['merged_at'] = '2026-11-26T00:00:00Z'
            self.assertIs(w.existing_pr(info), pr)
        with patch.object(w, 'gh_pages', return_value=[pr, dict(pr)]):
            with self.assertRaisesRegex(w.Blocked, 'Multiple documentation PRs'):
                w.existing_pr(info)

    def source_fixture(self, file, changed=False):
        url = 'https://github.com/percona/percona-clustersync-mongodb/pull/302'
        info = {'issue': {'key': 'PCSM-436', 'description': url}, 'release': '3.7.9', 'base': '3.7.9'}
        pr = {'head': {'sha': 'head'}, 'base': {'sha': 'base'}, 'state': 'closed', 'merged': True, 'changed_files': 1}
        refreshed = copy.deepcopy(pr)
        if changed:
            refreshed['head']['sha'] = 'other-head'
        with patch.object(w, 'paged_jira', return_value=[]), patch.object(w, 'jira', return_value=[]), \
                patch.object(w, 'gh', side_effect=[pr, refreshed]), \
                patch.object(w, 'gh_pages', side_effect=[[file], [], [], []]):
            return w.collect_sources(info)

    def test_missing_deleted_file_patch_blocks(self):
        with self.assertRaisesRegex(w.Blocked, 'diff is incomplete'):
            self.source_fixture({'status': 'removed', 'filename': 'old.go'})

    def test_mutated_source_pr_blocks_same_file_count(self):
        with self.assertRaisesRegex(w.Blocked, 'changed during evidence collection'):
            self.source_fixture({'status': 'modified', 'patch': '@@\n-old\n+new'}, changed=True)

    def test_complete_deleted_patch_is_preserved(self):
        file = {'status': 'removed', 'filename': 'old.go', 'patch': '@@\n-old'}
        self.assertEqual(self.source_fixture(file)['implementation_prs'][0]['files'], [file])

    def test_both_model_passes_receive_canonical_sources(self):
        info = {'issue': {'key': 'PCSM-436'}, 'release': '3.7.9', 'sha': 'base'}
        source = 'https://github.com/percona/percona-clustersync-mongodb/pull/302'
        evidence = {'implementation_prs': [{'pr': {'html_url': source}}]}
        proposal = {'blocker': '', 'summary': 'Change', 'edits': [
            {'path': 'docs/start.md', 'old': 'Old text.', 'new': 'New text.'}],
            'claims': [{'claim': 'Behavior', 'source': source, 'locator': 'Test function'}]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'docs/docs').mkdir(parents=True)
            (root / 'docs/docs/start.md').write_text('Old text.')
            with patch.object(w, 'command'), patch.object(w, 'build_image'), patch.object(w, 'build_docs'), \
                    patch.object(w, 'model_response', return_value=proposal) as model:
                w.draft_and_build(info, evidence, root)
            expected = sorted([source, w.SITE + '/browse/PCSM-436'])
            self.assertEqual(model.call_args_list[0].args[0]['allowed_claim_sources'], expected)
            self.assertEqual(model.call_args_list[1].args[0]['sources']['allowed_claim_sources'], expected)


if __name__ == '__main__':
    unittest.main()
