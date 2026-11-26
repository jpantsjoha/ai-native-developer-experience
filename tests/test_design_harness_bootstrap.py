"""Bootstrap offers the design/records harness as opt-in steps and never overwrites."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "operating-model-bootstrap"
BOOTSTRAP = SKILL / "scripts" / "bootstrap_operating_model.py"
STEPS = ("records-guard", "ui-context", "post-edit-ratchet", "ratchet-config")


def bootstrap(target: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(BOOTSTRAP), "--project-name", "Scratch", *args,
                           str(target)], capture_output=True, text=True)


class BootstrapAdoptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp.name) / "scratch"
        self.target.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_dry_run_lists_every_opt_in_step_and_writes_nothing(self) -> None:
        result = bootstrap(self.target, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        for step in STEPS:
            self.assertIn(f"opt-in, not installed: --adopt {step}", result.stdout)
        self.assertEqual(list(self.target.rglob("*")), [])

    def test_dry_run_with_adopt_still_writes_nothing(self) -> None:
        result = bootstrap(self.target, "--dry-run", "--adopt", "all")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("would create: .devex/hooks/records-guard.py", result.stdout)
        self.assertEqual(list(self.target.rglob("*")), [])

    def test_default_install_adds_no_harness_files(self) -> None:
        self.assertEqual(bootstrap(self.target).returncode, 0)
        self.assertFalse((self.target / ".devex").exists())
        self.assertFalse((self.target / ".claude").exists())

    def test_adopt_all_installs_executables_and_enables_nothing(self) -> None:
        result = bootstrap(self.target, "--adopt", "all")
        self.assertEqual(result.returncode, 0, result.stderr)
        hooks = self.target / ".devex" / "hooks"
        for name in ("records-guard.py", "ui-context.py", "post-edit-ratchet.py", "literal-ratchet.py"):
            self.assertTrue(os.access(hooks / name, os.X_OK), name)
        json.loads((self.target / ".devex/ratchet.config.json").read_text())
        self.assertFalse((self.target / ".claude/settings.json").exists())
        self.assertIn("nothing is enabled automatically", result.stdout)

    def test_adopt_single_step_installs_only_that_step(self) -> None:
        bootstrap(self.target, "--adopt", "records-guard")
        self.assertTrue((self.target / ".devex/hooks/records-guard.py").is_file())
        self.assertFalse((self.target / ".devex/hooks/ui-context.py").exists())

    def test_existing_different_file_is_preserved_never_overwritten(self) -> None:
        config = self.target / ".devex" / "ratchet.config.json"
        config.parent.mkdir()
        config.write_text('{"mine": true}\n')
        result = bootstrap(self.target, "--adopt", "ratchet-config")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(config.read_text(), '{"mine": true}\n')
        self.assertIn("preserved existing: .devex/ratchet.config.json", result.stdout)

    def test_preserved_step_is_reported_preserved_not_adopted(self) -> None:
        config = self.target / ".devex" / "ratchet.config.json"
        config.parent.mkdir()
        config.write_text('{"mine": true}\n')
        result = bootstrap(self.target, "--adopt", "ratchet-config")
        self.assertIn("preserved: --adopt ratchet-config", result.stdout)
        self.assertNotIn("adopted: --adopt ratchet-config", result.stdout)

    def test_adopted_hook_runs_from_the_installed_copy(self) -> None:
        bootstrap(self.target, "--adopt", "post-edit-ratchet", "--adopt", "ratchet-config")
        (self.target / "a.css").write_text(".a { color: #ff0000; }\n")
        engine = self.target / ".devex/hooks/literal-ratchet.py"
        subprocess.run([sys.executable, str(engine), "--root", str(self.target), "--update-baseline"],
                       check=True, capture_output=True)
        (self.target / "a.css").write_text(".a { color: #ff0000; } .b { color: #00ff00; }\n")
        payload = json.dumps({"tool_name": "Write", "cwd": str(self.target),
                              "tool_input": {"file_path": str(self.target / "a.css")}})
        out = subprocess.run([sys.executable, str(self.target / ".devex/hooks/post-edit-ratchet.py")],
                             input=payload, capture_output=True, text=True)
        self.assertEqual(json.loads(out.stdout)["decision"], "block")


class PackagingTests(unittest.TestCase):
    def test_mirrors_match_canonical_sources(self) -> None:
        result = subprocess.run([sys.executable, str(ROOT / "scripts/sync_design_harness.py"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0,
                         result.stderr + "\nrun: python3 scripts/sync_design_harness.py")

    def test_profile_template_has_design_baseline_row(self) -> None:
        text = (SKILL / "assets/PROJECT-OPERATING-PROFILE.template.md").read_text()
        self.assertIn("| Design baseline", text)
        self.assertIn("`design-steward`", text)

    def test_design_steward_is_routed_and_listed(self) -> None:
        self.assertIn("`design-steward`", (ROOT / "skills/delivery-orchestrator/SKILL.md").read_text())
        self.assertIn("./design-steward/SKILL.md", (ROOT / "skills/README.md").read_text())

    def test_skill_is_project_neutral(self) -> None:
        text = "".join(p.read_text() for p in (ROOT / "skills/design-steward").rglob("*.md"))
        for forbidden in ("DevDash", "ADR-0043", "mac-control", "DesignTokens.swift"):
            self.assertNotIn(forbidden, text)

    def test_hooks_are_not_registered_globally(self) -> None:
        for manifest in ("hooks.json", "hooks/hooks.json"):
            text = (ROOT / manifest).read_text()
            for name in ("records-guard", "ui-context", "post-edit-ratchet"):
                self.assertNotIn(name, text)


if __name__ == "__main__":
    unittest.main()
