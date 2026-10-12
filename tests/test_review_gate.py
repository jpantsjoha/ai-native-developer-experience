"""Offline review-gate regressions: fake review/GitHub CLIs never spend quota or use network."""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'review-gate.sh'
REAL_GIT = shutil.which('git')
FAKE_LANE = r'''
import json, os, pathlib, subprocess, sys, time
pathlib.Path(os.environ['LANE_LOG']).write_text(json.dumps(sys.argv))
pathlib.Path(os.environ['LANE_PID']).write_text(str(os.getpid()))
mode = os.environ.get('FAKE_MODE', 'pass')
if mode == 'async_wait':
    deadline = time.monotonic() + 10
    while not pathlib.Path(os.environ['LANE_RELEASE']).exists():
        if time.monotonic() > deadline:
            sys.exit(9)
        time.sleep(0.02)
if mode == 'timeout':
    print('VERDICT: PASS', flush=True)
    time.sleep(10)
if mode == 'change':
    pathlib.Path('a').write_text('changed during review\n')
    subprocess.run(['git', 'add', 'a'], check=True)
if mode == 'prompt_change':
    gitdir = subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir']).decode().strip()
    for prompt in pathlib.Path(gitdir, 'review-gate').glob('run-*/prompt'):
        prompt.write_text('replacement')
if mode == 'pr_change':
    pathlib.Path(os.environ['PR_CHANGED']).write_text('changed')
values = {
    'concerns': 'VERDICT: CONCERNS\n', 'block': 'VERDICT: BLOCK\n',
    'missing': 'Everything looks good\n',
    'multiple': 'VERDICT: BLOCK\nVERDICT: PASS\n',
    'duplicate': 'VERDICT: PASS\nVERDICT: PASS\n',
    'malformed': 'VERDICT: PASS with conditions\n',
    'nonfinal': 'VERDICT: PASS\nOne more thing\n',
    'indented': ' VERDICT: PASS\n',
    'stderr': 'No verdict here\n',
    'long': 'full output ' * 10000 + '\nVERDICT: PASS\n',
}
answer = values.get(mode, 'Checked the full diff. Candidate binding, failed provider exits, input integrity and local receipt semantics match the stated contract; no blocking correctness or security finding remains.\nVERDICT: PASS\n')
if pathlib.Path(sys.argv[0]).name == 'claude':
    model = sys.argv[sys.argv.index('--model') + 1]
    envelope = {'type': 'result', 'subtype': 'success', 'is_error': False,
                'result': answer, 'modelUsage': {model: {'inputTokens': 12}}}
    if mode == 'api_error': envelope.update(is_error=True, result='Session limit; VERDICT: PASS')
    if mode == 'wrong_model': envelope['modelUsage'] = {'wrong-model': {}}
    if mode == 'no_model': envelope['modelUsage'] = {}
    if mode == 'one_line': envelope['result'] = 'VERDICT: PASS'
    if mode == 'bad_json':
        sys.stdout.write('{'); sys.exit(0)
    sys.stdout.write(json.dumps(envelope))
else:
    sys.stdout.write(answer)
if mode == 'stderr':
    sys.stderr.write('VERDICT: PASS\n')
sys.exit(3 if mode == 'fail' else 0)
'''
FAKE_GH = r'''
import json, os, pathlib, sys
args = sys.argv[1:]
with open(os.environ['GH_LOG'], 'a') as log:
    log.write(json.dumps(args) + '\n')
if os.environ.get('GH_FAIL') == args[1]:
    if args[1] == 'diff':
        print('partial nonempty diff')
    sys.exit(2)
if args[1] == 'view':
    changed = pathlib.Path(os.environ['PR_CHANGED']).exists()
    print(json.dumps({'baseRefOid': 'a' * 40, 'headRefOid': ('c' if changed else 'b') * 40,
                      'commits': [{'oid': 'b' * 40, 'messageHeadline': 'change'}]}))
elif args[1] == 'diff':
    if os.environ.get('GH_BINARY'):
        print('diff --git a/payload.bin b/payload.bin\nBinary files a/payload.bin and b/payload.bin differ')
    else:
        print('diff --git a/a b/a\n--- a/a\n+++ b/a\n@@ -1 +1 @@\n-old\n+new')
elif args[1] == 'comment':
    pathlib.Path(os.environ['COMMENT']).write_text(pathlib.Path(args[-1]).read_text())
else:
    sys.exit(9)
'''
FAKE_GIT = r'''
import os, sys
args = sys.argv[1:]
if os.environ.get('GIT_FAIL') == args[0]:
    print('partial nonempty input')
    sys.exit(4)
os.execv(os.environ['REAL_GIT'], [os.environ['REAL_GIT']] + args)
'''


class ReviewGateTests(unittest.TestCase):
    """Exercise real Git snapshots while keeping external review providers fake."""

    def setUp(self):
        """Create an isolated repository and a PATH containing only fake review CLIs."""
        self.temp = tempfile.TemporaryDirectory(prefix='review-gate-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(('REVIEW_GATE', 'GIT_'))}
        self.env.update(PATH=f'{self.bin}:/usr/bin:/bin',
                        GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1',
                        REAL_GIT=REAL_GIT, REVIEW_GATE_LANE='agy', REVIEW_GATE_MODEL='fixture-model',
                        LANE_LOG=str(self.root / 'lane.json'), LANE_PID=str(self.root / 'lane.pid'),
                        LANE_RELEASE=str(self.root / 'lane.release'),
                        GH_LOG=str(self.root / 'gh.log'),
                        PR_CHANGED=str(self.root / 'pr.changed'), COMMENT=str(self.root / 'comment'))
        (self.bin / 'python3').symlink_to(sys.executable)
        for name, body in [('agy', FAKE_LANE), ('gemini', FAKE_LANE),
                           ('claude', FAKE_LANE), ('gh', FAKE_GH), ('git', FAKE_GIT)]:
            path = self.bin / name
            path.write_text(f'#!{sys.executable}\n' + body)
            path.chmod(0o755)
        self.git('init')
        self.git('config', 'user.name', 'Offline test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.repo / 'a').write_text('old\n')
        self.git('add', 'a')
        self.git('-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'base')
        self.base = self.git('rev-parse', 'HEAD').stdout.strip()
        (self.repo / 'a').write_text('new\n')
        self.git('add', 'a')

    def git(self, *args):
        """Run local Git fixture setup, failing immediately on setup errors."""
        return subprocess.run([REAL_GIT, *args], cwd=self.repo, env=self.env,
                              text=True, capture_output=True, check=True)

    def gate(self, *args, **env):
        """Run the real gate with controlled fake CLI behaviour and a hard test timeout."""
        return subprocess.run(['bash', str(SCRIPT), *(args or ('--staged',))],
                              cwd=self.repo, env={**self.env, **env}, text=True,
                              capture_output=True, timeout=15)

    def records(self):
        """Return local receipt paths, using the worktree's actual Git directory."""
        gitdir = self.git('rev-parse', '--absolute-git-dir').stdout.strip()
        return list(Path(gitdir, 'review-gate').glob('run-*/result.json'))

    def test_success_propagates_exact_candidate_and_full_artifacts(self):
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)
        path, = self.records()
        receipt = json.loads(path.read_text())
        self.assertEqual(receipt['result'], 'PASS')
        self.assertEqual(receipt['lane_exit'], 0)
        self.assertEqual(receipt['identity']['base'], self.base)
        self.assertEqual(receipt['identity']['head'], self.base)
        self.assertEqual(receipt['identity']['staged_tree'], self.git('write-tree').stdout.strip())
        self.assertEqual(len(receipt['identity']['diff_sha256']), 64)
        self.assertTrue((path.parent / 'diff').read_bytes())
        self.assertIn(b'VERDICT: PASS', (path.parent / 'stdout').read_bytes())

    def test_explicit_adapter_receives_complete_stdin_and_no_shell_arguments(self):
        adapter = self.root / 'review adapter'
        adapter.write_text(f'#!{sys.executable}\n' +
                          'import os, pathlib, sys\n' +
                          "pathlib.Path(os.environ['LANE_LOG']).write_bytes(sys.stdin.buffer.read())\n" +
                          "assert len(sys.argv) == 1\n" +
                          "assert os.environ['REVIEW_GATE_MODEL'] == 'fixture-model'\n" +
                          "print('Reviewed the complete supplied candidate and its boundaries. "
                          "The input contains the full change, and no correctness, security or "
                          "evidence conditions remain within this limited review scope.')\n" +
                          "print('VERDICT: PASS')\n")
        adapter.chmod(0o755)
        result = self.gate(REVIEW_GATE_LANE='adapter', REVIEW_GATE_ADAPTER=str(adapter))
        self.assertEqual(result.returncode, 0, result.stderr)
        path, = self.records()
        self.assertEqual(Path(self.env['LANE_LOG']).read_bytes(),
                         (path.parent / 'prompt').read_bytes())
        receipt = json.loads(path.read_text())
        self.assertEqual(receipt['lane_kind'], 'adapter')
        self.assertNotIn('resolved_model', receipt)

    def test_missing_or_relative_adapter_refuses_without_fallback(self):
        for adapter in ('', 'agy', str(self.root / 'absent')):
            with self.subTest(adapter=adapter):
                result = self.gate(REVIEW_GATE_LANE='adapter', REVIEW_GATE_ADAPTER=adapter)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(Path(self.env['LANE_LOG']).exists())

    def test_all_nonapprovals_refuse(self):
        for mode in ('concerns', 'block', 'missing', 'multiple', 'duplicate', 'malformed',
                     'nonfinal', 'indented', 'stderr', 'fail'):
            with self.subTest(mode=mode):
                result = self.gate(FAKE_MODE=mode)
                self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_failed_lane_printing_pass_retains_error_evidence(self):
        self.assertNotEqual(self.gate(FAKE_MODE='fail').returncode, 0)
        path, = self.records()
        self.assertIn(b'VERDICT: PASS', (path.parent / 'stdout').read_bytes())
        self.assertEqual(json.loads(path.read_text())['lane_exit'], 3)

    def test_timeout_printing_pass_refuses(self):
        result = self.gate(FAKE_MODE='timeout', REVIEW_GATE_TIMEOUT='1')
        self.assertNotEqual(result.returncode, 0)
        path, = self.records()
        self.assertTrue(json.loads(path.read_text())['timed_out'])

    def test_cancellation_kills_owned_lane_and_refuses(self):
        process = subprocess.Popen(['bash', str(SCRIPT), '--staged'], cwd=self.repo,
                                   env={**self.env, 'FAKE_MODE': 'timeout'},
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: process.poll() is None and process.kill())
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and not Path(self.env['LANE_PID']).exists():
            time.sleep(0.05)
        lane_pid = int(Path(self.env['LANE_PID']).read_text())
        process.send_signal(signal.SIGTERM)
        stdout, stderr = process.communicate(timeout=5)
        self.assertNotEqual(process.returncode, 0, stdout)
        self.assertIn(b'interrupted', stderr)
        with self.assertRaises(ProcessLookupError):
            os.kill(lane_pid, 0)

    def test_explicit_missing_lane_does_not_fall_back(self):
        (self.bin / 'agy').unlink()
        result = self.gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(Path(self.env['LANE_LOG']).exists())

    def test_no_lane_refuses(self):
        (self.bin / 'agy').unlink()
        (self.bin / 'gemini').unlink()
        self.assertNotEqual(self.gate(REVIEW_GATE_LANE='').returncode, 0)

    def test_changed_candidate_and_prompt_refuse(self):
        for mode in ('change', 'prompt_change'):
            with self.subTest(mode=mode):
                self.assertNotEqual(self.gate(FAKE_MODE=mode).returncode, 0)

    def test_diff_or_log_acquisition_failure_refuses(self):
        self.assertNotEqual(self.gate(GIT_FAIL='diff').returncode, 0)
        self.assertFalse(Path(self.env['LANE_LOG']).exists())
        self.commit_change()
        self.assertNotEqual(self.gate('--range', f'{self.base}..HEAD', GIT_FAIL='log').returncode, 0)
        self.assertFalse(Path(self.env['LANE_LOG']).exists())

    def test_oversized_bytes_and_lines_refuse_without_lane_call(self):
        for settings in ({'REVIEW_GATE_MAXBYTES': '100'}, {'REVIEW_GATE_MAXLINES': '1'},
                         {'REVIEW_GATE_MAXBYTES': '1000000'}):
            with self.subTest(settings=settings):
                self.assertNotEqual(self.gate(**settings).returncode, 0)
                self.assertFalse(Path(self.env['LANE_LOG']).exists())
        (self.repo / 'a').write_text('x' * 70000)
        self.git('add', 'a')
        self.assertNotEqual(self.gate().returncode, 0)
        self.assertFalse(Path(self.env['LANE_LOG']).exists())

    def test_review_output_is_not_truncated(self):
        self.assertEqual(self.gate(FAKE_MODE='long').returncode, 0)
        path, = self.records()
        self.assertGreater((path.parent / 'stdout').stat().st_size, 100000)

    def test_pr_defaults_no_comment_and_records_base_head(self):
        result = self.gate('--pr', '123')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(Path(self.env['COMMENT']).exists())
        path, = self.records()
        identity = json.loads(path.read_text())['identity']
        self.assertEqual(identity['base'], 'a' * 40)
        self.assertEqual(identity['head'], 'b' * 40)

    def test_pr_binary_omission_refuses_before_review(self):
        result = self.gate('--pr', '123', GH_BINARY='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('omits binary content', result.stderr)
        self.assertFalse(Path(self.env['LANE_LOG']).exists())
        self.assertFalse(Path(self.env['COMMENT']).exists())

    def test_explicit_comment_posts_only_after_pass(self):
        self.assertEqual(self.gate('--pr', '123', '--comment').returncode, 0)
        self.assertEqual(json.loads(Path(self.env['COMMENT']).read_text())['result'], 'PASS')
        Path(self.env['COMMENT']).unlink()
        self.assertNotEqual(self.gate('--pr', '123', '--comment', FAKE_MODE='block').returncode, 0)
        self.assertFalse(Path(self.env['COMMENT']).exists())

    def test_failed_pr_acquisition_and_changed_head_refuse(self):
        for settings in ({'GH_FAIL': 'diff'}, {'GH_FAIL': 'view'}, {'FAKE_MODE': 'pr_change'}):
            with self.subTest(settings=settings):
                self.assertNotEqual(self.gate('--pr', '123', **settings).returncode, 0)
        self.assertFalse(Path(self.env['COMMENT']).exists())

    def commit_change(self):
        """Commit the staged fixture to form a nonempty two-commit review range."""
        self.git('-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'change')

    def test_range_resolves_full_base_and_head(self):
        self.commit_change()
        result = self.gate('--range', f'{self.base}..HEAD')
        self.assertEqual(result.returncode, 0, result.stderr)
        path, = self.records()
        identity = json.loads(path.read_text())['identity']
        self.assertEqual(identity['base'], self.base)
        self.assertEqual(identity['head'], self.git('rev-parse', 'HEAD').stdout.strip())
        for value in ('missing..HEAD', f'{self.base}...HEAD', '..HEAD'):
            self.assertNotEqual(self.gate('--range', value).returncode, 0)

    def test_unique_runs_and_last_are_advisory_only(self):
        self.assertEqual(self.gate().returncode, 0)
        self.assertEqual(self.gate().returncode, 0)
        self.assertEqual(len(self.records()), 2)
        result = self.gate('--last')
        self.assertIn('never approval', result.stdout)
        self.assertNotEqual(self.gate(FAKE_MODE='block').returncode, 0)

    def test_worktree_records_use_actual_git_directory(self):
        worktree = self.root / 'worktree'
        self.git('worktree', 'add', '-b', 'test-lane', str(worktree))
        self.repo = worktree
        (self.repo / 'a').write_text('worktree change\n')
        self.git('add', 'a')
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stderr)
        path, = self.records()
        self.assertIn('/worktrees/', str(path))

    def test_gemini_lane_keeps_supported_arguments(self):
        result = self.gate(REVIEW_GATE_LANE='gemini')
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = json.loads(Path(self.env['LANE_LOG']).read_text())
        self.assertEqual(argv[1], '-p')
        self.assertEqual(argv[3], '-m')

    def test_async_receipt_is_advisory(self):
        result = self.gate('--staged', '--mode', 'async')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('no approval', result.stdout)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            records = self.records()
            if records and (records[0].parent / 'worker.log').read_text():
                break
            time.sleep(0.05)
        path, = self.records()
        self.assertTrue((path.parent / 'worker.log').read_text())
        receipt = json.loads(path.read_text())
        self.assertTrue(receipt['advisory'])
        self.assertEqual(receipt['result'], 'PASS')

    def wait_for_async_receipt(self):
        """Wait for the detached worker to finish writing its receipt and final output."""
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            records = self.records()
            if records and (records[0].parent / 'worker.log').read_text():
                return records[0]
            time.sleep(0.05)
        self.fail('advisory worker did not complete')

    def test_async_snapshot_survives_successful_commit(self):
        original_tree = self.git('write-tree').stdout.strip()
        result = self.gate('--staged', '--mode', 'async', FAKE_MODE='async_wait')
        self.assertEqual(result.returncode, 0, result.stderr)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and not Path(self.env['LANE_LOG']).exists():
            time.sleep(0.05)
        self.assertTrue(Path(self.env['LANE_LOG']).exists())
        self.commit_change()
        self.assertNotEqual(self.git('rev-parse', 'HEAD').stdout.strip(), self.base)
        self.assertEqual(self.git('diff', '--cached').stdout, '')
        Path(self.env['LANE_RELEASE']).touch()
        path = self.wait_for_async_receipt()
        receipt = json.loads(path.read_text())
        self.assertEqual(receipt['result'], 'PASS', receipt)
        self.assertTrue(receipt['advisory'])
        self.assertEqual(receipt['identity']['staged_tree'], original_tree)
        self.assertEqual(receipt['identity']['base'], self.base)
        # A worker starting after the commit must also review the saved snapshot.
        replay = self.gate('--worker', path.parent.name)
        self.assertEqual(replay.returncode, 0, replay.stderr)

    def test_async_snapshot_file_tampering_refuses_before_lane(self):
        result = self.gate('--staged', '--mode', 'async')
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.wait_for_async_receipt()
        for artifact in ('diff', 'commits', 'prompt'):
            with self.subTest(artifact=artifact):
                source = path.parent / artifact
                original = source.read_bytes()
                source.write_bytes(original + b'tampered')
                Path(self.env['LANE_LOG']).unlink(missing_ok=True)
                result = self.gate('--worker', path.parent.name)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(Path(self.env['LANE_LOG']).exists())
                source.write_bytes(original)

    def test_invalid_arguments_and_configuration_refuse(self):
        for args in (('--pr',), ('--staged', '--comment'), ('--wat',), ('--pr', '-1'),
                     ('--pr', '123', '--comment', '--mode', 'async')):
            self.assertNotEqual(self.gate(*args).returncode, 0)
        for settings in ({'REVIEW_GATE_TIMEOUT': '0'}, {'REVIEW_GATE_TIMEOUT': 'bad'},
                         {'REVIEW_GATE_LANE': 'made-up'}, {'REVIEW_GATE': 'nonsense'}):
            self.assertNotEqual(self.gate(**settings).returncode, 0)

    def test_claude_transport_is_explicit_readonly_and_identity_bound(self):
        result = self.gate(REVIEW_GATE_LANE='claude', REVIEW_GATE_MODEL='claude-opus-5-5')
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = json.loads(Path(self.env['LANE_LOG']).read_text())
        for flag in ('--safe-mode', '--strict-mcp-config', '--no-session-persistence'):
            self.assertIn(flag, argv)
        self.assertEqual(argv[argv.index('--tools') + 1], '')
        self.assertEqual(argv[argv.index('--permission-mode') + 1], 'dontAsk')
        self.assertNotIn('--fallback-model', argv)
        path, = self.records()
        self.assertEqual(json.loads(path.read_text())['resolved_model'], 'claude-opus-5-5')

    def test_claude_errors_and_model_substitution_never_approve(self):
        for mode in ('api_error', 'wrong_model', 'no_model', 'one_line', 'bad_json', 'fail'):
            with self.subTest(mode=mode):
                result = self.gate(REVIEW_GATE_LANE='claude', FAKE_MODE=mode)
                self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_configuration_required_even_when_providers_exist(self):
        for settings in ({'REVIEW_GATE_LANE': ''}, {'REVIEW_GATE_MODEL': ''}):
            with self.subTest(settings=settings):
                self.assertNotEqual(self.gate(**settings).returncode, 0)
                self.assertFalse(Path(self.env['LANE_LOG']).exists())


if __name__ == '__main__':
    unittest.main()
