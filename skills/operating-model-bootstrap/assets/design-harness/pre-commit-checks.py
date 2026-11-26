#!/usr/bin/env python3
"""pre-commit-checks: run the adopted harness guards on the staged change.

Why it exists: the Claude hooks do not run for Codex, Gemini or a human at a terminal. The
git pre-commit is the path every writer shares. This script is what `install-precommit.py`
wires in; it runs from the checkout being committed (`git rev-parse --show-toplevel`), so it
is right in every linked worktree and uses that branch's own copy of each guard.

Runs, when the file exists beside this one: `records-guard.py --staged`,
`config-guard.py --staged`, and `literal-ratchet.py --files <staged files>` when
`.devex/ratchet.config.json` exists. Exit 1 if any fails. `HARNESS_SKIP=1` skips all
(the audited override); `git commit --no-verify` skips the whole hook.
The one edge that bites: a guard missing on this branch is skipped, not failed, so a branch
cut before the harness landed still commits; the PR gate is what proves the harness is there.
"""

from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def git(root: str, *args: str) -> str:
    out = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                         timeout=60, check=True)
    return out.stdout


def run(script: str, *args: str, cwd: str) -> int:
    path = os.path.join(HERE, script)
    if not os.path.isfile(path):
        return 0
    return subprocess.run([sys.executable, path, *args], cwd=cwd).returncode


def main() -> int:
    if os.environ.get("HARNESS_SKIP") == "1":
        return 0
    try:
        root = git(os.getcwd(), "rev-parse", "--show-toplevel").strip()
    except (OSError, subprocess.SubprocessError):
        return 0
    failed = False
    for guard in ("records-guard.py", "config-guard.py"):
        if run(guard, "--staged", cwd=root) != 0:
            failed = True
    if os.path.isfile(os.path.join(root, ".devex", "ratchet.config.json")):
        try:
            staged = [f for f in git(root, "diff", "--cached", "--name-only",
                                     "--diff-filter=ACM").splitlines() if f]
        except (OSError, subprocess.SubprocessError):
            staged = []
        if staged and run("literal-ratchet.py", "--root", root, "--files", *staged, cwd=root) != 0:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
