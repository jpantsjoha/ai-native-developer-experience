import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "hitl_queue.py"
HEAD = ("| Item | Type | Role | Ref | Unblocks | Cost if wrong | Reversibility | "
        "Recommendation | Raised | Due | Record |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
GOOD = ("| Choose the retention period | decision | data owner | #41 | #38; M2 | Rework | "
        "costly | 90 days | 2026-11-20 | 2026-11-22 | ADR-007 |\n"
        "| Run the signing step | action | operator | local | - | - | cheap | - | "
        "2026-11-20 | - | STATUS |\n")


def run(*args, cwd=None):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                          text=True, cwd=cwd)


def make_repo(tmp: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(tmp)], check=True)
    (tmp / ".gitignore").write_text("/HITL/OPERATOR/*\n!/HITL/OPERATOR/README.md\n")
    (tmp / "HITL/OPERATOR").mkdir(parents=True)
    return tmp


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.root = make_repo(Path(self._t.name))
        self.q = self.root / "HITL/OPERATOR/Master-TODO.md"

    def tearDown(self):
        self._t.cleanup()

    def validate(self):
        return run("validate", "--root", str(self.root))

    def test_absent_queue_skips_cleanly(self):
        r = self.validate()
        self.assertEqual(r.returncode, 0)
        self.assertIn("skipped", r.stdout)

    def test_no_folder_skips_cleanly(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(run("validate", "--root", d).returncode, 0)

    def test_conforming_file_runs_and_passes(self):
        self.q.write_text(HEAD + GOOD)
        r = self.validate()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1 file(s) valid", r.stdout)

    def test_rejections(self):
        cols = HEAD.splitlines()[0]
        row = GOOD.splitlines()[0]
        cases = {
            "missing column": cols.replace(" Record |", "") + "\n" + HEAD.splitlines()[1] + "\n" + row,
            "reordered": cols.replace("Type | Role", "Role | Type") + "\n" + HEAD.splitlines()[1] + "\n" + row,
            "unknown type": HEAD + row.replace("decision", "wish"),
            "unknown reversibility": HEAD + row.replace("costly", "maybe"),
            "bad date": HEAD + row.replace("2026-11-20", "20/11/2026"),
            "impossible date": HEAD + row.replace("2026-11-22", "2026-13-45"),
            "empty required": HEAD + row.replace("data owner", ""),
            "empty optional not dash": HEAD + row.replace("90 days", ""),
        }
        for name, body in cases.items():
            with self.subTest(name):
                self.q.write_text(body + "\n")
                self.assertEqual(self.validate().returncode, 1)

    def test_tracked_queue_fails(self):
        self.q.write_text(HEAD + GOOD)
        subprocess.run(["git", "-C", str(self.root), "add", "-f", str(self.q)], check=True)
        r = self.validate()
        self.assertEqual(r.returncode, 1)
        self.assertIn("tracked", r.stderr)

    def test_unignored_queue_fails(self):
        (self.root / ".gitignore").write_text("")
        self.q.write_text(HEAD + GOOD)
        self.assertIn("not git-ignored", self.validate().stderr)


class MigrateTests(unittest.TestCase):
    SRC = ("# Status\n\n| Decision | Recommendation | Unblocks | Reversibility |\n"
           "| --- | --- | --- | --- |\n"
           "| Keep the entry skill ([PR #19](https://x/pull/19)) | Keep | - | cheap |\n"
           "| Fix README count ([#8](https://x/issues/8)) | Correct it | README | cheap |\n"
           "| No reversibility | x | - | |\n")

    def test_migrate_copies_open_items_and_leaves_source_identical(self):
        with tempfile.TemporaryDirectory() as d:
            root = make_repo(Path(d))
            src = root / "status.md"
            src.write_text(self.SRC)
            before = src.read_bytes()
            dry = run("migrate", "--root", str(root), "--source", str(src))
            self.assertEqual(dry.returncode, 0)
            self.assertFalse((root / "HITL/OPERATOR/Master-TODO.md").exists())
            r = run("migrate", "--root", str(root), "--source", str(src), "--yes",
                    "--today", "2026-11-26")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(src.read_bytes(), before)
            q = (root / "HITL/OPERATOR/Master-TODO.md").read_text()
            self.assertEqual(len([l for l in q.splitlines() if l.startswith("|")]), 4)
            self.assertIn("| #8 |", q)
            self.assertEqual(run("validate", "--root", str(root)).returncode, 0)
            again = run("migrate", "--root", str(root), "--source", str(src), "--yes",
                        "--today", "2026-11-27")
            self.assertIn("already present", again.stdout)
            self.assertEqual((root / "HITL/OPERATOR/Master-TODO.md").read_text(), q)
            self.assertEqual(src.read_bytes(), before)


class RepoTests(unittest.TestCase):
    def test_this_repo_ignores_queue_and_commits_readme(self):
        ignored = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q",
                                  "HITL/OPERATOR/Master-TODO.md"])
        self.assertEqual(ignored.returncode, 0)
        self.assertTrue((ROOT / "HITL/OPERATOR/README.md").is_file())
        self.assertEqual(run("validate", "--root", str(ROOT)).returncode, 0)


if __name__ == "__main__":
    unittest.main()
