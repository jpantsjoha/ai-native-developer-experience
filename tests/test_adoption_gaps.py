"""Adoption gaps (#32): adopt-only bootstrap, settings/pre-commit/make writers, path-owner hooks,
resolved Bash writes, --config, config-guard, raise note, registration audit, gate log paths.

Every git-running test uses a temporary GIT_CONFIG_GLOBAL and HOME; nothing is written under
~/.config or a real hooks directory.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "hooks" / "templates"
SCRIPTS = ROOT / "scripts"
BOOTSTRAP = ROOT / "skills/operating-model-bootstrap/scripts/bootstrap_operating_model.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GitCase(unittest.TestCase):
    """Base: isolated HOME and global git config for every subprocess."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(os.path.realpath(self.tmp.name))
        self.global_config = self.base / "gitconfig-global"
        self.global_config.write_text("[user]\n\temail = t@example.test\n\tname = t\n")
        self.env = {**os.environ, "GIT_CONFIG_GLOBAL": str(self.global_config),
                    "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(self.base / "home")}
        (self.base / "home").mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def git(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True,
                              text=True, env=self.env)

    def repo(self, name: str, branch: str, files: dict[str, str] | None = None) -> Path:
        path = self.base / name
        path.mkdir()
        self.git(path, "init", "-q", "-b", branch)
        for rel, text in (files or {"README.md": "r\n"}).items():
            (path / rel).parent.mkdir(parents=True, exist_ok=True)
            (path / rel).write_text(text)
        self.git(path, "add", "-A")
        self.git(path, "commit", "-q", "-m", "init")
        return path

    def fire(self, script: Path, payload, *args: str, cwd: Path | None = None):
        stdin = payload if isinstance(payload, str) else json.dumps(payload)
        return subprocess.run([sys.executable, str(script), *args], input=stdin, text=True,
                              capture_output=True, cwd=cwd, env=self.env)

    @staticmethod
    def verdict(result: subprocess.CompletedProcess[str]) -> str | None:
        if not result.stdout.strip():
            return None
        out = json.loads(result.stdout)
        return out.get("hookSpecificOutput", {}).get("permissionDecision") or out.get("decision")


class AdoptOnlyTests(GitCase):
    def seeded(self) -> Path:
        target = self.base / "proj"
        target.mkdir()
        for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
            (target / name).write_text(f"mine {name}\n")
        (target / "docs" / "operating-model").mkdir(parents=True)
        (target / "docs/operating-model/OPERATING-MANUAL.md").write_text("mine\n")
        return target

    def run_bootstrap(self, target: Path, *args: str):
        return subprocess.run([sys.executable, str(BOOTSTRAP), *args, str(target)],
                              capture_output=True, text=True, env=self.env)

    def test_plain_bootstrap_refuses_an_existing_seed(self) -> None:
        target = self.seeded()
        result = self.run_bootstrap(target, "--adopt", "records-guard")
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to overwrite", result.stderr)

    def test_adopt_only_is_a_dry_run_until_apply(self) -> None:
        target = self.seeded()
        before = sorted(p.relative_to(target).as_posix() for p in target.rglob("*"))
        result = self.run_bootstrap(target, "--adopt-only", "--adopt", "records-guard")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("would create: .devex/hooks/records-guard.py", result.stdout)
        self.assertIn("rerun with --apply", result.stdout)
        self.assertEqual(before, sorted(p.relative_to(target).as_posix() for p in target.rglob("*")))

    def test_apply_writes_only_the_harness_and_keeps_the_seed(self) -> None:
        target = self.seeded()
        result = self.run_bootstrap(target, "--adopt-only", "--apply", "--adopt", "records-guard")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / ".devex/hooks/records-guard.py").is_file())
        self.assertTrue((target / ".devex/hooks/bashwrites.py").is_file())
        self.assertEqual((target / "CLAUDE.md").read_text(), "mine CLAUDE.md\n")
        self.assertFalse((target / "docs/VISION.md").exists())
        self.assertFalse((target / "CHANGELOG.md").exists())

    def test_apply_never_overwrites_a_changed_file(self) -> None:
        target = self.seeded()
        guard = target / ".devex/hooks/records-guard.py"
        guard.parent.mkdir(parents=True)
        guard.write_text("# mine\n")
        result = self.run_bootstrap(target, "--adopt-only", "--apply", "--adopt", "records-guard")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(guard.read_text(), "# mine\n")
        self.assertIn("preserved existing: .devex/hooks/records-guard.py", result.stdout)

    def test_flag_misuse_is_an_error(self) -> None:
        target = self.seeded()
        self.assertEqual(self.run_bootstrap(target, "--apply", "--adopt", "all").returncode, 2)
        self.assertEqual(self.run_bootstrap(target, "--adopt-only").returncode, 2)
        self.assertEqual(self.run_bootstrap(target, "--adopt-only", "--apply", "--dry-run",
                                            "--adopt", "all").returncode, 2)

    def test_config_guard_brings_the_engine_it_loads(self) -> None:
        target = self.seeded()
        self.run_bootstrap(target, "--adopt-only", "--apply", "--adopt", "config-guard")
        self.assertTrue((target / ".devex/hooks/records-guard.py").is_file())
        self.assertTrue((target / ".devex/hooks/config-guard.py").is_file())


class WriterTests(GitCase):
    def target(self) -> Path:
        return self.repo("proj", "main")

    def run_bootstrap(self, target: Path, *args: str):
        return subprocess.run([sys.executable, str(BOOTSTRAP), "--adopt-only", *args, str(target)],
                              capture_output=True, text=True, env=self.env)

    def test_register_settings_dry_run_then_merge_without_touching_permissions(self) -> None:
        target = self.target()
        settings = target / ".claude" / "settings.json"
        settings.parent.mkdir()
        original = {"permissions": {"allow": ["Bash(ls)"], "defaultMode": "acceptEdits"},
                    "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [
                        {"type": "command", "command": "echo mine"}]}]}}
        settings.write_text(json.dumps(original))
        dry = self.run_bootstrap(target, "--adopt", "records-guard", "--register-settings")
        self.assertIn("would add hook", dry.stdout)
        self.assertEqual(json.loads(settings.read_text()), original)
        done = self.run_bootstrap(target, "--apply", "--adopt", "records-guard", "--register-settings")
        self.assertEqual(done.returncode, 0, done.stderr)
        merged = json.loads(settings.read_text())
        self.assertEqual(merged["permissions"], original["permissions"])
        commands = [h["command"] for g in merged["hooks"]["PreToolUse"] for h in g["hooks"]]
        self.assertIn("echo mine", commands)
        self.assertIn('python3 "$CLAUDE_PROJECT_DIR"/.devex/hooks/records-guard.py', commands)

    def test_register_settings_is_idempotent(self) -> None:
        target = self.target()
        args = ("--apply", "--adopt", "all", "--register-settings")
        self.run_bootstrap(target, *args)
        first = (target / ".claude/settings.json").read_text()
        again = self.run_bootstrap(target, *args)
        self.assertEqual((target / ".claude/settings.json").read_text(), first)
        self.assertIn("already registers", again.stdout)

    def test_register_settings_refuses_unreadable_json(self) -> None:
        target = self.target()
        settings = target / ".claude" / "settings.json"
        settings.parent.mkdir()
        settings.write_text("{ not json")
        result = self.run_bootstrap(target, "--apply", "--adopt", "records-guard", "--register-settings")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(settings.read_text(), "{ not json")

    def test_make_targets_write_once_and_append_one_include(self) -> None:
        target = self.target()
        (target / "Makefile").write_text("all:\n\t@true\n")
        dry = self.run_bootstrap(target, "--make-targets")
        self.assertIn("would append to Makefile: -include .devex/harness.mk", dry.stdout)
        self.assertFalse((target / ".devex/harness.mk").exists())
        self.run_bootstrap(target, "--apply", "--make-targets")
        self.run_bootstrap(target, "--apply", "--make-targets")
        text = (target / "Makefile").read_text()
        self.assertEqual(text.count("harness.mk"), 1)
        self.assertIn("harness-install:", (target / ".devex/harness.mk").read_text())

    def test_install_precommit_dry_run_writes_nothing_then_installs_in_the_clone(self) -> None:
        target = self.target()
        dry = self.run_bootstrap(target, "--install-precommit")
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertFalse((target / ".git/hooks/pre-commit").exists())
        done = self.run_bootstrap(target, "--apply", "--install-precommit")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue((target / ".git/hooks/pre-commit").is_file())


class PreCommitContractTests(GitCase):
    """The hooksPath chain contract (#32 item 5 and the #610 review note)."""

    def adopt(self, target: Path) -> None:
        subprocess.run([sys.executable, str(BOOTSTRAP), "--adopt-only", "--apply", "--adopt",
                        "records-guard", "--adopt", "pre-commit", str(target)],
                       check=True, capture_output=True, env=self.env)

    def test_global_hooks_path_is_never_written_and_the_clone_hook_is(self) -> None:
        global_hooks = self.base / "global-hooks"
        global_hooks.mkdir()
        self.global_config.write_text(self.global_config.read_text()
                                      + f"[core]\n\thooksPath = {global_hooks}\n")
        target = self.repo("proj", "main")
        self.adopt(target)
        result = subprocess.run([sys.executable, str(target / ".devex/hooks/install-precommit.py"),
                                 "--root", str(target)], capture_output=True, text=True, env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / ".git/hooks/pre-commit").is_file())
        self.assertEqual(list(global_hooks.iterdir()), [])
        self.assertIn("core.hooksPath is set", result.stderr)
        self.assertIn("git-common-dir", result.stderr)
        self.assertEqual(list((self.base / "home").iterdir()), [])

    def test_hook_resolves_at_commit_time_and_survives_removing_the_installing_worktree(self) -> None:
        target = self.repo("proj", "main", {"docs/STATUS.md": "s\n", "a.txt": "a\n"})
        self.adopt(target)
        self.git(target, "add", "-A")
        self.git(target, "commit", "-q", "-m", "harness")
        installer = self.base / "wt-install"
        self.git(target, "worktree", "add", "-q", "-b", "feat/install", str(installer))
        done = subprocess.run([sys.executable, str(installer / ".devex/hooks/install-precommit.py"),
                               "--root", str(installer)], capture_output=True, text=True, env=self.env)
        self.assertEqual(done.returncode, 0, done.stderr)
        hook_text = (target / ".git/hooks/pre-commit").read_text()
        self.assertNotIn(str(installer), hook_text)
        self.git(target, "worktree", "remove", "--force", str(installer))
        other = self.base / "wt-other"
        self.git(target, "worktree", "add", "-q", "-b", "feat/other", str(other))
        (other / "docs/STATUS.md").write_text("changed\n")
        self.git(other, "add", "docs/STATUS.md")
        blocked = subprocess.run(["git", "-C", str(other), "commit", "-q", "-m", "x"],
                                 capture_output=True, text=True, env=self.env)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("records-guard", blocked.stderr)

    def test_absent_script_prints_a_note_and_the_chained_hook_still_runs(self) -> None:
        target = self.repo("proj", "main")
        marker = self.base / "chained-ran"
        old = target / ".git/hooks/pre-commit"
        old.write_text(f"#!/bin/sh\ntouch {marker}\n")
        old.chmod(0o755)
        subprocess.run([sys.executable, str(ROOT / "hooks/templates/install-precommit.py"),
                        "--root", str(target)], check=True, capture_output=True, env=self.env)
        self.assertTrue((target / ".git/hooks/pre-commit.pre-harness").is_file())
        (target / "b.txt").write_text("b\n")
        self.git(target, "add", "b.txt")
        result = subprocess.run(["git", "-C", str(target), "commit", "-m", "b"],
                                capture_output=True, text=True, env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(marker.exists())
        self.assertIn("absent in this checkout", result.stderr)

    def test_installer_never_overwrites_a_foreign_hook_when_the_chain_name_is_taken(self) -> None:
        target = self.repo("proj", "main")
        hooks = target / ".git/hooks"
        (hooks / "pre-commit").write_text("#!/bin/sh\necho a\n")
        (hooks / "pre-commit.pre-harness").write_text("#!/bin/sh\necho b\n")
        result = subprocess.run([sys.executable, str(ROOT / "hooks/templates/install-precommit.py"),
                                 "--root", str(target)], capture_output=True, text=True, env=self.env)
        self.assertEqual(result.returncode, 2)
        self.assertEqual((hooks / "pre-commit").read_text(), "#!/bin/sh\necho a\n")


class PathOwnerTests(GitCase):
    def test_records_guard_judges_the_edited_paths_checkout_not_cwd(self) -> None:
        records = self.repo("records", "records/x", {"docs/STATUS.md": "s\n"})
        feature = self.repo("feature", "feat/x", {"docs/STATUS.md": "s\n"})
        guard = TEMPLATES / "records-guard.py"
        deny = self.fire(guard, {"tool_name": "Edit", "cwd": str(records),
                                 "tool_input": {"file_path": str(feature / "docs/STATUS.md")}})
        self.assertEqual(self.verdict(deny), "deny")
        allow = self.fire(guard, {"tool_name": "Edit", "cwd": str(feature),
                                  "tool_input": {"file_path": str(records / "docs/STATUS.md")}})
        self.assertIsNone(self.verdict(allow))

    def test_ui_context_reads_config_from_the_edited_paths_checkout(self) -> None:
        a = self.repo("a", "main", {".devex/ui-context.json": '{"ui_globs": ["**/*.zz"]}'})
        b = self.repo("b", "main")
        (b / "x.zz").write_text("x\n")
        (a / "x.zz").write_text("x\n")
        hook = TEMPLATES / "ui-context.py"
        env_state = {"DEVEX_STATE_DIR": str(self.base)}
        self.env.update(env_state)
        hit = self.fire(hook, {"tool_name": "Edit", "cwd": str(b), "session_id": "s1",
                               "tool_input": {"file_path": str(a / "x.zz")}})
        self.assertIn("additionalContext", hit.stdout)
        miss = self.fire(hook, {"tool_name": "Edit", "cwd": str(a), "session_id": "s2",
                                "tool_input": {"file_path": str(b / "x.zz")}})
        self.assertEqual(miss.stdout.strip(), "")

    def test_post_edit_ratchet_uses_the_owning_checkouts_config(self) -> None:
        a = self.repo("a", "main")
        b = self.repo("b", "main")
        (a / ".devex").mkdir()
        (a / ".devex/ratchet.config.json").write_text(json.dumps(
            {"globs": ["**/*.css"], "rules": [{"id": "hex", "regex": "#[0-9a-f]{6}", "message": "m"}]}))
        engine = SCRIPTS / "literal_ratchet.py"
        (a / "a.css").write_text("a{color:#ff0000}\n")
        subprocess.run([sys.executable, str(engine), "--root", str(a), "--update-baseline"],
                       check=True, capture_output=True, env=self.env)
        (a / "a.css").write_text("a{color:#ff0000;background:#00ff00}\n")
        hook = TEMPLATES / "post-edit-ratchet.py"
        self.env["DEVEX_RATCHET"] = str(engine)
        out = self.fire(hook, {"tool_name": "Write", "cwd": str(b),
                               "tool_input": {"file_path": str(a / "a.css")}})
        self.assertEqual(self.verdict(out), "block")


class BashResolutionTests(GitCase):
    def setUp(self) -> None:
        super().setUp()
        self.repo_path = self.repo("r", "feat/x", {"docs/STATUS.md": "s\n", "docs/ROADMAP.md": "r\n"})
        self.sibling = self.repo("sib", "feat/y", {"docs/STATUS.md": "s\n"})
        self.guard = TEMPLATES / "records-guard.py"
        # a copy beside bashwrites.py exactly as adoption installs it
        self.dest = self.base / "hooks"
        self.dest.mkdir()
        for name in ("records-guard.py", "bashwrites.py"):
            (self.dest / name).write_bytes((TEMPLATES / name).read_bytes())

    def bash(self, command: str, cwd: Path):
        return self.verdict(self.fire(self.dest / "records-guard.py",
                                      {"tool_name": "Bash", "cwd": str(cwd),
                                       "tool_input": {"command": command}}))

    def test_bare_name_after_cd_is_resolved(self) -> None:
        self.assertEqual(self.bash("cd docs && echo x > STATUS.md", self.repo_path), "deny")

    def test_session_in_a_subdirectory_writing_a_bare_name(self) -> None:
        self.assertEqual(self.bash("echo x > STATUS.md", self.repo_path / "docs"), "deny")

    def test_sibling_checkout_is_judged_by_its_own_branch(self) -> None:
        self.assertEqual(self.bash("cd ../sib/docs && sed -i '' s/s/t/ STATUS.md", self.repo_path), "deny")

    def test_glob_variable_and_interpreter_forms(self) -> None:
        for command in ("echo x > docs/STAT*.md",
                        "F=docs/STATUS.md; echo x >> $F",
                        "bash -c 'cd docs && tee STATUS.md'",
                        "python3 -c \"open('docs/'+'STATUS.md','w').write('x')\"",
                        "cd docs; python3 -c \"open('STATUS.md','w').write('x')\"",
                        "git -C docs checkout STATUS.md"):
            with self.subTest(command=command):
                self.assertEqual(self.bash(command, self.repo_path), "deny")

    def test_reads_and_other_files_are_allowed(self) -> None:
        for command in ("cat docs/STATUS.md", "cd docs && grep x STATUS.md",
                        "echo x > docs/notes.md", "ls 2>/dev/null; echo STATUS.md"):
            with self.subTest(command=command):
                self.assertIsNone(self.bash(command, self.repo_path))

    def test_records_branch_allows_the_write(self) -> None:
        self.git(self.repo_path, "checkout", "-q", "-b", "records/z")
        self.assertIsNone(self.bash("cd docs && echo x > STATUS.md", self.repo_path))

    def test_resolved_write_is_judged_only_by_its_owning_checkout(self) -> None:
        rec = self.repo("g-rec", "records/z", {"STATUS.md": "s\n"})
        feat = self.repo("g-feat", "feat/q", {"STATUS.md": "s\n"})
        self.assertIsNone(self.bash(f"echo x > {rec}/STATUS.md", feat))
        self.assertIsNone(self.bash("echo x > ../g-rec/STATUS.md", feat))
        self.assertEqual(self.bash(f"echo x > {feat}/STATUS.md", rec), "deny")

    def test_reads_that_mention_a_protected_name_with_a_write_looking_char(self) -> None:
        for command in ('grep ">" docs/STATUS.md', "echo hi > out.txt; cat docs/STATUS.md"):
            with self.subTest(command=command):
                self.assertIsNone(self.bash(command, self.repo_path))

    def test_without_bashwrites_the_text_heuristic_still_denies(self) -> None:
        (self.dest / "bashwrites.py").unlink()
        self.assertEqual(self.bash("echo x > docs/STATUS.md", self.repo_path), "deny")


class ConfigFlagAndGuardTests(GitCase):
    def test_records_guard_config_flag_reads_another_file(self) -> None:
        repo = self.repo("r", "feat/x", {"x.cfg": "c\n", "docs/STATUS.md": "s\n"})
        (repo / "alt.json").write_text('{"protected": ["x.cfg"], "branch_patterns": ["ok/*"]}')
        guard = TEMPLATES / "records-guard.py"
        payload = {"tool_name": "Edit", "cwd": str(repo), "tool_input": {"file_path": str(repo / "x.cfg")}}
        self.assertEqual(self.verdict(self.fire(guard, payload, "--config", "alt.json")), "deny")
        self.assertIsNone(self.verdict(self.fire(guard, payload)))
        status = {"tool_name": "Edit", "cwd": str(repo), "tool_input": {"file_path": str(repo / "docs/STATUS.md")}}
        self.assertIsNone(self.verdict(self.fire(guard, status, "--config", "alt.json")))

    def test_records_guard_config_flag_staged_mode(self) -> None:
        repo = self.repo("r", "feat/x", {"x.cfg": "c\n"})
        (repo / "alt.json").write_text('{"protected": ["x.cfg"], "branch_patterns": ["ok/*"]}')
        (repo / "x.cfg").write_text("changed\n")
        self.git(repo, "add", "x.cfg")
        result = self.fire(TEMPLATES / "records-guard.py", "", "--staged", "--config", "alt.json", cwd=repo)
        self.assertEqual(result.returncode, 1)
        self.assertIn("x.cfg", result.stderr)

    def test_config_guard_protects_an_unknown_devex_json_by_default(self) -> None:
        repo = self.repo("r", "feat/x", {".devex/other.json": "{}\n"})
        for name in ("records-guard.py", "config-guard.py", "bashwrites.py"):
            (repo / name).write_bytes((TEMPLATES / name).read_bytes())
        guard = repo / "config-guard.py"
        edit = {"tool_name": "Write", "cwd": str(repo),
                "tool_input": {"file_path": str(repo / ".devex/brand-new.json")}}
        self.assertEqual(self.verdict(self.fire(guard, edit)), "deny")
        self.git(repo, "checkout", "-q", "-b", "harness/ok")
        self.assertIsNone(self.verdict(self.fire(guard, edit)))

    def test_config_guard_cannot_be_weakened_by_its_own_config(self) -> None:
        repo = self.repo("r", "feat/x", {".devex/config-guard.json":
                                         '{"protected": ["only.txt"], "branch_patterns": ["harness/*"]}'})
        for name in ("records-guard.py", "config-guard.py", "bashwrites.py"):
            (repo / name).write_bytes((TEMPLATES / name).read_bytes())
        edit = {"tool_name": "Edit", "cwd": str(repo),
                "tool_input": {"file_path": str(repo / ".devex/ratchet.baseline.json")}}
        self.assertEqual(self.verdict(self.fire(repo / "config-guard.py", edit)), "deny")

    def test_config_guard_bash_write_to_unknown_json_after_cd(self) -> None:
        repo = self.repo("r", "feat/x")
        (repo / ".devex").mkdir()
        for name in ("records-guard.py", "config-guard.py", "bashwrites.py"):
            (repo / name).write_bytes((TEMPLATES / name).read_bytes())
        payload = {"tool_name": "Bash", "cwd": str(repo),
                   "tool_input": {"command": "cd .devex && echo '{}' > fresh.json"}}
        self.assertEqual(self.verdict(self.fire(repo / "config-guard.py", payload)), "deny")


class MatcherAndSkillTests(GitCase):
    def test_ui_context_matches_a_trailing_double_star(self) -> None:
        repo = self.repo("r", "main", {".devex/ui-context.json": '{"ui_globs": ["panel/**"]}'})
        (repo / "panel/Sources").mkdir(parents=True)
        (repo / "panel/Sources/V.swift").write_text("x\n")
        self.env["DEVEX_STATE_DIR"] = str(self.base)
        out = self.fire(TEMPLATES / "ui-context.py", {
            "tool_name": "Edit", "cwd": str(repo), "session_id": "t1",
            "tool_input": {"file_path": str(repo / "panel/Sources/V.swift")}})
        self.assertIn("additionalContext", out.stdout)

    def test_ui_context_and_ratchet_share_one_matcher(self) -> None:
        ui = load(TEMPLATES / "ui-context.py", "uic")
        engine = load(SCRIPTS / "literal_ratchet.py", "lr")
        patterns = ["**/*.swift", "panel/**", "panel/**/*", "a/*.css", "**", "x?.js", "a/**/b.css"]
        paths = ["V.swift", "panel/a/V.swift", "panel/V.swift", "a/x.css", "a/b/x.css",
                 "xa.js", "a/b.css", "a/c/d/b.css", "other/panel/V.swift"]
        for pattern in patterns:
            for path in paths:
                with self.subTest(pattern=pattern, path=path):
                    self.assertEqual(bool(ui.glob_to_regex(pattern).match(path)),
                                     bool(engine.glob_to_regex(pattern).match(path)))

    def fire_skill(self, skill: str) -> str:
        repo = self.repo("r" + str(abs(hash(skill)) % 1000), "main",
                         {".devex/ui-context.json": json.dumps({"ui_globs": ["**/*.css"], "skill": skill})})
        (repo / "a.css").write_text("x\n")
        self.env["DEVEX_STATE_DIR"] = str(self.base)
        out = self.fire(TEMPLATES / "ui-context.py", {
            "tool_name": "Edit", "cwd": str(repo), "session_id": "sk" + skill,
            "tool_input": {"file_path": str(repo / "a.css")}})
        return json.loads(out.stdout)["hookSpecificOutput"]["additionalContext"]

    def test_skill_name_and_skill_path_are_worded_differently(self) -> None:
        self.assertIn("load the `design-steward` skill", self.fire_skill("design-steward"))
        message = self.fire_skill("skills/design/SKILL.md")
        self.assertIn("read the design skill at `skills/design/SKILL.md`", message)
        self.assertNotIn("skill and the project", message.split("at `")[0])


class RaiseNoteTests(GitCase):
    CONFIG = {"globs": ["**/*.css"], "rules": [{"id": "hex", "regex": "#[0-9a-f]{6}"}]}

    def setUp(self) -> None:
        super().setUp()
        self.repo_path = self.repo("r", "main", {
            ".devex/ratchet.config.json": json.dumps(self.CONFIG),
            ".devex/ratchet.baseline.json": json.dumps({"version": 1, "counts": {"hex": {"a.css": 1}}}),
            "a.css": "a{color:#ff0000}\n"})
        self.git(self.repo_path, "checkout", "-q", "-b", "feat/raise")
        self.engine = SCRIPTS / "literal_ratchet.py"

    def baseline(self, counts: dict) -> None:
        (self.repo_path / ".devex/ratchet.baseline.json").write_text(
            json.dumps({"version": 1, "counts": counts}))

    def check(self):
        return subprocess.run([sys.executable, str(self.engine), "--root", str(self.repo_path),
                               "--check-raise", "main"], capture_output=True, text=True, env=self.env)

    def test_unresolvable_base_ref_is_an_error_not_a_pass(self) -> None:
        result = subprocess.run([sys.executable, str(self.engine), "--root", str(self.repo_path),
                                 "--check-raise", "nosuchref"], capture_output=True, text=True, env=self.env)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot resolve base ref", result.stderr)

    def test_no_raise_passes(self) -> None:
        self.baseline({"hex": {"a.css": 0}})
        self.assertEqual(self.check().returncode, 0)

    def test_raise_without_a_note_fails_on_any_branch_name(self) -> None:
        self.baseline({"hex": {"a.css": 3}})
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("is missing", result.stderr)

    def test_raise_with_a_reasoned_note_passes(self) -> None:
        self.baseline({"hex": {"a.css": 3}})
        (self.repo_path / ".devex/baseline-raise.txt").write_text("hex a.css generated fixture colours\n")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("covered: [hex] a.css 1 -> 3", result.stdout)

    def test_note_without_reason_or_for_another_file_fails(self) -> None:
        self.baseline({"hex": {"a.css": 3}})
        note = self.repo_path / ".devex/baseline-raise.txt"
        note.write_text("hex a.css\n")
        self.assertEqual(self.check().returncode, 1)
        note.write_text("hex b.css because reasons\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("matches no raise", result.stderr)

    def test_a_stale_note_unchanged_since_base_fails(self) -> None:
        note = self.repo_path / ".devex/baseline-raise.txt"
        self.git(self.repo_path, "checkout", "-q", "main")
        note.write_text("hex a.css earlier raise\n")
        self.git(self.repo_path, "add", "-A")
        self.git(self.repo_path, "commit", "-q", "-m", "note")
        self.git(self.repo_path, "checkout", "-q", "-b", "feat/two")
        self.baseline({"hex": {"a.css": 5}})
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("unchanged", result.stderr)

    def test_a_new_file_for_a_known_rule_needs_a_line_a_new_rule_does_not(self) -> None:
        self.baseline({"hex": {"a.css": 1, "b.css": 2}})
        self.assertEqual(self.check().returncode, 1)
        self.baseline({"hex": {"a.css": 1}, "other": {"z.css": 9}})
        self.assertEqual(self.check().returncode, 0)


class RegistrationAuditTests(GitCase):
    def audit(self, root: Path, config: dict):
        (root / ".devex").mkdir(exist_ok=True)
        (root / ".devex/test-registration.json").write_text(json.dumps(config))
        return subprocess.run([sys.executable, str(SCRIPTS / "registration_audit.py"), "--root", str(root)],
                              capture_output=True, text=True)

    def project(self) -> Path:
        root = self.base / "p"
        (root / "test").mkdir(parents=True)
        (root / "test/a.test.sh").write_text("true\n")
        (root / "test/b.test.sh").write_text("true\n")
        (root / "Makefile").write_text("test:\n\tbash test/a.test.sh\n")
        return root

    CONFIG = {"scripts": ["test/**/*.test.sh"], "runners": ["Makefile"]}

    def test_unregistered_script_fails_and_registered_passes(self) -> None:
        result = self.audit(self.project(), self.CONFIG)
        self.assertEqual(result.returncode, 1)
        self.assertIn("test/b.test.sh: not registered", result.stderr)
        self.assertNotIn("a.test.sh", result.stderr)

    def test_exclusion_needs_a_reason_and_goes_stale(self) -> None:
        root = self.project()
        ok = self.audit(root, {**self.CONFIG, "allow": [{"path": "test/b.test.sh", "reason": "run by a.test.sh"}]})
        self.assertEqual(ok.returncode, 0, ok.stderr)
        bare = self.audit(root, {**self.CONFIG, "allow": [{"path": "test/b.test.sh", "reason": ""}]})
        self.assertEqual(bare.returncode, 1)
        self.assertIn("needs a reason", bare.stderr)
        stale = self.audit(root, {**self.CONFIG, "allow": [
            {"path": "test/b.test.sh", "reason": "r"}, {"path": "test/a.test.sh", "reason": "r"},
            {"path": "test/gone.test.sh", "reason": "r"}]})
        self.assertIn("test/a.test.sh: stale", stale.stderr)
        self.assertIn("test/gone.test.sh: stale", stale.stderr)

    def test_bad_config_is_exit_two(self) -> None:
        self.assertEqual(self.audit(self.project(), {"scripts": []}).returncode, 2)


class GateLogTests(GitCase):
    def path(self, root: Path, *args: str) -> str:
        env = {**self.env, "TMPDIR": str(self.base)}
        return subprocess.run([sys.executable, str(SCRIPTS / "gate_log.py"), "--root", str(root), *args],
                              capture_output=True, text=True, env=env, check=True).stdout.strip()

    def test_path_differs_per_worktree_and_per_commit_and_is_stable_otherwise(self) -> None:
        main = self.repo("main", "main")
        other = self.base / "other"
        self.git(main, "worktree", "add", "-q", "-b", "feat/o", str(other))
        a, b = self.path(main, "--name", "check"), self.path(other, "--name", "check")
        self.assertNotEqual(a, b)
        self.assertEqual(a, self.path(main / ".", "--name", "check"))
        self.assertTrue(a.startswith(str(self.base)) and a.endswith(".log"))
        (main / "n.txt").write_text("n\n")
        self.git(main, "add", "-A")
        self.git(main, "commit", "-q", "-m", "n")
        self.assertNotEqual(a, self.path(main, "--name", "check"))

    def test_outside_git_uses_nogit(self) -> None:
        plain = self.base / "plain"
        plain.mkdir()
        self.assertIn("-nogit.log", self.path(plain))


if __name__ == "__main__":
    unittest.main()
