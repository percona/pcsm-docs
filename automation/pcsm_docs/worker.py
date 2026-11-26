"""PCSM event processor. Direct HTTPS APIs only; no Codex or local connections.

All writes are deterministic application code. Model output is limited to exact
replacements in existing Markdown files. Documentation builds run in an isolated
container without worker credentials or network access.
"""
import base64
import hashlib
import json
import os
import re
import smtplib
import ssl
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

SITE = 'https://perconadev.atlassian.net'
REPO = 'percona/pcsm-docs'
SOURCE_REPO = 'percona/percona-clustersync-mongodb'
RECIPIENT = 'rasika.chivate@percona.com'
STATE_BRANCH = 'automation/pcsm-event-state'
STATE_SAVE_ATTEMPTS = 3
TARGETS = {'10045': 'In QA', '10043': 'In Doc'}


class Blocked(Exception):
    pass


class ApiError(Blocked):
    def __init__(self, status):
        self.status = status
        super().__init__(f'API request failed (HTTP {status}); inspect service access. No automatic write retry.')


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Blocked('Unexpected API redirect; credentials were not forwarded.')


def required(name):
    value = os.environ.get(name, '')
    if not value:
        raise Blocked(f'Missing configuration: {name}')
    return value


def api(url, token, method='GET', body=None, basic=False):
    headers = {'Accept': 'application/json', 'User-Agent': 'pcsm-docs-event-worker'}
    if token:
        headers['Authorization'] = ('Basic ' if basic else 'Bearer ') + token
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers['Content-Type'] = 'application/json'
    try:
        with build_opener(NoRedirect).open(Request(url, data, headers, method=method), timeout=180) as r:
            payload = r.read(2_000_001)
            if len(payload) > 2_000_000:
                raise Blocked('API evidence exceeds safe size; manual review required.')
            return json.loads(payload) if payload else {}
    except HTTPError as exc:
        raise ApiError(exc.code) from None


def gh(path, method='GET', body=None, source=False):
    repo = SOURCE_REPO if source else REPO
    token = os.environ.get('PCSM_SOURCE_TOKEN', '') if source else required('GH_TOKEN')
    return api(f'https://api.github.com/repos/{repo}/{path}', token, method, body)


def jira(path, method='GET', body=None):
    auth = base64.b64encode((required('JIRA_EMAIL') + ':' + required('JIRA_API_TOKEN')).encode()).decode()
    return api(SITE + path, auth, method, body, basic=True)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate_event(event):
    if not isinstance(event, dict) or event.get('schema_version') != 1:
        raise Blocked('Invalid event schema.')
    if event.get('event_type') != 'jira.issue.status_changed' or event.get('site_url') != SITE or event.get('board_id') != 141:
        raise Blocked('Unexpected event source or board.')
    if not isinstance(event.get('issue_key'), str) or not re.fullmatch(r'PCSM-[1-9][0-9]*', event['issue_key']):
        raise Blocked('Invalid issue key.')
    if not isinstance(event.get('event_id'), str) or not re.fullmatch(r'pcsm-[0-9]+-[0-9]{13}-[0-9]+', event['event_id']):
        raise Blocked('Invalid stable event ID.')
    transition = event.get('transition', {})
    if not isinstance(transition, dict) or not isinstance(transition.get('to_id'), str):
        raise Blocked('Invalid transition schema.')
    if transition.get('to_id') not in TARGETS or transition.get('to_name') != TARGETS[transition['to_id']]:
        raise Blocked('Unapproved destination status.')
    if not re.fullmatch(r'[0-9]{13}', str(event.get('occurred_at_ms', ''))):
        raise Blocked('Invalid event timestamp.')
    if not isinstance(transition.get('from_id'), str) or not transition['from_id'].isdigit():
        raise Blocked('Missing source status ID.')
    return event


def paged_jira(path, key):
    values, start = [], 0
    for _ in range(100):
        page = jira(path + ('&' if '?' in path else '?') + urlencode({'startAt': start, 'maxResults': 100}))
        batch = page.get(key, [])
        values.extend(batch)
        start += len(batch)
        if page.get('isLast') or start >= page.get('total', 0):
            return values
        if not batch:
            break
    raise Blocked('Could not read complete Jira evidence.')


def fix_version_branch(versions):
    """Use the exact Jira Fix version name as the existing documentation branch."""
    if not isinstance(versions, list) or len(versions) != 1:
        raise Blocked('Exactly one Fix version is required.')
    version = versions[0]
    release = version.get('name') if isinstance(version, dict) else None
    if not isinstance(release, str) or not re.fullmatch(r'[A-Za-z0-9._/-]+', release) or '..' in release:
        raise Blocked('Fix version must exactly name a valid nonempty documentation branch.')
    try:
        base = gh('branches/' + quote(release, safe=''))['commit']['sha']
    except ApiError as exc:
        if exc.status == 404:
            raise Blocked('The branch named by Fix version was not found or is inaccessible; no branch is created.') from None
        raise
    return release, release, base


def verify(event):
    validate_event(event)
    board_filter = required('PCSM_BOARD_FILTER_ID')
    if not board_filter.isdigit():
        raise Blocked('Board filter must be the admin-confirmed numeric ID.')
    config = jira('/rest/agile/1.0/board/141/configuration')
    if str(config.get('filter', {}).get('id')) != board_filter:
        raise Blocked('Board 141 does not match the confirmed filter.')
    key = event['issue_key']
    result = jira('/rest/api/3/search/jql', 'POST', {
        'jql': f'filter = {board_filter} AND key = {key}', 'maxResults': 2,
        'fields': ['summary', 'description', 'status', 'fixVersions', 'customfield_10066', 'issuetype', 'attachment']})
    issues = result.get('issues', [])
    if len(issues) != 1 or issues[0]['key'] != key:
        raise Blocked('Ticket is not in the verified board filter.')
    issue = issues[0]
    fields = issue['fields']
    needs_doc = fields.get('customfield_10066') or {}
    if needs_doc.get('value') != 'Yes' or fields['status']['id'] != event['transition']['to_id']:
        raise Blocked('Ticket is stale or Needs Doc is not Yes.')
    if fields.get('issuetype', {}).get('subtask') or fields.get('issuetype', {}).get('name', '').lower() in {'admin', 'administrative task'}:
        raise Blocked('Administrative work and subtasks require manual triage.')
    release, branch, base = fix_version_branch(fields.get('fixVersions', []))
    histories = paged_jira(f'/rest/api/3/issue/{key}/changelog', 'values')
    transitions = [(h, item) for h in histories for item in h.get('items', []) if item.get('field') == 'status']
    if not transitions:
        raise Blocked('No authoritative status history.')
    history, item = max(transitions, key=lambda pair: pair[0]['created'])
    millis = int(datetime.fromisoformat(history['created'].replace('Z', '+00:00')).timestamp() * 1000)
    transition = event['transition']
    if (abs(millis - int(event['occurred_at_ms'])) > 1000 or item.get('from') != transition['from_id']
            or item.get('to') != transition['to_id'] or item.get('fromString') != transition.get('from_name')
            or item.get('toString') != transition['to_name']):
        raise Blocked('Event does not match the latest Jira status transition.')
    if event['event_id'] != f"pcsm-{issue['id']}-{event['occurred_at_ms']}-{transition['to_id']}":
        raise Blocked('Event ID does not match the authoritative ticket and transition.')
    return {'issue': issue, 'release': release, 'base': branch, 'sha': base, 'history_id': history['id']}


def gh_pages(path, source=False):
    result = []
    for page in range(1, 101):
        batch = gh(path + ('&' if '?' in path else '?') + f'per_page=100&page={page}', source=source)
        if not isinstance(batch, list):
            raise Blocked('Unexpected paginated response.')
        result.extend(batch)
        if len(batch) < 100:
            return result
    raise Blocked('Evidence requires more than 100 pages; manual review required.')


def existing_pr(info, test=False):
    key = info['issue']['key']
    for pr in gh_pages('pulls?state=all'):
        title_body = pr['title'] + '\n' + (pr.get('body') or '')
        if pr['base']['ref'] == info['base'] and re.search(r'\b' + re.escape(key) + r'\b', title_body):
            if test == ('<!-- pcsm-automation-test -->' in title_body):
                return pr
    return None


class State:
    """Public branch contains only opaque IDs, outcome flags, and public PR URLs."""
    def __init__(self, event, test):
        self.key = digest({'id': event['event_id'], 'test': test})
        self.path = '.automation-state/' + self.key + '.json'
        self.blob_sha = None
        self.data = {'digest': digest(event), 'status': 'new', 'stages': {}}
        self.saved_data = None
        try:
            f = gh('contents/' + self.path + '?ref=' + quote(STATE_BRANCH, safe=''))
            self.blob_sha = f['sha']
            prior = json.loads(base64.b64decode(f['content']))
            if prior['digest'] != self.data['digest']:
                raise Blocked('Event-ID conflict: payload changed.')
            self.data = prior
            self.saved_data = json.loads(json.dumps(prior))
        except ApiError as exc:
            if exc.status != 404:
                raise

    def refresh_after_conflict(self):
        try:
            f = gh('contents/' + self.path + '?ref=' + quote(STATE_BRANCH, safe=''))
        except ApiError as exc:
            if exc.status != 404:
                raise
            self.blob_sha = None
            return
        remote = json.loads(base64.b64decode(f['content']))
        if remote.get('digest') != self.data['digest']:
            raise Blocked('Checkpoint event changed concurrently; manual reconciliation required.')
        if remote == self.data:
            self.blob_sha = f['sha']
            self.saved_data = json.loads(json.dumps(remote))
            return
        if remote != self.saved_data:
            raise Blocked('Checkpoint changed concurrently; manual reconciliation required.')
        self.blob_sha = f['sha']

    def save(self):
        body = {'message': 'Checkpoint PCSM documentation event', 'branch': STATE_BRANCH,
                'content': base64.b64encode(json.dumps(self.data, sort_keys=True).encode()).decode()}
        for attempt in range(STATE_SAVE_ATTEMPTS):
            body.pop('sha', None)
            if self.blob_sha:
                body['sha'] = self.blob_sha
            try:
                result = gh('contents/' + self.path, 'PUT', body)
                self.blob_sha = result['content']['sha']
                self.saved_data = json.loads(json.dumps(self.data))
                return
            except ApiError as exc:
                if exc.status != 409 or attempt == STATE_SAVE_ATTEMPTS - 1:
                    raise
                self.refresh_after_conflict()


def ensure_state_branch():
    try:
        gh('git/ref/heads/' + STATE_BRANCH)
    except ApiError as exc:
        if exc.status != 404:
            raise
        sha = gh('git/ref/heads/main')['object']['sha']
        try:
            gh('git/refs', 'POST', {'ref': 'refs/heads/' + STATE_BRANCH, 'sha': sha})
        except ApiError as race:
            if race.status != 422:
                raise
            gh('git/ref/heads/' + STATE_BRANCH)


def notify(state, stage, subject, body):
    prior = state.data['stages'].get(stage)
    if prior:
        # SMTP has no idempotency primitive. An uncertain send is never retried.
        return prior
    state.data['stages'][stage] = 'sending'
    state.save()
    message = EmailMessage()
    message['From'] = required('SMTP_FROM')
    message['To'] = RECIPIENT
    message['Subject'] = subject
    message['Message-ID'] = f'<pcsm-{state.key}-{stage}@percona.com>'
    message.set_content(body)
    try:
        with smtplib.SMTP(required('SMTP_HOST'), int(os.environ.get('SMTP_PORT') or '587'), timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls(context=ssl.create_default_context())
            smtp.ehlo()
            smtp.login(required('SMTP_USER'), required('SMTP_PASSWORD'))
            refused = smtp.send_message(message)
            if refused:
                raise Blocked('SMTP recipient rejected.')
        state.data['stages'][stage] = 'accepted'
    except Exception:
        state.data['stages'][stage] = 'unverified'
    state.save()
    return state.data['stages'][stage]


def collect_sources(info):
    key = info['issue']['key']
    comments = paged_jira(f'/rest/api/3/issue/{key}/comment', 'comments')
    links = jira(f'/rest/api/3/issue/{key}/remotelink')
    raw = json.dumps({'ticket': info['issue'], 'comments': comments, 'links': links})
    pattern = r'https://github\.com/percona/percona-clustersync-mongodb/pull/([0-9]+)'
    numbers = sorted(set(re.findall(pattern, raw)))
    if not numbers:
        raise Blocked('No explicit implementation PR link in ticket, comments or remote links.')
    prs = []
    for number in numbers:
        pr = gh('pulls/' + number, source=True)
        files = gh_pages('pulls/' + number + '/files', source=True)
        if any(f.get('status') != 'removed' and not f.get('patch') for f in files):
            raise Blocked('Implementation diff is incomplete or contains binary evidence; manual research required.')
        if len(files) != pr.get('changed_files'):
            raise Blocked('Incomplete implementation PR file list.')
        prs.append({'pr': pr, 'files': files,
                    'discussion': gh_pages('issues/' + number + '/comments', source=True),
                    'reviews': gh_pages('pulls/' + number + '/reviews', source=True),
                    'inline_comments': gh_pages('pulls/' + number + '/comments', source=True)})
    return {'ticket': info['issue'], 'comments': comments, 'remote_links': links,
            'implementation_prs': prs, 'release': info['release'], 'docs_base': info['base']}


SCHEMA = {'type': 'object', 'additionalProperties': False, 'required': ['blocker', 'summary', 'edits', 'claims'],
          'properties': {
              'blocker': {'type': 'string'}, 'summary': {'type': 'string'},
              'edits': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False,
                  'required': ['path', 'old', 'new'], 'properties': {k: {'type': 'string'} for k in ['path', 'old', 'new']}}},
              'claims': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False,
                  'required': ['claim', 'source', 'locator'], 'properties': {k: {'type': 'string'} for k in ['claim', 'source', 'locator']}}}}}


def model_response(evidence, instruction):
    serialized = json.dumps(evidence)
    if len(serialized) > 500_000:
        raise Blocked('Source set is too large; no silent truncation. Manual research required.')
    model = required('PCSM_DOCS_MODEL')
    if 'codex' in model.lower():
        raise Blocked('A non-Codex model must be configured.')
    result = api('https://api.openai.com/v1/responses', required('OPENAI_API_KEY'), 'POST', {
        'model': model, 'store': False, 'max_output_tokens': 12000,
        'instructions': Path(__file__).with_name('prompt.txt').read_text() + '\n' + instruction,
        'input': serialized, 'text': {'format': {'type': 'json_schema', 'name': 'documentation_edits',
                                               'strict': True, 'schema': SCHEMA}}})
    if result.get('status') != 'completed':
        raise Blocked('Drafting response did not complete.')
    output = ''.join(c['text'] for item in result.get('output', []) if item.get('type') == 'message'
                     for c in item.get('content', []) if c.get('type') == 'output_text')
    return json.loads(output)


def apply_edits(files, proposal, allowed_sources):
    if proposal.get('blocker'):
        # Do not put arbitrary model text (possibly private evidence) in public logs.
        raise Blocked('Drafting review reported missing or conflicting evidence; manual review required.')
    if not 1 <= len(proposal.get('edits', [])) <= 10 or not proposal.get('claims'):
        raise Blocked('Draft requires 1–10 exact edits and a claim-to-source map.')
    output = dict(files)
    for edit in proposal['edits']:
        path = edit['path']
        if (not path.startswith('docs/') or not path.endswith('.md') or '..' in PurePosixPath(path).parts
                or '\\' in path or path not in files):
            raise Blocked('Draft changed a forbidden or new path.')
        old, new = edit['old'], edit['new']
        if not old or not new or old == new or output[path].count(old) != 1:
            raise Blocked('Draft replacement must match exactly once and preserve a nonempty result.')
        output[path] = output[path].replace(old, new, 1)
    for claim in proposal['claims']:
        if claim['source'] not in allowed_sources or not claim['locator'].strip():
            raise Blocked('Unverified claim source.')
    changes = {p: value for p, value in output.items() if value != files[p]}
    if not changes:
        raise Blocked('Draft contains no net documentation changes.')
    return changes


def clean_env():
    return {k: os.environ[k] for k in ('PATH', 'LANG', 'TMPDIR', 'SYSTEMROOT') if k in os.environ}


def command(args, cwd=None):
    result = subprocess.run(args, cwd=cwd, env=clean_env(), capture_output=True, timeout=600)
    if result.returncode:
        raise Blocked('Documentation checkout/build failed; no PR was published.')


def build_image(checkout, root):
    context = root / 'build-image'
    context.mkdir()
    (context / 'requirements.txt').write_bytes((checkout / 'requirements.txt').read_bytes())
    (context / 'Dockerfile').write_text(
        'FROM python:3.12-slim\n'
        'RUN apt-get update && apt-get install -y --no-install-recommends git '
        '&& rm -rf /var/lib/apt/lists/*\n'
        'COPY requirements.txt /tmp/requirements.txt\n'
        'RUN python -m venv /opt/venv && '
        '/opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt\n'
        'WORKDIR /workspace\n'
    )
    image = 'pcsm-docs-build:' + digest(str(root))[:12]
    command(['docker', 'build', '--quiet', '--tag', image, str(context)])
    return image


def build_docs(checkout, site_dir, image):
    site_dir.mkdir()
    command([
        'docker', 'run', '--rm', '--network=none', '--read-only',
        '--cap-drop=ALL', '--security-opt=no-new-privileges',
        '--user', f'{os.getuid()}:{os.getgid()}',
        '--tmpfs', '/tmp:rw,noexec,nosuid,size=64m',
        '--env', 'HOME=/tmp', '--workdir', '/workspace',
        '--mount', f'type=bind,source={checkout},target=/workspace,readonly',
        '--mount', f'type=bind,source={site_dir},target=/site',
        image, '/opt/venv/bin/mkdocs', 'build', '--strict', '--site-dir', '/site',
    ])


def draft_and_build(info, evidence, root):
    checkout = root / 'docs'
    command(['git', 'clone', '--quiet', '--no-checkout', 'https://github.com/' + REPO + '.git', str(checkout)])
    command(['git', 'checkout', '--detach', info['sha']], cwd=checkout)
    files = {str(p.relative_to(checkout)): p.read_text() for p in (checkout / 'docs').rglob('*.md') if not p.is_symlink()}
    context = dict(files)
    for name in ('variables.yml', 'mkdocs.yml', 'mkdocs-base.yml', 'AGENTS.md'):
        p = checkout / name
        if p.exists():
            context[name] = p.read_text()
    for p in checkout.rglob('AGENTS.md'):
        context[str(p.relative_to(checkout))] = p.read_text()
    evidence['documentation'] = context
    proposal = model_response(evidence, 'Produce a minimal, evidence-backed first draft.')
    sources = {SITE + '/browse/' + info['issue']['key']}
    for pr in evidence['implementation_prs']:
        sources.add(pr['pr']['html_url'])
    apply_edits(files, proposal, sources)
    reviewed = model_response({'sources': evidence, 'proposal': proposal},
                              'Pass 2: critically check every claim, release applicability, public-data suitability, '
                              'exact edits and writing. Return the corrected proposal or a blocker.')
    changes = apply_edits(files, reviewed, sources)
    image = build_image(checkout, root)
    build_docs(checkout, root / 'baseline', image)
    for path, content in changes.items():
        (checkout / path).write_text(content)
    build_docs(checkout, root / 'site', image)
    return reviewed, changes


def publish(info, proposal, changes, test, state):
    # Recheck current eligibility immediately before external publication.
    current = verify(EVENT)
    if (current['release'], current['base'], current['sha']) != (info['release'], info['base'], info['sha']):
        raise Blocked('Eligibility or base changed during drafting; review a fresh run.')
    prior = existing_pr(info, test)
    if prior:
        return prior
    head = 'automation/' + ('test-' if test else '') + info['issue']['key'].lower() + '-' + digest(info['release'])[:10]
    state.data['head'] = head
    state.data['stages']['publication'] = 'starting'
    state.save()
    commit = gh('git/commits/' + info['sha'])
    tree = gh('git/trees', 'POST', {'base_tree': commit['tree']['sha'], 'tree': [
        {'path': p, 'mode': '100644', 'type': 'blob', 'content': c} for p, c in changes.items()]})
    new_commit = gh('git/commits', 'POST', {'message': info['issue']['key'] + ': draft feature documentation',
                                         'tree': tree['sha'], 'parents': [info['sha']]})
    # A pre-existing head is never overwritten. Reconcile an interrupted run manually.
    gh('git/refs', 'POST', {'ref': 'refs/heads/' + head, 'sha': new_commit['sha']})
    claims = '\n'.join('| ' + ' | '.join(str(c[k]).replace('|', '\\|').replace('\n', ' ') for k in ['claim', 'source', 'locator']) + ' |'
                       for c in proposal['claims'])
    marker = '<!-- pcsm-automation-test -->\n**Controlled IT test. Do not merge.**\n\n' if test else ''
    body = (marker + proposal['summary'] + '\n\nJira: ' + SITE + '/browse/' + info['issue']['key']
            + '\n\n### Claim-to-source map\n\n| Claim | Source | Locator |\n| --- | --- | --- |\n' + claims)
    pr = gh('pulls', 'POST', {'head': head, 'base': info['base'], 'draft': True,
                              'title': ('[TEST] ' if test else '') + info['issue']['key'] + ': feature documentation', 'body': body})
    saved = gh('pulls/' + str(pr['number']))
    if not saved['draft'] or saved['head']['ref'] != head or saved['base']['ref'] != info['base']:
        raise Blocked('PR read-back did not match expected draft/head/base.')
    remote_files = {f['filename'] for f in gh_pages('pulls/' + str(pr['number']) + '/files')}
    if remote_files != set(changes):
        raise Blocked('PR file list verification failed.')
    state.data['pr_url'] = saved['html_url']
    state.data['stages']['publication'] = 'verified'
    state.save()
    return saved


def followups(info, pr, state, test):
    links = jira(f"/rest/api/3/issue/{info['issue']['key']}/remotelink")
    if not any(link.get('object', {}).get('url') == pr['html_url'] for link in links):
        jira(f"/rest/api/3/issue/{info['issue']['key']}/remotelink", 'POST', {
            'globalId': 'pcsm-docs-pr:' + str(pr['number']),
            'object': {'url': pr['html_url'], 'title': ('TEST: ' if test else '') + 'Documentation draft PR'}})
    verified = jira(f"/rest/api/3/issue/{info['issue']['key']}/remotelink")
    if not any(link.get('object', {}).get('url') == pr['html_url'] for link in verified):
        raise Blocked('Jira backlink was not verified.')
    state.data['stages']['backlink'] = 'verified'
    reviewer = os.environ.get('PCSM_COPILOT_REVIEWER', '')
    state.data['stages']['review'] = 'not_configured'
    if reviewer:
        try:
            result = gh(f"pulls/{pr['number']}/requested_reviewers", 'POST', {'reviewers': [reviewer]})
            requested = {r['login'] for r in result.get('requested_reviewers', [])}
            state.data['stages']['review'] = 'requested' if reviewer in requested else 'unverified'
        except ApiError:
            state.data['stages']['review'] = 'unavailable'
    state.save()


def process(event, test=False):
    activation = 'PCSM_DOCS_TEST_ENABLED' if test else 'PCSM_DOCS_ENABLED'
    if required(activation) != 'true':
        raise Blocked('Processing is disabled.')
    validate_event(event)
    if test and event['issue_key'] != 'PCSM-436':
        raise Blocked('Test-PR mode is restricted to PCSM-436.')
    for name in ('OPENAI_API_KEY', 'PCSM_DOCS_MODEL', 'SMTP_HOST', 'SMTP_USER', 'SMTP_PASSWORD', 'SMTP_FROM'):
        required(name)
    ensure_state_branch()
    state = State(event, test)
    if state.data['status'] == 'completed':
        return state.data
    if state.data['status'] != 'new':
        raise Blocked('Previous attempt requires manual reconciliation. No automatic replay of uncertain writes.')
    info = verify(event)
    lock = 'automation/pcsm-lock-' + event['issue_key'].lower()
    try:
        gh('git/refs', 'POST', {'ref': 'refs/heads/' + lock, 'sha': info['sha']})
    except ApiError as exc:
        if exc.status == 422:
            raise Blocked('Ticket is locked by another or interrupted run. Replay only after reconciliation.') from None
        raise
    # Re-read under the lock, in case another run completed between our read and acquisition.
    state = State(event, test)
    if state.data['status'] == 'completed':
        gh('git/refs/heads/' + lock, 'DELETE')
        return state.data
    if state.data['status'] != 'new':
        raise Blocked('Interrupted attempt remains locked for manual reconciliation.')
    state.data.update(status='running', run_id=os.environ.get('GITHUB_RUN_ID', 'local'), lock=lock)
    try:
        state.save()
        prefix = '[TEST] ' if test else ''
        notify(state, 'start_email', prefix + event['issue_key'] + ': documentation processing started',
               SITE + '/browse/' + event['issue_key'])
        pr = existing_pr(info, test)
        if not pr:
            evidence = collect_sources(info)
            with tempfile.TemporaryDirectory(prefix='pcsm-docs-') as directory:
                proposal, changes = draft_and_build(info, evidence, Path(directory))
                pr = publish(info, proposal, changes, test, state)
        followups(info, pr, state, test)
        state.data['pr_url'] = pr['html_url']
        notify(state, 'completion_email', prefix + event['issue_key'] + ': documentation processing finished',
               pr['html_url'] + '\nReview request: ' + state.data['stages'].get('review', 'existing PR reused'))
        state.data['status'] = 'completed'
        state.save()
        gh('git/refs/heads/' + lock, 'DELETE')
        return state.data
    except Exception:
        state.data['status'] = 'blocked'
        state.save()
        notify(state, 'completion_email', event['issue_key'] + ': documentation processing blocked',
               'Inspect the GitHub Actions run. Existing work is preserved; do not retry uncertain writes.\n'
               + state.data.get('pr_url', 'No verified PR recorded.'))
        # Preserve the lock after any failure; an operator must reconcile external writes.
        raise


EVENT = {}
if __name__ == '__main__':
    try:
        EVENT = json.loads(required('PCSM_EVENT_JSON'))
        mode = sys.argv[1]
        if mode == 'validate':
            info = verify(EVENT)
            print('Validated event, Jira history, board, Needs Doc, Fix version and documentation branch. No writes performed.')
        elif mode in ('process', 'test-pr'):
            result = process(EVENT, test=mode == 'test-pr')
            print(json.dumps({k: result[k] for k in ('status', 'pr_url', 'stages') if k in result}))
        else:
            raise Blocked('Unknown mode.')
    except (Blocked, KeyError, ValueError, TypeError) as exc:
        # Only application-authored blocker messages are public; never print raw source/API responses.
        print(str(exc) if isinstance(exc, Blocked) else 'Invalid configuration or incomplete evidence.', file=sys.stderr)
        sys.exit(1)
