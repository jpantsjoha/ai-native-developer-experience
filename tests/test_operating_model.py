"""Regression tests for the drop-in operating-model initializer and validator."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / ".agents" / "skills" / "operating-model-bootstrap"
BOOTSTRAP = SKILL_ROOT / "scripts" / "bootstrap_operating_model.py"
VALIDATE = SKILL_ROOT / "scripts" / "validate_operating_model.py"


def run_script(script: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    """Run one skill script exactly as an adopter would from a shell."""

    return subprocess.run(
        [sys.executable, str(script), *arguments],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class OperatingModelBootstrapTests(unittest.TestCase):
    """Exercise the safety and coherence contracts against disposable projects."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.target = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def install(self) -> subprocess.CompletedProcess[str]:
        """Install the standard all-surface seed into the disposable target."""

        return run_script(BOOTSTRAP, "--project-name", "Monday One", str(self.target))

    def test_clean_seed_installs_and_validates_with_readiness_warning(self) -> None:
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)

        expected_planning_seed = {
            "docs/VISION.md": "# Monday One Vision",
            "docs/ROADMAP.md": "# Monday One Roadmap",
            "docs/STATUS.md": "# Monday One Status",
            "docs/operating-model/DELIVERY-WORKFLOW.md": (
                "# Monday One Delivery Workflow"
            ),
            "CHANGELOG.md": "## Unreleased",
        }
        for relative_path, marker in expected_planning_seed.items():
            path = self.target / relative_path
            self.assertTrue(path.is_file(), relative_path)
            self.assertIn(marker, path.read_text(encoding="utf-8"))

        validation = run_script(VALIDATE, "--target", str(self.target))
        self.assertEqual(validation.returncode, 0, validation.stderr)
        self.assertIn("seed supports design/R0/R1 only", validation.stdout)
        self.assertIn("PASS operating-model validation", validation.stdout)

    def test_existing_difference_blocks_all_writes(self) -> None:
        (self.target / "CLAUDE.md").write_text("existing contract\n", encoding="utf-8")

        result = self.install()
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to overwrite", result.stderr)
        self.assertFalse((self.target / "docs" / "operating-model").exists())
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_existing_planning_file_is_preserved_while_missing_seed_is_created(self) -> None:
        docs = self.target / "docs"
        docs.mkdir()
        roadmap = docs / "ROADMAP.md"
        roadmap.write_text("# Existing roadmap\n", encoding="utf-8")

        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preserved existing: docs/ROADMAP.md", result.stdout)
        self.assertEqual(roadmap.read_text(encoding="utf-8"), "# Existing roadmap\n")
        self.assertTrue((self.target / "AGENTS.md").is_file())
        self.assertTrue((docs / "VISION.md").is_file())

    def test_dry_run_reports_planning_seed_without_writing(self) -> None:
        result = run_script(
            BOOTSTRAP,
            "--dry-run",
            "--project-name",
            "Monday One",
            str(self.target),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("would create: docs/VISION.md", result.stdout)
        self.assertIn("would create: docs/ROADMAP.md", result.stdout)
        self.assertIn("would create: docs/STATUS.md", result.stdout)
        self.assertIn("would create: CHANGELOG.md", result.stdout)
        self.assertIn("PASS dry-run preflight found no conflicts", result.stdout)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_generated_seed_is_idempotent(self) -> None:
        first = self.install()
        second = self.install()

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("unchanged: 12 matching file(s)", second.stdout)
        self.assertNotIn("created:", second.stdout)

    def test_one_surface_contract_change_fails_drift_validation(self) -> None:
        self.assertEqual(self.install().returncode, 0)
        adapter = self.target / "CLAUDE.md"
        adapter.write_text(
            adapter.read_text(encoding="utf-8").replace(
                "Classify risk before confirming authority",
                "Confirm authority before classifying risk",
            ),
            encoding="utf-8",
        )

        validation = run_script(VALIDATE, "--target", str(self.target))
        self.assertEqual(validation.returncode, 1)
        self.assertIn("semantic drift", validation.stderr)

    def test_manual_change_invalidates_profile_and_adapters(self) -> None:
        self.assertEqual(self.install().returncode, 0)
        manual = self.target / "docs" / "operating-model" / "OPERATING-MANUAL.md"
        manual.write_text(
            manual.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8"
        )

        validation = run_script(VALIDATE, "--target", str(self.target))
        self.assertEqual(validation.returncode, 1)
        self.assertIn("manual SHA-256 does not match", validation.stderr)
        self.assertIn("wrong manual digest", validation.stderr)

    def test_active_status_rejects_unresolved_placeholders(self) -> None:
        self.assertEqual(self.install().returncode, 0)
        profile = (
            self.target / "docs" / "operating-model" / "PROJECT-OPERATING-PROFILE.md"
        )
        profile.write_text(
            profile.read_text(encoding="utf-8").replace(
                "**Adoption status:** seed", "**Adoption status:** active"
            ),
            encoding="utf-8",
        )

        validation = run_script(
            VALIDATE, "--target", str(self.target), "--require-active"
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("active profile has", validation.stderr)

    def test_checkpoint_and_evidence_must_bind_to_same_candidate(self) -> None:
        self.assertEqual(self.install().returncode, 0)
        manual = self.target / "docs" / "operating-model" / "OPERATING-MANUAL.md"
        digest = hashlib.sha256(manual.read_bytes()).hexdigest()
        checkpoint = self.target / "checkpoint.yaml"
        evidence = self.target / "evidence.yaml"
        checkpoint.write_text(
            "operating_contract:\n"
            "  manual_version: 2.1.0\n"
            f"  manual_sha256: {digest}\n"
            "risk_tier: R2\n"
            "candidate_sha_or_tree_digest: candidate-a\n",
            encoding="utf-8",
        )
        evidence.write_text(
            "operating_contract:\n"
            "  manual_version: 2.1.0\n"
            f"  manual_sha256: {digest}\n"
            "candidate:\n"
            "  sha_or_digest: candidate-b\n",
            encoding="utf-8",
        )

        validation = run_script(
            VALIDATE,
            "--target",
            str(self.target),
            "--checkpoint",
            checkpoint.name,
            "--evidence",
            evidence.name,
        )
        self.assertEqual(validation.returncode, 1)
        self.assertIn("bind to different candidates", validation.stderr)


if __name__ == "__main__":
    unittest.main()
