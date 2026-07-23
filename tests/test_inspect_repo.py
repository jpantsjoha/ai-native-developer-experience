"""Regression tests for the read-only repository-inspection backfill engine."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / ".agents" / "skills" / "operating-model-bootstrap"
INSPECT = SKILL_ROOT / "scripts" / "inspect_repo.py"
BOOTSTRAP = SKILL_ROOT / "scripts" / "bootstrap_operating_model.py"
VALIDATE = SKILL_ROOT / "scripts" / "validate_operating_model.py"


def run_inspect(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INSPECT), str(repo)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class InspectRepoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, relative: str, content: str) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_infers_stack_tooling_ci_vision_and_stays_read_only(self) -> None:
        self.write("package.json", json.dumps(
            {"name": "widget", "devDependencies": {"typescript": "^5"}, "dependencies": {"react": "^18"}}
        ))
        self.write("tsconfig.json", "{}")
        self.write(".github/workflows/ci.yml", "name: CI\non: [push]\n")
        self.write("README.md", "# Acme Widget\n\nA thing.\n")
        self.write("Makefile", "test:\n\tpytest\nlint:\n\truff .\n")
        self.write("CODEOWNERS", "* @alice @bob\n")

        snapshot = sorted(str(p.relative_to(self.repo)) for p in self.repo.rglob("*"))
        result = run_inspect(self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        out = result.stdout

        # Stack + evidence pointer.
        self.assertIn("TypeScript", out)
        self.assertIn("React", out)
        self.assertIn("source: package.json", out)
        # Automation + delivery + vision.
        self.assertIn("GitHub Actions", out)
        self.assertIn("Acme Widget", out)
        # Every finding is an inferred marker, never a bare verified fact.
        self.assertIn("inferred — source:", out)

        # Read-only: inspection created/changed nothing in the target repo.
        after = sorted(str(p.relative_to(self.repo)) for p in self.repo.rglob("*"))
        self.assertEqual(snapshot, after)

    def test_authority_is_never_inferred(self) -> None:
        self.write("CODEOWNERS", "* @alice @bob\n")
        result = run_inspect(self.repo)
        out = result.stdout
        # CODEOWNERS handles surface as candidates only, at low confidence, and the
        # finding explicitly disclaims inferring role/authority.
        self.assertIn("role/authority NOT inferred", out)
        self.assertIn("confidence: low", out)

    def test_empty_repo_infers_nothing(self) -> None:
        result = run_inspect(self.repo)
        self.assertEqual(result.returncode, 0)
        self.assertIn("No inferable evidence", result.stdout)

    def test_engine_marker_trips_the_validator_active_gate(self) -> None:
        """Bind producer to enforcer: a marker inspect_repo actually emits must be caught
        by the validator's active-gate, so the two cannot drift apart and let unconfirmed
        inference reach `active`. (Adversarial-gate finding: separate unit tests miss this.)
        """
        self.write("package.json", json.dumps({"name": "x", "devDependencies": {"typescript": "^5"}}))
        emitted = [
            line.strip().strip("`")
            for line in run_inspect(self.repo).stdout.splitlines()
            if line.strip().strip("`").startswith("inferred — source:")
        ]
        self.assertTrue(emitted, "engine emitted no inferred markers to bind against")
        marker = emitted[0]

        project = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, project, ignore_errors=True)
        boot = subprocess.run(
            [sys.executable, str(BOOTSTRAP), "--project-name", "Probe", str(project)],
            cwd=REPO_ROOT, check=False, capture_output=True, text=True,
        )
        self.assertEqual(boot.returncode, 0, boot.stderr)
        profile = project / "docs" / "operating-model" / "PROJECT-OPERATING-PROFILE.md"
        profile.write_text(
            profile.read_text(encoding="utf-8")
            .replace("**Adoption status:** seed", "**Adoption status:** active")
            .replace("**Profile owner:** <accountable human or role>", f"**Profile owner:** {marker}"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(VALIDATE), "--target", str(project), "--require-active"],
            cwd=REPO_ROOT, check=False, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("unconfirmed inferred", result.stderr)


if __name__ == "__main__":
    unittest.main()
