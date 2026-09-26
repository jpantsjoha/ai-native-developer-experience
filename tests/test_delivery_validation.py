"""CLI refusal fixtures for offline delivery records; no provider or network calls."""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


VALIDATOR = Path(__file__).resolve().parents[1] / "scripts/validate_delivery.py"


class DeliveryValidationTests(unittest.TestCase):
    """Plant defects in disposable records and inspect the real CLI result."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.policy = {
            "version": 1,
            "documents": {role: f"{role}.md" for role in
                          ("vision", "roadmap", "status", "changelog")},
            "records": {kind: kind for kind in ("spec", "decision", "epic", "task")},
        }
        for role in self.policy["documents"]:
            self.put(f"{role}.md", f"# {role}\n")
        self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Accepted\n")
        self.put("decision/decision.md", "# ADR-001: Decision\n\n## Status\n\nAccepted — 2026-09-26\n")
        self.put("epic/epic.md", "**Epic ID:** EP-001\n**Status:** In progress\n")
        self.put("task/task.md", "**Task ID:** TASK-001\n**Status:** Ready\n**Parent:** EP-001\n**Depends on:** REQ-001, ADR-001\n")
        self.save_policy()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def put(self, name: str, text: str) -> None:
        """Write a fixture; parent directories are owned by the temporary root."""
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def save_policy(self) -> None:
        """Persist the current test policy."""
        self.put(".delivery.json", json.dumps(self.policy))

    def run_gate(self, expected: int = 0, code: str = "") -> dict:
        """Require structured findings and an intentional exit, never a crash."""
        result = subprocess.run([sys.executable, str(VALIDATOR), "--root", str(self.root),
                                 "--json"], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "PASS" if expected == 0 else "FAIL")
        if code:
            self.assertIn(code, {f["code"] for f in payload["findings"]}, payload)
        return payload

    def test_valid_records(self) -> None:
        self.assertEqual(self.run_gate()["records_checked"], 4)

    def test_missing_required_document(self) -> None:
        (self.root / "vision.md").unlink()
        self.run_gate(1, "FILE")

    def test_empty_required_document(self) -> None:
        self.put("vision.md", " \n")
        self.run_gate(1, "EMPTY")

    def test_missing_and_empty_record_roots(self) -> None:
        (self.root / "task/task.md").unlink()
        self.run_gate(1, "INVENTORY")
        (self.root / "task").rmdir()
        self.run_gate(1, "INVENTORY")

    def test_policy_cannot_disable_inventory(self) -> None:
        for key in ("documents", "records"):
            with self.subTest(key=key):
                before = self.policy[key]
                self.policy[key] = {}
                self.save_policy()
                self.run_gate(1, "POLICY")
                self.policy[key] = before

    def test_malformed_policy_and_types(self) -> None:
        for text in ('{', '[]', '{"version":1,"version":1}',
                     json.dumps({**self.policy, "version": True}),
                     json.dumps({**self.policy, "records": {"spec": []}}),
                     json.dumps({**self.policy, "surprise": True})):
            with self.subTest(text=text):
                self.put(".delivery.json", text)
                self.run_gate(1, "POLICY")

    def test_policy_path_escape_and_symlink(self) -> None:
        for value in ("../outside.md", "/tmp/outside.md", "C:\\outside.md"):
            with self.subTest(value=value):
                self.policy["documents"]["vision"] = value
                self.save_policy()
                self.run_gate(1, "PATH")
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "outside.md"
            target.write_text("# External", encoding="utf-8")
            (self.root / "outside.md").symlink_to(target)
            self.policy["documents"]["vision"] = "outside.md"
            self.save_policy()
            self.run_gate(1, "PATH")

    def test_missing_invalid_and_duplicate_id(self) -> None:
        for content, code in (("**Status:** Accepted\n", "ID"),
                              ("**Spec ID:** garbage\n**Status:** Accepted\n", "ID"),
                              ("**Spec ID:** EP-001\n**Status:** Accepted\n", "DUPLICATE_ID")):
            self.put("spec/spec.md", content)
            self.run_gate(1, code)

    def test_invalid_or_ambiguous_state(self) -> None:
        for state in ("Magic", "Accepted\n**Status:** Done", "Accepted **Status:** Done"):
            self.put("spec/spec.md", f"**Spec ID:** REQ-001\n**Status:** {state}\n")
            self.run_gate(1, "STATUS")

    def test_examples_cannot_supply_metadata(self) -> None:
        for example in ("```md\n**Status:** Accepted\n```", "~~~\n**Status:** Accepted\n~~~",
                        "<!--\n**Status:** Accepted\n-->", "`**Status:** Accepted`",
                        "    **Status:** Accepted"):
            self.put("spec/spec.md", "**Spec ID:** REQ-001\n" + example + "\n")
            self.run_gate(1, "STATUS")

    def test_examples_cannot_override_real_metadata(self) -> None:
        self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Accepted\n"
                 "```\n**Status:** Bad\n[bad](missing.md)\n```\n"
                 "<!-- **Status:** Bad -->\n`[bad](missing.md)`\n")
        self.run_gate()

    def test_fence_in_comment_cannot_hide_duplicate_status(self) -> None:
        self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Accepted\n"
                 "<!--\n```\n-->\n**Status:** Done\n")
        self.run_gate(1, "STATUS")

    def test_inline_comment_literal_cannot_hide_later_defects(self) -> None:
        for suffix, code in (("**Status:** Garbage", "STATUS"), ("[receipt](missing.md)", "LINK")):
            self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Accepted\n\n"
                     "The token is `<!--`.\n\n" + suffix + "\n")
            self.run_gate(1, code)

    def test_unmatched_backticks_cannot_hide_duplicate_status(self) -> None:
        for closer in ("``", "`"):
            self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Accepted\n\n"
                     "`unmatched opener\n\n**Status:** Garbage\n\nending " + closer + " delimiter.\n")
            self.run_gate(1, "STATUS")

    def test_code_span_cannot_cross_a_heading(self) -> None:
        self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Accepted\n\n"
                 "`unmatched opener\n## New section\n**Status:** Garbage\nending ` delimiter.\n")
        self.run_gate(1, "STATUS")

    def test_code_span_cannot_cross_setext_or_thematic_breaks(self) -> None:
        for separator in ("---", "===", "***", "___", " - - - ", "  * * *", " _ _ _ "):
            with self.subTest(separator=separator):
                self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Accepted\n\n"
                         "`unmatched opener\n" + separator + "\n**Status:** Garbage\nending ` delimiter.\n")
                self.run_gate(1, "STATUS")

    def test_multiline_code_span_requires_fenced_example(self) -> None:
        self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Accepted\n\n"
                 "Example ``one ` tick\n**Status:** Garbage\n<!-- `` end of example.\n")
        self.run_gate(1, "GRAMMAR")

    def test_empty_heading_and_html_cannot_hide_status(self) -> None:
        for boundary in ("#", "######", "<hr>", "<div>"):
            self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Accepted\n\n"
                     "`unmatched opener\n" + boundary + "\n**Status:** Garbage\nending ` delimiter.\n")
            self.run_gate(1, "GRAMMAR")

    def test_unmatched_literal_backtick_requires_escape(self) -> None:
        self.put("vision.md", "# Vision\nUse a literal ` character.\n")
        self.run_gate(1, "GRAMMAR")
        self.put("vision.md", "# Vision\nUse an escaped literal \\` character.\n")
        self.run_gate()

    def test_bad_parent(self) -> None:
        for parent in ("", "**Parent:** EP-999\n", "**Parent:** REQ-001\n"):
            self.put("task/task.md", "**Task ID:** TASK-001\n**Status:** Ready\n" + parent)
            self.run_gate(1, "PARENT")

    def test_missing_dependency_and_cycle(self) -> None:
        self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Accepted\n**Depends on:** BAD-999\n")
        self.run_gate(1, "DEPENDENCY")
        self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Accepted\n**Depends on:** TASK-001\n")
        self.run_gate(1, "CYCLE")

    def test_supersession_requires_same_kind_target(self) -> None:
        for target in ("", "**Superseded by:** ADR-001\n", "**Superseded by:** REQ-999\n"):
            self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Superseded\n" + target)
            self.run_gate(1, "SUPERSESSION")

    def test_supersession_cycle_refuses(self) -> None:
        self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Superseded\n**Superseded by:** REQ-002\n")
        self.put("spec/next.md", "**Spec ID:** REQ-002\n**Status:** Superseded\n**Superseded by:** REQ-001\n")
        self.run_gate(1, "SUPERSESSION")

    def test_supersession_forward_link_passes(self) -> None:
        self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Superseded\n**Superseded by:** REQ-002\n")
        self.put("spec/next.md", "**Spec ID:** REQ-002\n**Status:** Accepted\n")
        self.run_gate()

    def test_done_needs_local_nonempty_evidence(self) -> None:
        for evidence in ("", "**Evidence:** https://example.invalid\n",
                         "**Evidence:** [receipt](../empty.txt)\n"):
            self.put("empty.txt", "")
            self.put("task/task.md", "**Task ID:** TASK-001\n**Status:** Done\n**Parent:** EP-001\n" + evidence)
            self.run_gate(1, "EVIDENCE")
        self.put("receipt.txt", "Synthetic result, not authenticated proof\n")
        self.put("task/task.md", "**Task ID:** TASK-001\n**Status:** Done\n**Parent:** EP-001\n**Evidence:** [receipt](../receipt.txt)\n")
        self.run_gate()

    def test_broken_inline_and_reference_links(self) -> None:
        for link in ("[x](missing.md)", "[x][ref]\n\n[ref]: missing.md", "[ref][]\n\n[ref]: missing.md",
                     "[ref]\n\n[ref]: missing.md", "[x][unknown]"):
            self.put("vision.md", "# Vision\n" + link + "\n")
            self.run_gate(1, "LINK")

    def test_unmatched_prose_bracket_cannot_hide_later_link(self) -> None:
        self.put("vision.md", "# Vision\nAn unmatched [ is prose.\n\n[broken](missing.md)\n")
        self.run_gate(1, "LINK")

    def test_unmatched_prose_bracket_with_valid_link_passes(self) -> None:
        self.put("vision.md", "# Vision\nAn unmatched [ is prose.\n\n[valid](roadmap.md)\n")
        self.run_gate()

    def test_prose_bracket_group_cannot_hide_nested_link(self) -> None:
        self.put("vision.md", "# Vision\n[Some prose\n\n[broken](missing.md)\n\nMore prose]\n")
        self.run_gate(1, "LINK")
        self.put("vision.md", "# Vision\n[Some prose\n\n[valid](roadmap.md)\n\nMore prose]\n")
        self.run_gate()

    def test_image_inside_link_checks_both_destinations(self) -> None:
        self.put("vision.md", "# Vision\n[![image](missing.md)](roadmap.md)\n")
        self.run_gate(1, "LINK")
        self.put("vision.md", "# Vision\n[![image](status.md)](missing.md)\n")
        self.run_gate(1, "LINK")
        self.put("vision.md", "# Vision\n[![image](status.md)](roadmap.md)\n")
        self.run_gate()

    def test_valid_link_variants_and_offline_urls(self) -> None:
        self.put("a (b).md", "# Sample\n")
        self.put("vision.md", '# Vision\n[x](<a (b).md>)\n[x](a%20(b).md "Title")\n'
                 '[x](https://does-not-exist.invalid/path)\n[x](#unchecked-heading)\n'
                 '[ref][]\n[ref]: roadmap.md\n![image](status.md)\n')
        self.run_gate()

    def test_quoted_link_titles_do_not_affect_destination_depth(self) -> None:
        self.put("vision.md", '# Vision\n[x](roadmap.md "Version (draft")\n'
                 "[x](status.md 'Closing ) draft')\n")
        self.run_gate()

    def test_link_cannot_escape_root(self) -> None:
        self.put("vision.md", "# Vision\n[x](%2e%2e/outside.md)\n")
        self.run_gate(1, "PATH")

    def test_evidence_symlink_escape_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "receipt.txt"
            target.write_text("A receipt outside the repository", encoding="utf-8")
            (self.root / "receipt.txt").symlink_to(target)
            self.put("task/task.md", "**Task ID:** TASK-001\n**Status:** Done\n**Parent:** EP-001\n**Evidence:** [receipt](../receipt.txt)\n")
            self.run_gate(1, "EVIDENCE")

    def test_record_symlink_escape_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "spec.md"
            target.write_text("**Spec ID:** REQ-002\n**Status:** Accepted\n", encoding="utf-8")
            (self.root / "spec/escape.md").symlink_to(target)
            self.run_gate(1, "PATH")

    def test_symlinked_record_directory_refuses(self) -> None:
        (self.root / "spec/linked").symlink_to(self.root / "task", target_is_directory=True)
        self.run_gate(1, "INVENTORY")

    def test_scan_error_never_returns_pass(self) -> None:
        spec = importlib.util.spec_from_file_location("delivery_gate_fixture", VALIDATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        def denied(*args, **kwargs):
            kwargs["onerror"](PermissionError("synthetic scan denial"))

        with patch.object(module.os, "walk", side_effect=denied):
            with self.assertRaises(PermissionError):
                module.Gate(self.root).run(".delivery.json")

    def test_make_planning_rejects_planted_invalid_state(self) -> None:
        self.put("Makefile", (VALIDATOR.parent.parent / "Makefile").read_text(encoding="utf-8"))
        self.put("scripts/validate_delivery.py", VALIDATOR.read_text(encoding="utf-8"))
        self.put("spec/spec.md", "**Spec ID:** REQ-001\n**Status:** Pretend complete\n")
        result = subprocess.run(["make", "planning", f"PYTHON={sys.executable}"], cwd=self.root,
                                capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL STATUS", result.stderr)

    def test_record_discovery_and_overlapping_roots(self) -> None:
        self.put("spec/new.md", "**Spec ID:** REQ-001\n**Status:** Draft\n")
        self.run_gate(1, "DUPLICATE_ID")
        (self.root / "spec/new.md").unlink()
        self.policy["records"]["epic"] = "spec"
        self.save_policy()
        self.run_gate(1, "INVENTORY")

    def test_unreadable_encoding_is_a_finding(self) -> None:
        (self.root / "vision.md").write_bytes(b"\xff")
        self.run_gate(1, "FILE")


if __name__ == "__main__":
    unittest.main()
