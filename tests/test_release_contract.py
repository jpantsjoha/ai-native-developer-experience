"""Exercise release preflight through the operating-model CLI with synthetic receipts."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/operating-model-bootstrap/scripts'
FIELDS = {
    'mode': 'Release mode', 'build_trigger': 'Build trigger',
    'build_executor': 'Build executor', 'promotion_trigger': 'Promotion trigger',
    'release_owner': 'Release owner', 'release_decision': 'Release decision',
}


class ReleaseContractTests(unittest.TestCase):
    """Guard policy consistency without pretending synthetic receipts are authority."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        install = subprocess.run(
            [sys.executable, str(SCRIPTS / 'bootstrap_operating_model.py'),
             '--project-name', 'Fixture', str(self.root)], capture_output=True, text=True,
        )
        self.assertEqual(install.returncode, 0, install.stderr)
        self.profile = self.root / 'docs/operating-model/PROJECT-OPERATING-PROFILE.md'
        self.original = re.sub(r'<[^>\n]+>', 'fixture value', self.profile.read_text()).replace(
            '**Adoption status:** seed', '**Adoption status:** active').replace(
                'inferred — source:', 'fixture provenance:')
        self.policy = {
            'mode': 'tag-ci', 'build_trigger': 'tag', 'build_executor': 'ci',
            'promotion_trigger': 'separate-approval', 'release_owner': 'Fixture owner',
            'release_decision': 'release-decision.md',
        }
        (self.root / 'release-decision.md').write_text('Synthetic approved decision fixture\n')
        self.record = {
            'schema_version': 1, 'policy': copy.deepcopy(self.policy),
            'candidate': 'a' * 40, 'artifact_sha256': 'b' * 64,
            'decision_sha256': hashlib.sha256((self.root / 'release-decision.md').read_bytes()).hexdigest(),
            'review_candidate': 'a' * 40, 'review_verdict': 'PASS',
            'receipts': {k: f'{k}.txt' for k in (
                'approval', 'build', 'validation', 'review', 'rollback', 'observation_plan')},
        }
        for name in self.record['receipts'].values():
            (self.root / name).write_text('Synthetic evidence fixture; no live approval\n')
        self.write_profile()

    def write_profile(self) -> None:
        """Replace any generated placeholders with one explicit test policy."""
        text = self.original
        for label in FIELDS.values():
            text = re.sub(rf'^\*\*{label}:\*\*[^\n]*\n?', '', text, flags=re.M)
        self.profile.write_text(text + '\n' + '\n'.join(
            f'**{FIELDS[k]}:** {v}' for k, v in self.policy.items()) + '\n')

    def run_gate(self, record=None, extra=()) -> subprocess.CompletedProcess[str]:
        """Run an isolated preflight; nonzero is expected for planted defects."""
        (self.root / 'release.json').write_text(json.dumps(self.record if record is None else record))
        return subprocess.run(
            [sys.executable, str(SCRIPTS / 'validate_operating_model.py'),
             '--target', str(self.root), '--release-evidence', 'release.json',
             '--candidate', 'a' * 40, *extra], capture_output=True, text=True,
        )

    def rejected(self, record=None, message='') -> None:
        """Require a normal validation failure, not a parser error or traceback."""
        result = self.run_gate(record)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(message, result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_default_policy_and_receipts_pass_structurally(self):
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('release structure only', result.stdout)

    def test_approved_alternative_requires_same_evidence(self):
        self.policy.update(mode='approved-alternative', build_trigger='manual',
                           build_executor='controlled-runner')
        self.write_profile()
        self.record['policy'] = copy.deepcopy(self.policy)
        self.assertEqual(self.run_gate().returncode, 0)
        del self.record['receipts']['approval']
        self.rejected(message='receipts')

    def test_missing_each_policy_field_fails(self):
        original = self.policy.copy()
        for field in original:
            with self.subTest(field=field):
                self.policy = {k: v for k, v in original.items() if k != field}
                self.write_profile()
                self.rejected(message=FIELDS[field])

    def test_duplicate_policy_field_fails(self):
        self.profile.write_text(self.profile.read_text() + '\n**Release mode:** tag-ci\n')
        self.rejected(message='Release mode')

    def test_contradictory_or_unknown_policy_fails(self):
        original = self.policy.copy()
        for changes in ({'mode': 'anything'}, {'build_trigger': 'manual'},
                        {'build_executor': 'controlled-runner'},
                        {'promotion_trigger': 'automatic'},
                        {'mode': 'approved-alternative', 'build_trigger': 'manual',
                         'promotion_trigger': 'tag'}):
            with self.subTest(changes=changes):
                self.policy = dict(original, **changes)
                self.write_profile()
                self.record['policy'] = self.policy.copy()
                self.rejected(message='release policy')

    def test_stale_policy_and_candidates_fail(self):
        for key, value in [('policy', dict(self.policy, build_trigger='manual')),
                           ('candidate', 'c' * 40), ('review_candidate', 'c' * 40),
                           ('review_verdict', 'PASS_WITH_CONDITIONS'),
                           ('artifact_sha256', ''), ('schema_version', True)]:
            with self.subTest(key=key):
                record = dict(self.record, **{key: value})
                self.rejected(record, 'release')

    def test_each_receipt_required_and_nonempty(self):
        for key, path in self.record['receipts'].items():
            with self.subTest(key=key):
                record = copy.deepcopy(self.record)
                del record['receipts'][key]
                self.rejected(record, 'receipts')
                file = self.root / path
                saved = file.read_text()
                file.write_text(' \n')
                self.rejected(message='empty')
                file.unlink()
                self.rejected(message='missing')
                file.write_text(saved)

    def test_changed_decision_invalidates_record(self):
        (self.root / self.policy['release_decision']).write_text('Changed decision')
        self.rejected(message='decision digest')

    def test_missing_decision_fails(self):
        (self.root / self.policy['release_decision']).unlink()
        self.rejected(message='missing')

    def test_outside_symlink_and_absolute_receipt_fail(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other) / 'receipt.txt'
            outside.write_text('outside')
            (self.root / 'escape').symlink_to(outside)
            for path in ['escape', str(outside), '../receipt.txt']:
                with self.subTest(path=path):
                    self.record['receipts']['review'] = path
                    self.rejected(message='project-relative')

    def test_wrong_shapes_unknown_fields_fail(self):
        for record in [[], None, dict(self.record, unexpected=True),
                       dict(self.record, policy=[]), dict(self.record, receipts=[]),
                       dict(self.record, candidate=23)]:
            with self.subTest(record=record):
                if record is None:
                    record = {'schema_version': 1}
                self.rejected(record, 'release')

    def test_seed_cannot_pass_release_preflight(self):
        self.profile.write_text(self.profile.read_text().replace(
            '**Adoption status:** active', '**Adoption status:** seed'))
        self.rejected(message='active profile required')

    def test_malformed_and_duplicate_json_fail_closed(self):
        for text in ['{', '{"schema_version": 1, "schema_version": 1}']:
            (self.root / 'bad.json').write_text(text)
            result = self.run_gate(extra=('--release-evidence', 'bad.json'))
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('release', result.stderr)
            self.assertNotIn('Traceback', result.stderr)

    def test_template_mode_cannot_skip_release_check(self):
        result = self.run_gate(extra=('--template-root', str(SCRIPTS.parent)))
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
