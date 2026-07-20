"""Regression tests for the plugin-packaging drift validator."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_plugin.py"

NAME = "join-the-team"
VERSION = "0.1.0"


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_fixture(root: Path) -> None:
    """Create a minimal but valid plugin packaging layout in a temp dir."""

    manifest = {"name": NAME, "version": VERSION}
    write_json(root / ".claude-plugin" / "plugin.json", manifest)
    write_json(
        root / ".claude-plugin" / "marketplace.json",
        {"name": "m", "plugins": [dict(manifest)]},
    )
    write_json(root / "gemini-extension.json", {**manifest, "contextFileName": "GEMINI.md"})
    write_json(
        root / ".kimi-plugin" / "plugin.json",
        {
            **manifest,
            "skills": "./.agents/skills/",
            "sessionStart": {"skill": "using-the-harness"},
        },
    )

    skill = root / ".agents" / "skills" / "using-the-harness"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: using-the-harness\ndescription: x\n---\n", encoding="utf-8"
    )
    os.symlink(".agents/skills", root / "skills")

    (root / "GEMINI.md").write_text("# adapter\n", encoding="utf-8")
    hook = root / "hooks" / "session-start"
    hook.parent.mkdir(parents=True)
    hook.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    hook.chmod(0o755)
    write_json(
        root / "hooks" / "hooks.json",
        {
            "hooks": {
                "SessionStart": [
                    {
                        "matcher": "startup",
                        "hooks": [
                            {
                                "type": "command",
                                "command": '"${CLAUDE_PLUGIN_ROOT}/hooks/session-start"',
                            }
                        ],
                    }
                ]
            }
        },
    )


class PluginPackagingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        build_fixture(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_repository_packaging_has_no_drift(self) -> None:
        result = run_validator(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS plugin-packaging validation", result.stdout)

    def test_documented_skill_counts_match_canonical_library(self) -> None:
        skill_count = len(
            [
                path
                for path in (REPO_ROOT / ".agents" / "skills").iterdir()
                if path.is_dir() and (path / "SKILL.md").is_file()
            ]
        )
        expected = str(skill_count)
        claims = {
            ".agents/skills/README.md": f"## The {expected} Skills",
            "README.md": f"full harness is live: {expected} skills",
            "docs/install/claude.md": f"the {expected} `.agents/skills/` capabilities",
            "docs/install/codex.md": f"the {expected} skills should be named",
            "docs/install/kimi.md": f"to see the {expected} skills",
            "docs/install/antigravity.md": f"the {expected} `.agents/skills/` capabilities",
        }
        for relative_path, claim in claims.items():
            with self.subTest(path=relative_path):
                text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(claim, text)

    def test_valid_fixture_passes(self) -> None:
        result = run_validator(self.root)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_version_drift_between_manifests_fails(self) -> None:
        path = self.root / ".claude-plugin" / "plugin.json"
        path.write_text(
            json.dumps({"name": NAME, "version": "9.9.9"}) + "\n", encoding="utf-8"
        )
        result = run_validator(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("name/version drift", result.stderr)

    def test_dead_session_start_skill_fails(self) -> None:
        path = self.root / ".kimi-plugin" / "plugin.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["sessionStart"]["skill"] = "does-not-exist"
        path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        result = run_validator(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("sessionStart skill not found", result.stderr)

    def test_broken_skills_alias_fails(self) -> None:
        (self.root / "skills").unlink()
        result = run_validator(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("discovery alias", result.stderr)

    def test_frontmatter_dirname_mismatch_fails(self) -> None:
        skill = self.root / ".agents" / "skills" / "using-the-harness" / "SKILL.md"
        skill.write_text("---\nname: renamed\ndescription: x\n---\n", encoding="utf-8")
        result = run_validator(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("frontmatter name", result.stderr)


if __name__ == "__main__":
    unittest.main()
