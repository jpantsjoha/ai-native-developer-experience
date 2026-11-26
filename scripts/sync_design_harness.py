#!/usr/bin/env python3
"""Refresh the bootstrap skill's design-harness mirrors from their canonical sources.

Why it exists: a skill-only install ships only `skills/`, so the opt-in hook templates and
the ratchet engine must also sit inside `operating-model-bootstrap/assets/design-harness/`.
The canonical files are `hooks/templates/*` and `scripts/literal_ratchet.py`; a test fails
when a mirror differs. Run with --check to verify without writing.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIRROR = ROOT / "skills" / "operating-model-bootstrap" / "assets" / "design-harness"
SOURCES = {
    "records-guard.py": ROOT / "hooks/templates/records-guard.py",
    "ui-context.py": ROOT / "hooks/templates/ui-context.py",
    "post-edit-ratchet.py": ROOT / "hooks/templates/post-edit-ratchet.py",
    "ratchet.config.example.json": ROOT / "hooks/templates/ratchet.config.example.json",
    "literal-ratchet.py": ROOT / "scripts/literal_ratchet.py",
    "bashwrites.py": ROOT / "hooks/templates/bashwrites.py",
    "config-guard.py": ROOT / "hooks/templates/config-guard.py",
    "pre-commit-checks.py": ROOT / "hooks/templates/pre-commit-checks.py",
    "install-precommit.py": ROOT / "hooks/templates/install-precommit.py",
    "harness.mk": ROOT / "hooks/templates/harness.mk",
    "registration-audit.py": ROOT / "scripts/registration_audit.py",
    "gate-log.py": ROOT / "scripts/gate_log.py",
}


def drifted() -> list[str]:
    return [name for name, src in SOURCES.items()
            if not (MIRROR / name).is_file() or (MIRROR / name).read_bytes() != src.read_bytes()]


def main() -> int:
    stale = drifted()
    if "--check" in sys.argv[1:]:
        for name in stale:
            print(f"DRIFT: {name} differs from its canonical source", file=sys.stderr)
        return 1 if stale else 0
    MIRROR.mkdir(parents=True, exist_ok=True)
    for name in stale:
        shutil.copy2(SOURCES[name], MIRROR / name)
        print(f"synced: {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
