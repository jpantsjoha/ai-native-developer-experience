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
            "skills": "./skills/",
            "sessionStart": {"skill": "using-the-harness"},
        },
    )

    skill = root / "skills" / "using-the-harness"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: using-the-harness\ndescription: x\n---\n", encoding="utf-8"
    )
    (root / ".agents").mkdir(parents=True, exist_ok=True)
    os.symlink("../skills", root / ".agents" / "skills")

    (root / "GEMINI.md").write_text("# adapter\n", encoding="utf-8")
    hook = root / "hooks" / "session-start"
    hook.parent.mkdir(parents=True)
    hook.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    hook.chmod(0o755)
    hooks_manifest = {
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
    }
    # Claude Code reads hooks/hooks.json; Antigravity (agy) reads hooks.json at the
    # package root. Both must exist and stay identical.
    write_json(root / "hooks" / "hooks.json", hooks_manifest)
    write_json(root / "hooks.json", hooks_manifest)


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
                for path in (REPO_ROOT / "skills").iterdir()
                if path.is_dir() and (path / "SKILL.md").is_file()
            ]
        )
        expected = str(skill_count)
        claims = {
            "skills/README.md": f"## The {expected} Skills",
            "README.md": f"full harness is live: {expected} skills",
            "docs/install/claude.md": f"the {expected} `skills/` capabilities",
            "docs/install/codex.md": f"the {expected} skills should be named",
            "docs/install/kimi.md": f"to see the {expected} skills",
            "docs/install/antigravity.md": f"the {expected} `skills/` capabilities",
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
        (self.root / ".agents" / "skills").unlink()
        result = run_validator(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("discovery alias", result.stderr)

    def test_missing_root_hooks_manifest_fails(self) -> None:
        (self.root / "hooks.json").unlink()
        result = run_validator(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing manifest: hooks.json", result.stderr)

    def test_hook_manifest_drift_fails(self) -> None:
        path = self.root / "hooks.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["hooks"]["SessionStart"][0]["matcher"] = "startup|clear"
        write_json(path, payload)
        result = run_validator(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("hook manifest drift", result.stderr)

    def test_frontmatter_dirname_mismatch_fails(self) -> None:
        skill = self.root / "skills" / "using-the-harness" / "SKILL.md"
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
        skill = self.root / "skills" / "using-the-harness" / "SKILL.md"
        skill.write_text("---\nname: using-the-harness\n---\n", encoding="utf-8")
        self.assert_spec_failure("missing a non-empty description")

    def test_skill_overlong_description_fails(self) -> None:
        skill = self.root / "skills" / "using-the-harness" / "SKILL.md"
        skill.write_text(
            f"---\nname: using-the-harness\ndescription: {'x' * 1025}\n---\n",
            encoding="utf-8",
        )
        self.assert_spec_failure("limit is 1024")

    def test_skill_without_frontmatter_fails(self) -> None:
        skill = self.root / "skills" / "using-the-harness" / "SKILL.md"
        skill.write_text("# no frontmatter here\n", encoding="utf-8")
        self.assert_spec_failure("no closed YAML frontmatter")

    def test_alias_symlink_escaping_root_fails(self) -> None:
        outside = Path(self.temporary.name).parent / "outside-skills"
        outside.mkdir(exist_ok=True)
        (self.root / ".agents" / "skills").unlink()
        os.symlink(str(outside), self.root / ".agents" / "skills")
        try:
            self.assert_spec_failure("escapes the plugin root")
        finally:
            outside.rmdir()

    def test_absolute_alias_symlink_fails(self) -> None:
        (self.root / ".agents" / "skills").unlink()
        os.symlink(str(self.root / "skills"), self.root / ".agents" / "skills")
        self.assert_spec_failure("must be relative")

    def test_fixed_location_as_symlink_fails(self) -> None:
        """Codex's installer drops a symlink at skills/, so it must be a real directory."""
        real = self.root / ".agents" / "skills"
        real.unlink()
        (self.root / "skills").rename(real)
        os.symlink(".agents/skills", self.root / "skills")
        self.assert_spec_failure("must be a real directory")

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

    def mcp(self, server: dict) -> None:
        write_json(
            self.root / "mcp.json",
            {"$schema": MCP_SCHEMA, "mcpServers": {"probe": server}},
        )

    # --- Findings from the independent cross-model review of v0.1.7..v0.2.2 -----------
    # Each of these passed the gate before the review. A check without a failing fixture
    # is not an implemented check.

    def test_mcp_null_command_fails(self) -> None:
        self.mcp({"type": "stdio", "command": None})
        self.assert_spec_failure("command must be a non-empty string")

    def test_mcp_null_url_fails(self) -> None:
        self.mcp({"type": "streamable-http", "url": None})
        self.assert_spec_failure("url must be a non-empty string")

    def test_mcp_non_string_args_fails(self) -> None:
        self.mcp({"type": "stdio", "command": "uvx", "args": ["ok", 7]})
        self.assert_spec_failure("args must be an array of strings")

    def test_mcp_non_string_env_value_fails(self) -> None:
        self.mcp({"type": "stdio", "command": "uvx", "env": {"A": 1}})
        self.assert_spec_failure("env must be an object of string values")

    def test_mcp_non_string_headers_fails(self) -> None:
        self.mcp({"type": "streamable-http", "url": "https://e.invalid", "headers": {"A": 1}})
        self.assert_spec_failure("headers must be an object of string values")

    def test_mcp_relative_cwd_traversal_fails(self) -> None:
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "./../outside"})
        self.assert_spec_failure("must not traverse outside its root")

    def test_mcp_plugin_root_cwd_traversal_fails(self) -> None:
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_ROOT}/../outside"})
        self.assert_spec_failure("must not traverse outside its root")

    def test_mcp_nested_cwd_traversal_fails(self) -> None:
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_DATA}/a/../../out"})
        self.assert_spec_failure("must not traverse outside its root")

    def test_mcp_cwd_descending_then_returning_passes(self) -> None:
        """`a/../b` never leaves the root, so it must not be rejected."""
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_ROOT}/a/../b"})
        result = run_validator(self.root, "--spec-only")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_mcp_cwd_escaping_via_in_root_symlink_fails(self) -> None:
        """A lexical `..` check cannot see an in-root symlink pointing outside."""
        outside = Path(self.temporary.name).parent / "mcp-outside"
        outside.mkdir(exist_ok=True)
        os.symlink(str(outside), self.root / "escape")
        try:
            self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_ROOT}/escape/work"})
            self.assert_spec_failure("resolves outside the plugin root")
        finally:
            outside.rmdir()

    def test_mcp_cwd_via_windows_relative_symlink_fails(self) -> None:
        """POSIX reads "..\\outside" as one filename; Windows climbs out of the root."""
        os.symlink("..\\outside", self.root / "winrel")
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_ROOT}/winrel/work"})
        self.assert_spec_failure("resolves outside the plugin root")

    def test_mcp_cwd_via_windows_netzero_symlink_passes(self) -> None:
        """"sub\\..\\workdir" never leaves the root, so it must not be rejected."""
        (self.root / "workdir").mkdir()
        (self.root / "sub").mkdir()
        os.symlink("sub\\..\\workdir", self.root / "netzero")
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_ROOT}/netzero"})
        result = run_validator(self.root, "--spec-only")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_mcp_plugin_data_traversal_fails(self) -> None:
        """PLUGIN_DATA is client-managed, so a net-zero `..` cannot be proven contained."""
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_DATA}/link/../work"})
        self.assert_spec_failure("resolves outside the plugin root")

    def test_mcp_plugin_data_plain_path_passes(self) -> None:
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_DATA}/work"})
        result = run_validator(self.root, "--spec-only")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_mcp_cwd_with_doubled_separator_passes(self) -> None:
        """`.//skills` is in-root; a stripped prefix must not leave an absolute path."""
        (self.root / "workdir").mkdir()
        for cwd in (".//workdir", "${PLUGIN_ROOT}//workdir"):
            with self.subTest(cwd=cwd):
                self.mcp({"type": "stdio", "command": "uvx", "cwd": cwd})
                result = run_validator(self.root, "--spec-only")
                self.assertEqual(result.returncode, 0, f"{cwd} wrongly rejected")

    def test_mcp_cwd_via_windows_absolute_symlink_fails(self) -> None:
        """A POSIX host reads "C:\\out" as relative; a Windows client reads it as absolute."""
        for name, target in (("win", "C:\\outside"), ("unc", "\\\\server\\share")):
            with self.subTest(target=target):
                os.symlink(target, self.root / name)
                self.mcp({"type": "stdio", "command": "uvx",
                          "cwd": f"${{PLUGIN_ROOT}}/{name}/work"})
                self.assert_spec_failure("resolves outside the plugin root")

    def test_mcp_cwd_via_in_root_relative_symlink_passes(self) -> None:
        """An ordinary relative symlink to a sibling directory stays contained."""
        (self.root / "workdir").mkdir()
        os.symlink("workdir", self.root / "good")
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_ROOT}/good"})
        result = run_validator(self.root, "--spec-only")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_mcp_cwd_via_broken_symlink_fails(self) -> None:
        """A broken symlink reports exists()==False, so containment must use lexists."""
        os.symlink("/outside-not-yet-created", self.root / "escape")
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_ROOT}/escape/work"})
        self.assert_spec_failure("resolves outside the plugin root")

    def test_mcp_cwd_to_not_yet_created_in_root_path_passes(self) -> None:
        """Containment checks escape, not presence: a plain missing path is fine."""
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_ROOT}/newdir/sub"})
        result = run_validator(self.root, "--spec-only")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_mcp_cwd_into_real_in_root_directory_passes(self) -> None:
        """Containment must not reject an ordinary directory inside the package."""
        (self.root / "workdir").mkdir()
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_ROOT}/workdir"})
        result = run_validator(self.root, "--spec-only")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_mcp_explicit_null_optional_fields_fail(self) -> None:
        """An explicit null is a present field of the wrong type, not an absent field."""
        for field, server in {
            "args": {"type": "stdio", "command": "uvx", "args": None},
            "env": {"type": "stdio", "command": "uvx", "env": None},
            "cwd": {"type": "stdio", "command": "uvx", "cwd": None},
            "headers": {
                "type": "streamable-http",
                "url": "https://example.invalid",
                "headers": None,
            },
        }.items():
            with self.subTest(field=field):
                self.mcp(server)
                result = run_validator(self.root, "--spec-only")
                self.assertEqual(result.returncode, 1, f"{field}=null was accepted")

    def test_mcp_windows_separator_traversal_fails(self) -> None:
        """A Windows client resolves `\\` as a separator, so `./..\\outside` escapes there."""
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "./..\\outside"})
        self.assert_spec_failure("must not traverse outside its root")

    def test_mcp_windows_separator_rooted_traversal_fails(self) -> None:
        self.mcp({"type": "stdio", "command": "uvx", "cwd": "${PLUGIN_ROOT}/..\\outside"})
        self.assert_spec_failure("must not traverse outside its root")

    def test_unicode_digit_version_fails(self) -> None:
        """Python's `\\d` matches Unicode digits; the SemVer rule must be ASCII-only."""
        self.mutate_manifest(version="1.2٢.3")
        self.assert_spec_failure("version must be SemVer")

    def test_trailing_newline_version_fails(self) -> None:
        """`$` permits a trailing newline, so the rule uses fullmatch()."""
        self.mutate_manifest(version="1.2.3\n")
        self.assert_spec_failure("version must be SemVer")

    def test_non_semver_version_fails(self) -> None:
        self.mutate_manifest(version="banana")
        self.assert_spec_failure("version must be SemVer")

    def test_missing_version_fails(self) -> None:
        self.mutate_manifest(version=None)
        self.assert_spec_failure("version must be SemVer")

    def test_prerelease_semver_passes(self) -> None:
        self.mutate_manifest(version="1.2.3-rc.1+build.5")
        result = run_validator(self.root, "--spec-only")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_root_manifest_version_drift_fails_full_gate(self) -> None:
        self.mutate_manifest(version="9.9.9")
        result = run_validator(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("name/version drift", result.stderr)


if __name__ == "__main__":
    unittest.main()
