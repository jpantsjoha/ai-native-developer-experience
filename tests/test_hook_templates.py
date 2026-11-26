"""Payload tests for the opt-in hook templates: allow, deny and malformed cases each."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "hooks" / "templates"


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


def fire(script: Path, payload, *args: str, env: dict | None = None,
         cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run([sys.executable, str(script), *args], input=stdin, text=True,
                          capture_output=True, cwd=cwd, env={**os.environ, **(env or {})})


def decision(result: subprocess.CompletedProcess[str]) -> str | None:
    if not result.stdout.strip():
        return None
    out = json.loads(result.stdout)
    return out.get("hookSpecificOutput", {}).get("permissionDecision") or out.get("decision")


class RecordsGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q", "-b", "feat/x")
        git(self.repo, "config", "user.email", "t@example.test")
        git(self.repo, "config", "user.name", "t")
        (self.repo / "docs").mkdir()
        (self.repo / "docs/STATUS.md").write_text("s\n")
        (self.repo / "CHANGELOG.md").write_text("c\n")
        (self.repo / "app.py").write_text("x\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "init")
        self.script = TEMPLATES / "records-guard.py"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def edit(self, rel: str, tool: str = "Edit"):
        return {"tool_name": tool, "cwd": str(self.repo),
                "tool_input": {"file_path": str(self.repo / rel)}}

    def test_denies_protected_edit_off_a_records_branch(self) -> None:
        for tool in ("Edit", "Write", "MultiEdit"):
            with self.subTest(tool=tool):
                result = fire(self.script, self.edit("docs/STATUS.md", tool))
                self.assertEqual(result.returncode, 0)
                self.assertEqual(decision(result), "deny")
                self.assertIn("records branch", result.stdout)

    def test_allows_protected_edit_on_a_records_branch(self) -> None:
        git(self.repo, "checkout", "-q", "-b", "records/batch-1")
        self.assertIsNone(decision(fire(self.script, self.edit("CHANGELOG.md"))))

    def test_allows_unprotected_edit(self) -> None:
        self.assertIsNone(decision(fire(self.script, self.edit("app.py"))))

    def test_bash_write_denied_and_read_allowed(self) -> None:
        def bash(cmd):
            return {"tool_name": "Bash", "cwd": str(self.repo), "tool_input": {"command": cmd}}
        self.assertEqual(decision(fire(self.script, bash("echo x >> CHANGELOG.md"))), "deny")
        self.assertEqual(decision(fire(self.script, bash("sed -i '' s/a/b/ docs/STATUS.md"))), "deny")
        self.assertIsNone(decision(fire(self.script, bash("cat CHANGELOG.md"))))

    def test_null_and_stderr_redirections_are_not_writes(self) -> None:
        def bash(cmd):
            return {"tool_name": "Bash", "cwd": str(self.repo), "tool_input": {"command": cmd}}
        for cmd in ("cat docs/STATUS.md 2>&1", "cat CHANGELOG.md >/dev/null",
                    "cat CHANGELOG.md 2>/dev/null", "grep x CHANGELOG.md &>/dev/null",
                    "cat CHANGELOG.md > /dev/null 2>&1", "head CHANGELOG.md 1>&2"):
            with self.subTest(cmd=cmd):
                self.assertIsNone(decision(fire(self.script, bash(cmd))))
        for cmd in ("echo x > CHANGELOG.md 2>&1", "echo x >> CHANGELOG.md 2>/dev/null"):
            with self.subTest(cmd=cmd):
                self.assertEqual(decision(fire(self.script, bash(cmd))), "deny")

    def test_unborn_branch_is_still_judged(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            git(repo, "init", "-q", "-b", "feat/new")
            payload = {"tool_name": "Edit", "cwd": str(repo),
                       "tool_input": {"file_path": str(repo / "CHANGELOG.md")}}
            self.assertEqual(decision(fire(self.script, payload)), "deny")
            git(repo, "checkout", "-q", "-b", "records/first")
            self.assertIsNone(decision(fire(self.script, payload)))

    def test_malformed_and_odd_payloads_allow(self) -> None:
        for bad in ("{not json", "", "[]", '{"tool_name": "Edit"}',
                    '{"tool_name": "Edit", "tool_input": "x"}'):
            with self.subTest(bad=bad):
                result = fire(self.script, bad)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stdout.strip(), "")

    def test_outside_a_git_repo_allows(self) -> None:
        with tempfile.TemporaryDirectory() as bare:
            payload = {"tool_name": "Edit", "cwd": bare,
                       "tool_input": {"file_path": str(Path(bare) / "CHANGELOG.md")}}
            result = fire(self.script, payload)
            self.assertIsNone(decision(result))  # cannot see a branch: fail open

    def test_custom_config_changes_protected_set(self) -> None:
        (self.repo / ".devex").mkdir()
        (self.repo / ".devex/records-guard.json").write_text(
            json.dumps({"protected": ["app.py"], "branch_patterns": ["rec/*"]}))
        self.assertEqual(decision(fire(self.script, self.edit("app.py"))), "deny")
        self.assertIsNone(decision(fire(self.script, self.edit("CHANGELOG.md"))))

    def test_staged_mode_blocks_then_passes_on_records_branch(self) -> None:
        (self.repo / "CHANGELOG.md").write_text("changed\n")
        git(self.repo, "add", "CHANGELOG.md")
        blocked = fire(self.script, "", "--staged", cwd=self.repo)
        self.assertEqual(blocked.returncode, 1)
        self.assertIn("CHANGELOG.md", blocked.stderr)
        git(self.repo, "checkout", "-q", "-b", "records/b2")
        self.assertEqual(fire(self.script, "", "--staged", cwd=self.repo).returncode, 0)

    def test_staged_mode_ignores_unprotected(self) -> None:
        (self.repo / "app.py").write_text("y\n")
        git(self.repo, "add", "app.py")
        self.assertEqual(fire(self.script, "", "--staged", cwd=self.repo).returncode, 0)


class UiContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name)
        self.script = TEMPLATES / "ui-context.py"
        self.env = {"DEVEX_STATE_DIR": str(self.state)}

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def payload(self, rel: str, session: str = "s1"):
        return {"tool_name": "Edit", "session_id": session, "cwd": "/proj",
                "tool_input": {"file_path": f"/proj/{rel}"}}

    def test_reminds_once_per_session_on_ui_path(self) -> None:
        first = fire(self.script, self.payload("Views/Row.swift"), env=self.env)
        self.assertIn("design-steward", first.stdout)
        self.assertNotIn('"deny"', first.stdout)
        second = fire(self.script, self.payload("Views/Other.swift"), env=self.env)
        self.assertEqual(second.stdout.strip(), "")
        other_session = fire(self.script, self.payload("a.css", "s2"), env=self.env)
        self.assertIn("design-steward", other_session.stdout)

    def test_silent_on_non_ui_path_and_other_tools(self) -> None:
        self.assertEqual(fire(self.script, self.payload("server/db.py"), env=self.env).stdout.strip(), "")
        bash = {"tool_name": "Bash", "session_id": "s3", "tool_input": {"command": "ls"}}
        self.assertEqual(fire(self.script, bash, env=self.env).stdout.strip(), "")

    def test_malformed_allows(self) -> None:
        for bad in ("{oops", "", "null"):
            result = fire(self.script, bad, env=self.env)
            self.assertEqual((result.returncode, result.stdout.strip()), (0, ""))


class PostEditRatchetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self.tmp.name) / "proj"
        (self.proj / ".devex").mkdir(parents=True)
        shutil.copy(TEMPLATES / "ratchet.config.example.json", self.proj / ".devex/ratchet.config.json")
        self.hooks = Path(self.tmp.name) / "hooks"
        self.hooks.mkdir()
        shutil.copy(TEMPLATES / "post-edit-ratchet.py", self.hooks)
        shutil.copy(ROOT / "scripts/literal_ratchet.py", self.hooks / "literal-ratchet.py")
        self.css = self.proj / "a.css"
        self.css.write_text(".a { color: #ff0000; }\n")
        engine = self.hooks / "literal-ratchet.py"
        subprocess.run([sys.executable, str(engine), "--root", str(self.proj), "--update-baseline"],
                       check=True, capture_output=True)
        self.script = self.hooks / "post-edit-ratchet.py"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def payload(self, path: Path):
        return {"tool_name": "Edit", "cwd": str(self.proj), "tool_input": {"file_path": str(path)}}

    def test_blocks_a_regression_with_file_and_line(self) -> None:
        self.css.write_text(".a { color: #ff0000; }\n.b { color: #00ff00; }\n")
        result = fire(self.script, self.payload(self.css))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(decision(result), "block")
        self.assertIn("a.css:", json.loads(result.stdout)["reason"])

    def test_clean_edit_allows(self) -> None:
        self.assertEqual(fire(self.script, self.payload(self.css)).stdout.strip(), "")

    def test_no_config_or_malformed_allows(self) -> None:
        (self.proj / ".devex/ratchet.config.json").unlink()
        self.css.write_text("#111111 #222222")
        self.assertEqual(fire(self.script, self.payload(self.css)).stdout.strip(), "")
        for bad in ("{x", "", "[]"):
            result = fire(self.script, bad)
            self.assertEqual((result.returncode, result.stdout.strip()), (0, ""))


class NoAskTests(unittest.TestCase):
    def test_no_template_can_return_ask(self) -> None:
        for path in TEMPLATES.glob("*.py"):
            with self.subTest(template=path.name):
                text = path.read_text()
                self.assertNotIn('"ask"', text)
                self.assertNotIn("'ask'", text)


if __name__ == "__main__":
    unittest.main()
