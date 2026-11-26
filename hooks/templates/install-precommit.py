#!/usr/bin/env python3
"""install-precommit: put the harness pre-commit into THIS clone's own hooks directory.

Why it exists: a repository needs a git pre-commit that runs the harness guards for every
writer, in every linked worktree, without touching anything outside the clone.

  install-precommit.py [--root DIR] [--dry-run]

What it writes: `<git-common-dir>/hooks/pre-commit`, one dispatcher shared by the clone and
its linked worktrees. The dispatcher resolves the harness at COMMIT time
(`git rev-parse --show-toplevel`, then `.devex/hooks/pre-commit-checks.py`), so it never
bakes the path of the checkout it was installed from: remove that worktree and every commit
still works. When the script is absent on a branch it prints a note and exits 0 after the
chained hook has run. An existing hook of another origin is kept as `pre-commit.pre-harness`
and run first; if that name is taken the installer refuses and changes nothing.

hooksPath chain contract. The hooks directory is `<git-common-dir>/hooks`, resolved from
`git rev-parse --git-common-dir`; it is NOT `git rev-parse --git-path hooks`, which follows
`core.hooksPath` (a global one would send the write outside the clone). The installer
refuses when that directory resolves outside the git common dir, and it never writes to
`core.hooksPath`, local or global. When `core.hooksPath` is set, git ignores the clone's hooks
directory, so the installer prints the one line the global dispatcher must run:
`"$(git rev-parse --git-common-dir)/hooks/pre-commit"` (not `.git/hooks/pre-commit`, which
does not exist in a linked worktree).
The one edge that bites: with `core.hooksPath` set and a dispatcher that does not chain, the
hook is installed and silent; run `--dry-run` (it reports `hooksPath`) and read the note.
Python 3 standard library only.
"""

from __future__ import annotations

import argparse
import os
import stat
import subprocess
import sys

MARKER = "# devex-charter harness pre-commit"
DISPATCHER = f"""#!/bin/sh
{MARKER}
# Runs the chained hook first, then this checkout's .devex/hooks/pre-commit-checks.py.
hooks="$(cd "$(dirname "$0")" && pwd)"
chain="$hooks/pre-commit.pre-harness"
if [ -x "$chain" ]; then "$chain" "$@" || exit $?; fi
root="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
checks="$root/.devex/hooks/pre-commit-checks.py"
if [ -f "$checks" ]; then exec python3 "$checks" "$@"; fi
echo "devex harness: .devex/hooks/pre-commit-checks.py absent in this checkout; skipped" >&2
exit 0
"""


def git(root: str, *args: str) -> str:
    out = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                         timeout=30, check=True)
    return out.stdout.strip()


def plan(root: str) -> tuple[str, list[str], list[str]]:
    """(hooks dir, actions, notes); raises ValueError when the install must refuse."""
    top = git(root, "rev-parse", "--show-toplevel")
    common = git(top, "rev-parse", "--git-common-dir")
    common = os.path.realpath(common if os.path.isabs(common) else os.path.join(top, common))
    hooks = os.path.join(common, "hooks")
    real = os.path.realpath(hooks)
    if real != hooks and not real.startswith(common + os.sep):
        raise ValueError(f"{hooks} resolves outside the clone's git directory ({real}); refusing")
    target = os.path.join(hooks, "pre-commit")
    chain = os.path.join(hooks, "pre-commit.pre-harness")
    actions, notes = [], []
    if os.path.lexists(target):
        with open(target, encoding="utf-8", errors="replace") as handle:
            ours = MARKER in handle.read()
        if not ours:
            if os.path.lexists(chain):
                raise ValueError(f"{target} is not ours and {chain} already exists; "
                                 "resolve by hand, nothing changed")
            actions.append(f"keep existing {target} as {chain} and chain it")
    actions.append(f"write {target}")
    hooks_path = subprocess.run(["git", "-C", top, "config", "--get", "core.hooksPath"],
                                capture_output=True, text=True).stdout.strip()
    if hooks_path:
        notes.append(f"core.hooksPath is set ({hooks_path}): git ignores {hooks}; the dispatcher "
                     f"there must run \"$(git rev-parse --git-common-dir)/hooks/pre-commit\"")
    return hooks, actions, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        hooks, actions, notes = plan(os.path.abspath(args.root))
    except (OSError, subprocess.SubprocessError):
        print("ERROR not a git repository", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    prefix = "would " if args.dry_run else ""
    for action in actions:
        print(f"{prefix}{action}")
    for note in notes:
        print(f"note: {note}", file=sys.stderr)
    if args.dry_run:
        return 0
    target = os.path.join(hooks, "pre-commit")
    chain = os.path.join(hooks, "pre-commit.pre-harness")
    os.makedirs(hooks, exist_ok=True)
    if os.path.lexists(target):
        with open(target, encoding="utf-8", errors="replace") as handle:
            ours = MARKER in handle.read()
        if not ours:
            os.rename(target, chain)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(DISPATCHER)
    os.chmod(target, os.stat(target).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"installed {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
