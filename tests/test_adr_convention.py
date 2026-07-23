"""Enforces the ADR lifecycle convention (see ADR/ADR-0001-*).

A decision's state is encoded redundantly — in the filename postfix (`-DRAFT` /
`-approved`) and in the in-file frontmatter `status:` field. Redundancy is only safe if
the two are kept in agreement; this test is the mechanism that keeps the redundancy from
drifting into a lie.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ADR_DIR = REPO_ROOT / "ADR"

POSTFIX_TO_STATUS = {"DRAFT": "draft", "approved": "approved"}
VALID_STATUSES = {"draft", "approved", "superseded"}
FILENAME_RE = re.compile(r"^ADR-(\d{4})-[a-z0-9-]+-(DRAFT|approved)\.md$")
STATUS_RE = re.compile(r"^status:\s*(\S+)\s*$", re.MULTILINE)


def adr_files() -> list[Path]:
    if not ADR_DIR.is_dir():
        return []
    return sorted(p for p in ADR_DIR.glob("*.md"))


class TestAdrConvention(unittest.TestCase):
    def test_filenames_match_convention(self) -> None:
        for path in adr_files():
            with self.subTest(adr=path.name):
                self.assertRegex(
                    path.name,
                    FILENAME_RE,
                    f"{path.name} does not match ADR-NNNN-<slug>-(DRAFT|approved).md",
                )

    def test_filename_postfix_and_status_field_agree(self) -> None:
        for path in adr_files():
            match = FILENAME_RE.match(path.name)
            if match is None:
                continue  # covered by test_filenames_match_convention
            with self.subTest(adr=path.name):
                postfix = match.group(2)
                text = path.read_text(encoding="utf-8")
                status_match = STATUS_RE.search(text)
                self.assertIsNotNone(
                    status_match, f"{path.name} has no `status:` frontmatter field"
                )
                status = status_match.group(1)
                self.assertIn(
                    status, VALID_STATUSES, f"{path.name} has invalid status {status!r}"
                )
                self.assertEqual(
                    status,
                    POSTFIX_TO_STATUS[postfix],
                    f"{path.name}: filename postfix '{postfix}' disagrees with "
                    f"status: {status!r}",
                )


if __name__ == "__main__":
    unittest.main()
