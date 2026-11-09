"""Fixtures for the read-only lane hygiene report: verdicts and proof of no mutation."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/lane_hygiene.py"
ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "Fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}


class LaneHygieneTests(unittest.TestCase):
    """Build one repository holding every lane shape, then inspect the real CLI."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.commit("README.md", "seed\n", "seed")

        # Merged with a merge commit: integrated by ancestry.
        self.lane("merged", ["a.txt"])
        self.git("merge", "-q", "--no-ff", "merged", "-m", "merge merged")
        # Squash-merged with two commits: only the squash check can see it.
        self.lane("squashed", ["b1.txt", "b2.txt"])
        self.git("merge", "-q", "--squash", "squashed")
        self.git("commit", "-q", "-m", "squash squashed")
        # Rebased onto main commit by commit: patch-equivalent.
        self.lane("rebased", ["c.txt"])
        tip = self.git("rev-parse", "rebased").strip()
        self.commit("main-moves.txt", "m\n", "main moves on")  # forces a new commit ID
        self.git("cherry-pick", tip)
        # Unmerged work, dirty work, a deleted worktree path, and a plain merged branch.
        self.lane("active", ["d.txt"])
        self.lane("dirty", ["e.txt"])
        (self.base / "wt-dirty" / "uncommitted.txt").write_text("wip\n")
        self.lane("vanished", ["f.txt"])
        shutil.rmtree(self.base / "wt-vanished")
        self.git("branch", "branch-only")
        self.git("checkout", "-q", "branch-only")
        self.commit("g.txt", "g\n", "branch-only work")
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--no-ff", "branch-only", "-m", "merge branch-only")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def git(self, *args: str, cwd: Path | None = None) -> str:
        """Run git in the fixture with an isolated configuration."""
        return subprocess.run(["git", *args], cwd=cwd or self.repo, env=ENV, check=True,
                              capture_output=True, text=True).stdout

    def commit(self, name: str, text: str, message: str, cwd: Path | None = None) -> None:
        """Write one file and commit it."""
        (cwd or self.repo).joinpath(name).write_text(text)
        self.git("add", name, cwd=cwd)
        self.git("commit", "-q", "-m", message, cwd=cwd)

    def lane(self, name: str, files: list[str]) -> None:
        """Create a worktree lane with one commit per file, branched from main."""
        path = self.base / f"wt-{name}"
        self.git("worktree", "add", "-q", "-b", name, str(path), "main")
        for file in files:
            self.commit(file, f"{file}\n", f"{name}: {file}", cwd=path)

    def run_report(self, *extra: str) -> subprocess.CompletedProcess:
        """Invoke the CLI as a user would."""
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.repo),
                               "--base", "main", *extra], env=ENV, capture_output=True,
                              text=True, cwd=self.base)

    def verdicts(self, *extra: str) -> dict[str, str]:
        """Map each reported name fragment to its category."""
        result = self.run_report("--json", *extra)
        self.assertEqual(result.returncode, 0, result.stderr)
        return {item["name"]: item["category"]
                for item in json.loads(result.stdout)["items"]}

    def category(self, verdicts: dict[str, str], fragment: str) -> str:
        """Find the single verdict whose name contains `fragment`."""
        found = [cat for name, cat in verdicts.items() if fragment in name]
        self.assertEqual(len(found), 1, (fragment, verdicts))
        return found[0]

    def snapshot(self) -> tuple:
        """Everything the report must not change: refs, worktrees, status, every index."""
        indexes = sorted((self.repo / ".git").glob("worktrees/*/index"))
        return (self.git("for-each-ref"), self.git("worktree", "list", "--porcelain"),
                self.git("status", "--porcelain", cwd=self.base / "wt-dirty"),
                (self.repo / ".git" / "index").read_bytes(),
                [(str(path), path.read_bytes()) for path in indexes])

    def test_each_lane_shape_gets_the_right_verdict(self) -> None:
        verdicts = self.verdicts()
        self.assertEqual(self.category(verdicts, "[merged]"), "remove-candidate")
        self.assertEqual(self.category(verdicts, "[squashed]"), "remove-candidate")
        self.assertEqual(self.category(verdicts, "[rebased]"), "remove-candidate")
        self.assertEqual(self.category(verdicts, "[active]"), "active")
        self.assertEqual(self.category(verdicts, "[dirty]"), "keep-dirty")
        self.assertEqual(self.category(verdicts, "[vanished]"), "stale-metadata")
        self.assertEqual(self.category(verdicts, "branch-only"), "branch-remove-candidate")
        self.assertEqual(self.category(verdicts, "[main]"), "primary")

    def test_integration_method_is_reported(self) -> None:
        items = json.loads(self.run_report("--json").stdout)["items"]
        methods = {item["name"].rsplit("[", 1)[-1].rstrip("]"): item["detail"].get("integration")
                   for item in items if item["kind"] == "worktree"}
        self.assertEqual(methods["merged"], "ancestry")
        self.assertEqual(methods["squashed"], "squash-equivalent")
        self.assertEqual(methods["rebased"], "patch-equivalent")

    def test_report_changes_nothing(self) -> None:
        # Make linked-worktree indexes stat-stale, so a status that refreshed them would show.
        for lane in ("wt-merged", "wt-squashed", "wt-active"):
            tracked = self.base / lane / "README.md"
            os.utime(tracked, (1_000_000_000, 1_000_000_000))
        before = self.snapshot()
        self.run_report()
        self.run_report("--json", "--strict")
        self.assertEqual(before, self.snapshot())
        self.assertTrue((self.base / "wt-merged").is_dir())
        self.assertTrue((self.base / "wt-dirty" / "uncommitted.txt").is_file())

    def test_strict_fails_only_when_removable_items_exist(self) -> None:
        self.assertEqual(self.run_report("--strict").returncode, 1)
        clean = self.base / "clean"
        clean.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=clean, env=ENV, check=True)
        self.commit("x.txt", "x\n", "seed", cwd=clean)
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(clean),
                                 "--base", "main", "--strict"], env=ENV,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_suggestions_are_printed_not_run(self) -> None:
        result = self.run_report()
        self.assertIn("suggested, not run: git worktree remove", result.stdout)
        self.assertIn("Nothing was changed.", result.stdout)

    def test_stale_plugin_registrations_are_reported(self) -> None:
        registry = self.base / "installed_plugins.json"
        registry.write_text(json.dumps({"version": 2, "plugins": {"devex-charter@m": [
            {"scope": "user"},
            {"scope": "project", "projectPath": str(self.repo)},
            {"scope": "project", "projectPath": str(self.base / "gone")},
        ]}}))
        verdicts = self.verdicts("--installed-plugins", str(registry))
        stale = [name for name, cat in verdicts.items() if cat == "stale-registration"]
        self.assertEqual(stale, [f"devex-charter@m @ {self.base / 'gone'}"])

    def test_merge_commit_carrying_unmerged_content_is_not_integrated(self) -> None:
        # Every non-merge commit is cherry-picked onto main, but the merge commit itself
        # adds a file main never receives. `git cherry` alone would call this integrated.
        self.git("checkout", "-q", "-b", "hidden", "main")
        self.commit("x.txt", "x\n", "hidden: x")
        x_commit = self.git("rev-parse", "HEAD").strip()
        self.git("checkout", "-q", "-b", "side", "main")
        self.commit("s.txt", "s\n", "side: s")
        s_commit = self.git("rev-parse", "HEAD").strip()
        self.git("checkout", "-q", "hidden")
        self.git("merge", "-q", "--no-ff", "--no-commit", "side")
        (self.repo / "unmerged.txt").write_text("only in the merge commit\n")
        self.git("add", "unmerged.txt")
        self.git("commit", "-q", "-m", "merge side into hidden, plus unmerged.txt")
        self.git("checkout", "-q", "main")
        self.commit("main-2.txt", "m\n", "main moves")
        self.git("cherry-pick", x_commit)
        self.git("cherry-pick", s_commit)
        verdicts = self.verdicts()
        self.assertNotEqual(verdicts.get("hidden"), "branch-remove-candidate", verdicts)

    def test_partial_squash_is_not_integrated(self) -> None:
        self.git("checkout", "-q", "-b", "partial", "main")
        self.commit("p1.txt", "p1\n", "partial: p1")
        self.commit("p2.txt", "p2\n", "partial: p2")
        self.git("checkout", "-q", "main")
        self.commit("p1.txt", "p1\n", "squash of the first commit only")
        verdicts = self.verdicts()
        self.assertNotEqual(verdicts.get("partial"), "branch-remove-candidate")

    def test_fresh_lane_is_never_removable(self) -> None:
        self.git("worktree", "add", "-q", "-b", "fresh", str(self.base / "wt-fresh"), "main")
        self.git("branch", "fresh-branch", "main")
        verdicts = self.verdicts()
        self.assertEqual(self.category(verdicts, "[fresh]"), "review-no-unique-commits")
        self.assertEqual(verdicts["fresh-branch"], "review-no-unique-commits")

    def test_ignored_files_are_called_out(self) -> None:
        (self.repo / ".git" / "info").mkdir(exist_ok=True)
        (self.repo / ".git" / "info" / "exclude").write_text(".env\n")
        (self.base / "wt-merged" / ".env").write_text("SECRET=local\n")
        items = json.loads(self.run_report("--json").stdout)["items"]
        merged = [i for i in items if i["name"].endswith("[merged]")][0]
        self.assertEqual(merged["category"], "remove-candidate")
        self.assertIn("ignored path", merged["reason"])

    def test_suggestions_are_shell_quoted(self) -> None:
        odd = self.base / "wt it's odd"
        self.git("worktree", "add", "-q", "-b", "odd", str(odd), "main")
        self.commit("odd.txt", "odd\n", "odd work", cwd=odd)
        self.git("merge", "-q", "--no-ff", "odd", "-m", "merge odd")
        items = json.loads(self.run_report("--json").stdout)["items"]
        item = [i for i in items if i["name"].endswith("[odd]")][0]
        tokens = shlex.split(item["suggestion"])
        self.assertEqual(tokens[:4], ["git", "worktree", "remove", str(odd)])

    def test_pr_state_requires_the_pr_to_target_the_base(self) -> None:
        self.lane("pr-lane", ["pr.txt"])
        tip = self.git("rev-parse", "pr-lane").strip()
        fake = self.base / "fakebin"
        fake.mkdir()
        gh = fake / "gh"
        gh.write_text("#!/bin/sh\ncat \"$FAKE_GH_JSON\"\n")
        gh.chmod(0o755)
        answer = self.base / "gh.json"
        env = {**ENV, "PATH": f"{fake}{os.pathsep}{ENV['PATH']}", "FAKE_GH_JSON": str(answer)}

        def verdict(base_ref: str) -> str:
            answer.write_text(json.dumps([{"number": 7, "headRefOid": tip,
                                           "baseRefName": base_ref}]))
            result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.repo),
                                     "--base", "main", "--json", "--pr-state"], env=env,
                                    capture_output=True, text=True, cwd=self.base)
            self.assertEqual(result.returncode, 0, result.stderr)
            items = json.loads(result.stdout)["items"]
            return [i for i in items if i["name"].endswith("[pr-lane]")][0]["category"]

        self.assertEqual(verdict("release/1.0"), "active")
        self.assertEqual(verdict("main"), "remove-candidate")

    def test_long_lived_local_branches_are_never_candidates(self) -> None:
        for name in ("develop", "release/1.0"):
            self.git("checkout", "-q", "-b", name, "main")
            self.commit(f"{name.replace('/', '-')}.txt", "x\n", f"{name} work")
            self.git("checkout", "-q", "main")
            self.git("merge", "-q", "--no-ff", name, "-m", f"merge {name}")
        verdicts = self.verdicts()
        self.assertNotIn("develop", verdicts)
        self.assertNotIn("release/1.0", verdicts)

    def test_missing_base_is_a_harness_failure(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.repo),
                                 "--base", "no-such-branch"], env=ENV,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("base ref not found", result.stderr)


class RemoteBranchTests(unittest.TestCase):
    """Remote branches are judged against the remote's own base, never the local one."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.origin = self.base / "origin.git"
        self.repo = self.base / "repo"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.origin)],
                       env=ENV, check=True)
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("remote", "add", "origin", str(self.origin))
        self.commit("seed.txt", "seed\n", "seed")
        self.git("push", "-q", "origin", "main")
        # Merged on origin: the only true candidate.
        self.pushed_branch("done", merge=True, push_main=True)
        # Long-lived name merged on origin: never a candidate.
        self.pushed_branch("develop", merge=True, push_main=True)
        # Pushed, merged only into local main: origin/main lacks it.
        self.pushed_branch("local-only", merge=True, push_main=False)
        # Freshly cut from origin's main and pushed: no commits of its own.
        self.git("fetch", "-q", "origin")
        self.git("push", "-q", "origin", "refs/remotes/origin/main:refs/heads/fresh")
        # Another remote is out of scope by default.
        upstream = self.base / "upstream.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(upstream)],
                       env=ENV, check=True)
        self.git("remote", "add", "upstream", str(upstream))
        self.git("push", "-q", "upstream", "main", "done")
        self.git("fetch", "-q", "--all")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def git(self, *args: str) -> str:
        """Run git in the fixture with an isolated configuration."""
        return subprocess.run(["git", *args], cwd=self.repo, env=ENV, check=True,
                              capture_output=True, text=True).stdout

    def commit(self, name: str, text: str, message: str) -> None:
        """Write one file and commit it."""
        (self.repo / name).write_text(text)
        self.git("add", name)
        self.git("commit", "-q", "-m", message)

    def pushed_branch(self, name: str, merge: bool, push_main: bool) -> None:
        """Commit on a branch, push it, and optionally merge it into (local) main."""
        self.git("checkout", "-q", "-b", name, "main")
        self.commit(f"{name.replace('/', '-')}.txt", f"{name}\n", f"{name} work")
        self.git("push", "-q", "origin", name)
        self.git("checkout", "-q", "main")
        if merge:
            self.git("merge", "-q", "--no-ff", name, "-m", f"merge {name}")
        if push_main:
            self.git("push", "-q", "origin", "main")

    def remote_candidates(self, *extra: str) -> set[str]:
        """Names reported as remote-branch candidates."""
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.repo),
                                 "--json", *extra], env=ENV, capture_output=True,
                                text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return {item["name"] for item in json.loads(result.stdout)["items"]
                if item["category"] == "remote-branch-candidate"}

    def test_only_branches_merged_on_the_remote_are_candidates(self) -> None:
        self.assertEqual(self.remote_candidates("--base", "main"), {"origin/done"})

    def test_other_remotes_are_ignored_unless_asked(self) -> None:
        self.assertNotIn("upstream/done", self.remote_candidates("--base", "main"))


if __name__ == "__main__":
    unittest.main()
