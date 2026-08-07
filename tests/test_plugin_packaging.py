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
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"


def run_validator(root: Path, *flags: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--root", str(root), *flags],
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
    write_json(
        root / "plugin.json",
        {
            "$schema": PLUGIN_SCHEMA,
            **manifest,
            "description": "fixture",
            "author": {"name": "Fixture Author", "url": "https://example.invalid"},
            "license": "Apache-2.0",
            "keywords": ["fixture"],
            "extensions": {
                "com.anthropic.claude-code": {
                    "manifest": "./.claude-plugin/plugin.json",
                    "hooks": "./hooks/hooks.json",
                }
            },
        },
    )
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


class SpecConformanceTests(unittest.TestCase):
    """Negative fixtures for the Agent Plugins 1.0.0 / Agent Skills conformance gate.

    A validator that only ever passes is decoration. Every check the gate claims to make
    gets a fixture here that must fail it.
    """

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        build_fixture(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def mutate_manifest(self, **changes: object) -> None:
        """Apply changes to the fixture's root plugin.json; a None value deletes the key."""
        path = self.root / "plugin.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        for key, value in changes.items():
            if value is None:
                payload.pop(key, None)
            else:
                payload[key] = value
        write_json(path, payload)

    def assert_spec_failure(self, fragment: str) -> None:
        result = run_validator(self.root, "--spec-only")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(fragment, result.stderr)

    def test_conformant_fixture_passes_spec_gate(self) -> None:
        result = run_validator(self.root, "--spec-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Agent Plugins 1.0.0 conformance", result.stdout)

    def test_repository_passes_spec_gate(self) -> None:
        result = run_validator(REPO_ROOT, "--spec-only")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_root_manifest_fails(self) -> None:
        (self.root / "plugin.json").unlink()
        self.assert_spec_failure("missing manifest: plugin.json")

    def test_absent_schema_fails(self) -> None:
        self.mutate_manifest(**{"$schema": None})
        self.assert_spec_failure("$schema must be")

    def test_wrong_schema_version_fails(self) -> None:
        self.mutate_manifest(
            **{"$schema": "https://agent-plugins.org/schemas/0.9.0/plugin.schema.json"}
        )
        self.assert_spec_failure("$schema must be")

    def test_uppercase_name_fails(self) -> None:
        self.mutate_manifest(name="Join-The-Team")
        self.assert_spec_failure("violates the spec name pattern")

    def test_leading_hyphen_name_fails(self) -> None:
        self.mutate_manifest(name="-join-the-team")
        self.assert_spec_failure("violates the spec name pattern")

    def test_consecutive_hyphen_name_fails(self) -> None:
        self.mutate_manifest(name="join--the-team")
        self.assert_spec_failure("violates the spec name pattern")

    def test_unknown_top_level_field_fails(self) -> None:
        self.mutate_manifest(skills="./skills/")
        self.assert_spec_failure("unknown top-level fields")

    def test_author_with_unknown_field_fails(self) -> None:
        self.mutate_manifest(author={"name": "x", "github": "y"})
        self.assert_spec_failure("author has unknown fields")

    def test_non_reverse_domain_extension_key_fails(self) -> None:
        self.mutate_manifest(extensions={"claudecode": {"manifest": "./plugin.json"}})
        self.assert_spec_failure("is not a reverse-domain namespace")

    def test_extension_pointing_at_missing_path_fails(self) -> None:
        self.mutate_manifest(
            extensions={"com.anthropic.claude-code": {"commands": "./commands/"}}
        )
        self.assert_spec_failure("points at missing path")

    def test_skill_missing_description_fails(self) -> None:
        skill = self.root / ".agents" / "skills" / "using-the-harness" / "SKILL.md"
        skill.write_text("---\nname: using-the-harness\n---\n", encoding="utf-8")
        self.assert_spec_failure("missing a non-empty description")

    def test_skill_overlong_description_fails(self) -> None:
        skill = self.root / ".agents" / "skills" / "using-the-harness" / "SKILL.md"
        skill.write_text(
            f"---\nname: using-the-harness\ndescription: {'x' * 1025}\n---\n",
            encoding="utf-8",
        )
        self.assert_spec_failure("limit is 1024")

    def test_skill_without_frontmatter_fails(self) -> None:
        skill = self.root / ".agents" / "skills" / "using-the-harness" / "SKILL.md"
        skill.write_text("# no frontmatter here\n", encoding="utf-8")
        self.assert_spec_failure("no closed YAML frontmatter")

    def test_skills_symlink_escaping_root_fails(self) -> None:
        outside = Path(self.temporary.name).parent / "outside-skills"
        outside.mkdir(exist_ok=True)
        (self.root / "skills").unlink()
        os.symlink(str(outside), self.root / "skills")
        try:
            self.assert_spec_failure("escapes the plugin root")
        finally:
            outside.rmdir()

    def test_absolute_skills_symlink_fails(self) -> None:
        (self.root / "skills").unlink()
        os.symlink(str(self.root / ".agents" / "skills"), self.root / "skills")
        self.assert_spec_failure("must be relative")

    def test_mcp_server_without_type_fails(self) -> None:
        write_json(
            self.root / "mcp.json",
            {"$schema": MCP_SCHEMA, "mcpServers": {"docs": {"command": "uvx"}}},
        )
        self.assert_spec_failure("expected one of")

    def test_mcp_env_declaring_reserved_variable_fails(self) -> None:
        write_json(
            self.root / "mcp.json",
            {
                "$schema": MCP_SCHEMA,
                "mcpServers": {
                    "docs": {
                        "type": "stdio",
                        "command": "uvx",
                        "env": {"PLUGIN_ROOT": "/tmp"},
                    }
                },
            },
        )
        self.assert_spec_failure("reserved variables")

    def test_mcp_plaintext_remote_url_fails(self) -> None:
        write_json(
            self.root / "mcp.json",
            {
                "$schema": MCP_SCHEMA,
                "mcpServers": {
                    "remote": {"type": "streamable-http", "url": "http://example.com/mcp"}
                },
            },
        )
        self.assert_spec_failure("must use https")

    def test_conformant_mcp_config_passes(self) -> None:
        write_json(
            self.root / "mcp.json",
            {
                "$schema": MCP_SCHEMA,
                "mcpServers": {
                    "local": {
                        "type": "stdio",
                        "command": "uvx",
                        "args": ["server@latest", "--root", "${PLUGIN_ROOT}"],
                        "cwd": "${PLUGIN_DATA}/work",
                    },
                    "remote": {"type": "streamable-http", "url": "https://example.com/mcp"},
                },
            },
        )
        result = run_validator(self.root, "--spec-only")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_root_manifest_version_drift_fails_full_gate(self) -> None:
        self.mutate_manifest(version="9.9.9")
        result = run_validator(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("name/version drift", result.stderr)


if __name__ == "__main__":
    unittest.main()
