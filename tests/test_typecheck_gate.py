"""Negative tests for the `make typecheck` gate: it must fail closed.

Each case copies the real Makefile into a throwaway tree, so the recipe under test is the
shipped one and nothing in the repository is compiled or written.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAKE = shutil.which("make")


@unittest.skipIf(MAKE is None, "make is not installed")
class TypecheckGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        shutil.copy(ROOT / "Makefile", self.root / "Makefile")
        self.write("scripts/ok.py", "print('ok')\n")
        self.write("tests/test_ok.py", "x = 1\n")
        self.write("skills/demo/scripts/tool.py", "y = 2\n")
        self.write("skills/demo/scripts/run.sh", "#!/bin/sh\necho ok\n")
        self.write(".githooks/pre-commit", "#!/bin/sh\nexit 0\n")
        self.write("hooks/session-start", "#!/bin/sh\nexit 0\n")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def typecheck(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [MAKE, "-s", "typecheck", f"PYTHON={sys.executable}"],
            cwd=self.root, text=True, capture_output=True, check=False,
        )

    def test_clean_tree_passes(self) -> None:
        result = self.typecheck()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_python_syntax_error_fails(self) -> None:
        self.write("skills/demo/scripts/broken.py", "def broken(:\n")
        self.assertNotEqual(self.typecheck().returncode, 0)

    def test_shell_syntax_error_fails(self) -> None:
        self.write("skills/demo/scripts/broken.sh", "if then fi (\n")
        self.assertNotEqual(self.typecheck().returncode, 0)

    def test_missing_discovery_root_fails(self) -> None:
        shutil.rmtree(self.root / "skills")
        result = self.typecheck()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("discovery failed", result.stderr)

    def test_missing_fixed_shell_script_fails(self) -> None:
        (self.root / "hooks" / "session-start").unlink()
        result = self.typecheck()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing shell script", result.stderr)


if __name__ == "__main__":
    unittest.main()
