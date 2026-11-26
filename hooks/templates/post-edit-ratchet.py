#!/usr/bin/env python3
"""post-edit-ratchet: after an edit, run the literal ratchet on that file; block on regression.

Why it exists: the ratchet is cheapest when it fails at the edit that caused the regression,
with file:line, not at CI. PostToolUse hook; reads the payload on stdin and runs
`literal-ratchet.py --files <edited file>` (the copy installed beside this hook, or the path
in $DEVEX_RATCHET), against the checkout that owns the edited path (its config and baseline),
not the session `cwd`. On regression it prints `{"decision": "block", "reason": ...}`. It never
returns `ask`. No config, no baseline, a missing engine or malformed JSON all allow silently.

The one edge that bites: it checks only the edited file, so a baseline built from a dirty
tree can hide old debt; build the baseline with `--update-baseline` on a clean checkout.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
CONFIG = os.path.join(".devex", "ratchet.config.json")


def owner_root(path: str, cwd: str) -> str:
    """Git toplevel that owns `path`; `cwd` when the path is in no checkout (or git fails)."""
    absolute = os.path.normpath(path if os.path.isabs(path) else os.path.join(cwd, path))
    directory = os.path.dirname(absolute)
    while directory and not os.path.isdir(directory):
        parent = os.path.dirname(directory)
        if parent == directory:
            return cwd
        directory = parent
    try:
        out = subprocess.run(["git", "-C", directory, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=10, check=True)
    except (OSError, subprocess.SubprocessError):
        return cwd
    return os.path.realpath(out.stdout.strip()) if out.stdout.strip() else cwd


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            return 0
    except (ValueError, OSError):
        return 0
    tool_input = payload.get("tool_input")
    if payload.get("tool_name") not in EDIT_TOOLS or not isinstance(tool_input, dict):
        return 0
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(path, str):
        return 0
    session_cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else os.getcwd()
    path = os.path.normpath(path if os.path.isabs(path) else os.path.join(session_cwd, path))
    cwd = owner_root(path, session_cwd)
    if not os.path.isfile(os.path.join(cwd, CONFIG)):
        return 0
    engine = os.environ.get("DEVEX_RATCHET") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "literal-ratchet.py")
    if not os.path.isfile(engine):
        return 0
    try:
        result = subprocess.run(
            [sys.executable, engine, "--root", cwd, "--files", path],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return 0
    if result.returncode == 1:
        report = (result.stderr or result.stdout).strip()
        print(json.dumps({"decision": "block",
                          "reason": "literal ratchet regression after this edit; replace the "
                                    "literal with a token (do not raise the baseline):\n" + report}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
