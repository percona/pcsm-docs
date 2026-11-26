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
        with patch.dict(os.environ, {'PCSM_BOARD_FILTER_ID': '13034',
                                     'PCSM_RELEASE_BRANCHES': '{"1.2.0":"1.2.0"}'}), \
                patch.object(w, 'jira', side_effect=[{'filter': {'id': filter_id}}, {'issues': [issue]}]), \
                patch.object(w, 'gh', return_value={'commit': {'sha': 'base'}}), \
                patch.object(w, 'paged_jira', return_value=[history]):
            return w.verify(event or globals()['event']())

    def test_authoritative_jira_verification(self):
        e = event()
        issue, history = self.verification_fixture(e)
        verified = self.verify_fixture(issue, history)
        self.assertEqual((verified['base'], verified['history_id']), ('1.2.0', '42'))

    def test_fix_version_selects_exact_mapped_branch(self):
        issue, history = self.verification_fixture(event())
        mapping = {'1.2.0': 'release/1.2', '1.3.0': 'docs-1.3'}
        for release, branch in mapping.items():
            issue['fields']['fixVersions'] = [{'name': release}]
            with self.subTest(release=release), \
                    patch.dict(os.environ, {'PCSM_BOARD_FILTER_ID': '13034',
                                            'PCSM_RELEASE_BRANCHES': json.dumps(mapping)}), \
                    patch.object(w, 'jira', side_effect=[{'filter': {'id': 13034}}, {'issues': [issue]}]), \
                    patch.object(w, 'gh', return_value={'commit': {'sha': 'selected-sha'}}) as github, \
                    patch.object(w, 'paged_jira', return_value=[history]):
                info = w.verify(event())
                self.assertEqual((info['release'], info['base'], info['sha']),
                                 (release, branch, 'selected-sha'))
                github.assert_called_once_with('branches/' + w.quote(branch, safe=''))

    def test_invalid_mapping_blocks_without_branch_lookup(self):
        mappings = ['not json', 'null', '[]', '{}',
                    '{"1.2.0":"one","1.2.0":"two"}',
                    '{"1.2.0":null}', '{"1.2.0":[]}', '{"1.2.0":""}',
                    '{"1.2.0":"../main"}', '{"1.2.0":"branch with spaces"}',
                    '{"1.3.0":"1.3.0"}']
        for mapping in mappings:
            with self.subTest(mapping=mapping), \
                    patch.dict(os.environ, {'PCSM_RELEASE_BRANCHES': mapping}), \
                    patch.object(w, 'gh') as github:
                with self.assertRaises(w.Blocked):
                    w.mapped_release_branch([{'name': '1.2.0'}])
                github.assert_not_called()

    def test_missing_mapped_branch_has_no_fallback_or_creation(self):
        with patch.dict(os.environ, {'PCSM_RELEASE_BRANCHES': '{"1.2.0":"release/1.2"}'}), \
                patch.object(w, 'gh', side_effect=w.ApiError(404)) as github:
            with self.assertRaisesRegex(w.Blocked, 'no branch is created'):
                w.mapped_release_branch([{'name': '1.2.0'}])
            github.assert_called_once_with('branches/release%2F1.2')

    def test_changed_mapping_blocks_publication(self):
        info = {'release': '1.2.0', 'base': 'release/1.2', 'sha': 'same'}
        with patch.object(w, 'verify', return_value={**info, 'base': 'another-branch'}), \
                patch.object(w, 'gh') as github:
            with self.assertRaises(w.Blocked):
                w.publish(info, {}, {}, True, None)
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
        for versions in [[], [{'name': '1.1.0'}, {'name': '1.2.0'}], [{'name': 'unmapped'}]]:
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

    def test_non_pcsm_436_test_cannot_write(self):
        e = event()
        e['issue_key'] = 'PCSM-437'
        with patch.dict(os.environ, {'PCSM_DOCS_TEST_ENABLED': 'true'}), patch.object(w, 'gh') as github:
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

    def test_smtp_uncertain_state_never_resends(self):
        class State:
            data = {'stages': {'start_email': 'sending'}}
        with patch.object(w.smtplib, 'SMTP') as smtp:
            self.assertEqual(w.notify(State(), 'start_email', 'title', 'text'), 'sending')
            smtp.assert_not_called()

    def test_publication_rechecks_base_before_writes(self):
        info = {'release': '1.2.0', 'base': '1.2.0', 'sha': 'old'}
        with patch.object(w, 'verify', return_value={**info, 'sha': 'new'}), patch.object(w, 'gh') as github:
            with self.assertRaises(w.Blocked):
                w.publish(info, {}, {}, True, None)
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

    def test_all_pr_states_and_test_reuse(self):
        normal = {'title': 'PCSM-436: docs', 'body': '', 'base': {'ref': '1.2.0'}, 'state': 'closed'}
        test = copy.deepcopy(normal)
        test['body'] = '<!-- pcsm-automation-test -->'
        with patch.object(w, 'gh_pages', return_value=[normal, test]) as pages:
            info = {'issue': {'key': 'PCSM-436'}, 'base': '1.2.0'}
            self.assertIs(w.existing_pr(info), normal)
            self.assertIs(w.existing_pr(info, True), test)
            self.assertEqual(pages.call_args.args[0], 'pulls?state=all')

    def test_build_environment_excludes_secrets(self):
        with patch.dict(os.environ, {'GH_TOKEN': 'secret', 'OPENAI_API_KEY': 'secret', 'SMTP_PASSWORD': 'secret'}):
            self.assertFalse({'GH_TOKEN', 'OPENAI_API_KEY', 'SMTP_PASSWORD'} & w.clean_env().keys())

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


if __name__ == '__main__':
    unittest.main()
