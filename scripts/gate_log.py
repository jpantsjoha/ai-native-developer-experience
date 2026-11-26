#!/usr/bin/env python3
"""gate-log: print a log path for a gate run that is keyed by worktree and commit.

Why it exists: two worktrees of one repository that both write `$TMPDIR/gate.log` overwrite
each other, and a reader then trusts the other lane's result. This prints
`$TMPDIR/<name>-<hash of the worktree path>-<short sha>.log`: stable inside one worktree at
one commit, different across worktrees and across commits.

  gate_log.py [--name NAME] [--root DIR] [--sha SHA]

`--name` defaults to `gate`, `--root` to the current directory (its git toplevel is hashed),
`--sha` to `git rev-parse --short HEAD`, or `nogit` outside a repository. Use it in a
Makefile as `LOG := $(shell python3 .devex/tools/gate-log.py --name check)` and read the
same path back from the check that proves the gate ran.
The one edge that bites: an uncommitted edit does not change the sha; treat the log as
evidence for the commit, not for a dirty tree. Python 3 standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile


def git(root: str, *args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                             timeout=15, check=True)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def log_path(name: str, root: str, sha: str | None = None) -> str:
    top = git(root, "rev-parse", "--show-toplevel") or root
    key = hashlib.sha256(os.path.realpath(top).encode()).hexdigest()[:10]
    short = sha or git(root, "rev-parse", "--short", "HEAD") or "nogit"
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
    return os.path.join(tempfile.gettempdir(), f"{safe}-{key}-{short}.log")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--name", default="gate")
    parser.add_argument("--root", default=".")
    parser.add_argument("--sha")
    args = parser.parse_args(argv)
    print(log_path(args.name, os.path.abspath(args.root), args.sha))
    return 0


if __name__ == "__main__":
    sys.exit(main())
