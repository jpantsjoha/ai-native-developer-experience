"""Prove the literal ratchet bites: a rise fails, a fall passes, a raise-on-update is refused."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "scripts" / "literal_ratchet.py"
CONFIG = json.loads((ROOT / "hooks/templates/ratchet.config.example.json").read_text())

# stack -> (file, clean body, body with one more literal, extra literal line)
STACKS = {
    "swift": ("Views/Row.swift",
              "let a = Color(red: 1, green: 0, blue: 0)\nlet b = Color.accentColor\n",
              "let c = Color(red: 0, green: 1, blue: 0)\n"),
    "css": ("styles/panel.css",
            ".a { color: #ff0000; padding: 8px; }\n.b { color: var(--text); }\n",
            ".c { color: #00ff00; }\n"),
    "tsx": ("src/Card.tsx",
            "export const A = () => <div style={{ color: 'red' }} />;\n",
            "export const B = () => <div style={{ margin: 4 }} />;\n"),
}


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(ENGINE), "--root", str(root), *args],
                          capture_output=True, text=True)


class RatchetCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".devex").mkdir()
        (self.root / ".devex/ratchet.config.json").write_text(json.dumps(CONFIG))
        for rel, body, _ in STACKS.values():
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text(body)
        first = run(self.root, "--update-baseline")
        self.assertEqual(first.returncode, 0, first.stderr)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def baseline(self) -> dict:
        return json.loads((self.root / ".devex/ratchet.baseline.json").read_text())["counts"]


class RatchetBites(RatchetCase):
    def test_clean_tree_passes(self) -> None:
        result = run(self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS ratchet", result.stdout)

    def test_rise_fails_with_file_and_line_for_each_stack(self) -> None:
        for stack, (rel, body, extra) in STACKS.items():
            with self.subTest(stack=stack):
                path = self.root / rel
                path.write_text(body + extra)
                result = run(self.root)
                path.write_text(body)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(rel + ":", result.stderr)
                self.assertIn("count rose", result.stderr)

    def test_fall_passes_and_update_lowers_the_baseline(self) -> None:
        rel = STACKS["swift"][0]
        (self.root / rel).write_text("let b = Color.accentColor\n")
        self.assertEqual(run(self.root).returncode, 0)
        self.assertEqual(run(self.root, "--update-baseline").returncode, 0)
        self.assertNotIn(rel, self.baseline().get("swift-literal-colour", {}))
        # the ratchet is now tighter: the old literal is a new pair and fails
        (self.root / rel).write_text(STACKS["swift"][1])
        self.assertEqual(run(self.root).returncode, 1)

    def test_new_file_with_literal_is_a_new_pair(self) -> None:
        (self.root / "Views/Other.swift").write_text("let x = Color(red: 1, green: 1, blue: 1)\n")
        result = run(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("new literal in file", result.stderr)

    def test_update_baseline_refuses_to_raise(self) -> None:
        rel, body, extra = STACKS["css"]
        before = (self.root / ".devex/ratchet.baseline.json").read_text()
        (self.root / rel).write_text(body + extra)
        result = run(self.root, "--update-baseline")
        self.assertEqual(result.returncode, 2)
        self.assertIn("REFUSED", result.stderr)
        self.assertEqual((self.root / ".devex/ratchet.baseline.json").read_text(), before)

    def test_update_baseline_refuses_a_new_pair(self) -> None:
        (self.root / "src/New.tsx").write_text("const x = <i style={{ top: 1 }} />;\n")
        self.assertEqual(run(self.root, "--update-baseline").returncode, 2)

    def test_exempt_token_file_is_ignored(self) -> None:
        tokens = self.root / "Sources/DesignTokens.swift"
        tokens.parent.mkdir()
        tokens.write_text("let red = Color(red: 1, green: 0, blue: 0)\n" * 5)
        self.assertEqual(run(self.root).returncode, 0)

    def test_files_flag_checks_only_named_files(self) -> None:
        rel, body, extra = STACKS["css"]
        (self.root / rel).write_text(body + extra)
        swift_only = run(self.root, "--files", STACKS["swift"][0])
        self.assertEqual(swift_only.returncode, 0)
        css = run(self.root, "--files", str(self.root / rel))
        self.assertEqual(css.returncode, 1)
        outside = run(self.root, "--files", "/etc/hosts")
        self.assertEqual(outside.returncode, 0)

    def test_json_output_is_parseable(self) -> None:
        rel, body, extra = STACKS["tsx"]
        (self.root / rel).write_text(body + extra)
        result = run(self.root, "--json")
        data = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(data["status"], "regression")
        self.assertEqual(data["regressions"][0]["file"], rel)
        self.assertEqual(data["exit"], 1)

    def test_bad_config_and_missing_baseline_exit_2(self) -> None:
        (self.root / ".devex/ratchet.config.json").write_text("{not json")
        self.assertEqual(run(self.root).returncode, 2)
        (self.root / ".devex/ratchet.config.json").write_text(json.dumps(CONFIG))
        (self.root / ".devex/ratchet.baseline.json").unlink()
        self.assertEqual(run(self.root).returncode, 2)

    def test_check_is_deterministic(self) -> None:
        rel, body, extra = STACKS["swift"]
        (self.root / rel).write_text(body + extra)
        self.assertEqual(run(self.root, "--json").stdout, run(self.root, "--json").stdout)


if __name__ == "__main__":
    unittest.main()
