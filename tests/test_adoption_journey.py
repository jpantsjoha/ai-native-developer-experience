"""Exercise documented adoption from installed packages and copied skill directories."""

from __future__ import annotations

import hashlib
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def snapshot(root: Path) -> dict[str, str]:
    """Fingerprint package files to detect accidental writes during adoption."""
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob('*') if path.is_file()
    }


class AdoptionJourneyTests(unittest.TestCase):
    """Run real scripts from a consumer cwd with no local package assumption."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix='harness adoption ')
        self.base = Path(self.temp.name)
        self.package = self.base / 'plugin cache with spaces'
        self.project = self.base / 'consumer project'
        self.project.mkdir()
        shutil.copytree(ROOT / 'skills', self.package / 'skills',
                        ignore=shutil.ignore_patterns('__pycache__'))
        self.before = snapshot(self.package)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_args(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        """Execute an extracted command without shell expansion or a live model."""
        return subprocess.run(args, cwd=self.project, text=True,
                              capture_output=True, check=False)

    def command(self, name: str) -> list[str]:
        """Apply the documented host substitution to the actual command Markdown."""
        content = (ROOT / 'commands' / f'{name}.md').read_text()
        match = re.search(r'python3 [^\n`]+', content)
        self.assertIsNotNone(match, name)
        line = match.group().replace('${CLAUDE_PLUGIN_ROOT}', str(self.package))
        line = line.replace('<project name>', 'Adoption Trial')
        args = shlex.split(line)
        args[0] = sys.executable
        return args

    def test_plugin_commands_bootstrap_inspect_validate_without_local_skills(self) -> None:
        args = self.command('bootstrap')
        dry = self.run_args(args)
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertEqual(list(self.project.iterdir()), [])
        args.remove('--dry-run')
        installed = self.run_args(args)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.assertFalse((self.project / '.agents').exists())
        for name in ['init', 'validate']:
            result = self.run_args(self.command(name))
            self.assertEqual(result.returncode, 0, result.stderr)
        followup = next(line.removeprefix('NEXT run: ') for line in
                        installed.stdout.splitlines() if line.startswith('NEXT run: '))
        checked = self.run_args(shlex.split(followup))
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertIn('PASS operating-model validation', checked.stdout)
        repeat = self.run_args(args)
        self.assertEqual(repeat.returncode, 0, repeat.stderr)
        self.assertIn('unchanged: 12 matching file(s)', repeat.stdout)
        self.assertEqual(snapshot(self.package), self.before)
        for name in ['AGENTS.md', 'CLAUDE.md', 'GEMINI.md']:
            content = (self.project / name).read_text()
            self.assertIn('project or user scope', content)
            self.assertNotIn(str(self.package), content)
            self.assertNotIn('skills live under `.agents/skills/`', content)

    def test_documented_asset_validation_from_external_install(self) -> None:
        skill = self.package / 'skills/operating-model-bootstrap'
        content = (skill / 'SKILL.md').read_text()
        block = next(block for block in re.findall(r'```bash\n(.*?)```', content, re.S)
                     if '--template-root' in block)
        command = block.replace('<bootstrap-skill-dir>', str(skill))
        command = command.replace('\\\n', ' ')
        args = shlex.split(command)
        args[0] = sys.executable
        result = self.run_args(args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PASS operating-model validation', result.stdout)
        self.assertEqual(list(self.project.iterdir()), [])
        self.assertEqual(snapshot(self.package), self.before)

    def test_plugin_conflict_preserves_project_and_package(self) -> None:
        (self.project / 'AGENTS.md').write_text('Existing team authority\n')
        before = snapshot(self.project)
        args = self.command('bootstrap')
        args.remove('--dry-run')
        result = self.run_args(args)
        self.assertEqual(result.returncode, 2)
        self.assertIn('refusing to overwrite', result.stderr)
        self.assertEqual(snapshot(self.project), before)
        self.assertEqual(snapshot(self.package), self.before)

    def test_copied_project_and_user_skills_use_the_same_scripts(self) -> None:
        for scope in ['project', 'user']:
            with self.subTest(scope=scope):
                project = self.base / f'{scope} consumer'
                project.mkdir()
                skills = (project / '.agents/skills' if scope == 'project'
                          else self.base / 'user home/.agents/skills')
                shutil.copytree(ROOT / 'skills', skills,
                                ignore=shutil.ignore_patterns('__pycache__'))
                scripts = skills / 'operating-model-bootstrap/scripts'
                before = snapshot(skills)
                for script, args in [
                    ('bootstrap_operating_model.py', ['--project-name', 'Scope trial', str(project)]),
                    ('inspect_repo.py', [str(project)]),
                    ('validate_operating_model.py', ['--target', str(project)]),
                ]:
                    result = subprocess.run([sys.executable, str(scripts / script), *args],
                                            cwd=project, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(snapshot(skills), before)
                if scope == 'user':
                    self.assertFalse((project / '.agents').exists())


if __name__ == '__main__':
    unittest.main()
