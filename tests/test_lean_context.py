"""Exercise shared discovery and session context across adoption and host modes."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LeanContextTests(unittest.TestCase):
    def test_discovery_adapters_have_one_contract(self):
        """Each host must discover the same bounded contract."""
        for directory, suffix in [(ROOT, ''), (ROOT / 'skills/operating-model-bootstrap/assets/adapters', '.template')]:
            texts = [(directory / (name + '.md' + suffix)).read_text() for name in ('AGENTS', 'CLAUDE', 'GEMINI')]
            self.assertEqual(len(set(texts)), 1)
            self.assertLess(len(texts[0].encode()), 2400)

    def test_hook_modes_in_adopted_and_unadopted_consumers(self):
        """Default stays small; full/off and both payload formats retain meaning."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for adopted in (False, True):
                if adopted:
                    profile = root / 'docs/operating-model/PROJECT-OPERATING-PROFILE.md'
                    profile.parent.mkdir(parents=True)
                    profile.write_text('fixture')
                for claude in (False, True):
                    for mode in ('auto', 'pointer', 'full', 'off'):
                        env = os.environ.copy()
                        env.pop('CLAUDE_PLUGIN_ROOT', None)
                        env['JOIN_THE_TEAM_ORIENTATION'] = mode
                        if claude:
                            env['CLAUDE_PLUGIN_ROOT'] = str(ROOT)
                        result = subprocess.run(['bash', str(ROOT / 'hooks/session-start')], cwd=root, env=env, text=True, capture_output=True, check=True)
                        if mode == 'off':
                            self.assertEqual(result.stdout, '')
                            continue
                        payload = json.loads(result.stdout)
                        context = (payload['hookSpecificOutput'] if claude else payload)['additionalContext']
                        if mode == 'full':
                            self.assertIn((ROOT / 'skills/using-the-harness/SKILL.md').read_text().strip(), context)
                        else:
                            self.assertLess(len(context.encode()), 1200)
                            self.assertEqual('Project contract:' in context, adopted)
                            self.assertNotIn('## Skill routing', context)
