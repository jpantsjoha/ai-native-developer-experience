#!/usr/bin/env python3
"""records-guard: protected delivery records are editable only on a records branch.

Why it exists: "only the records task edits ROADMAP / STATUS / CHANGELOG" is otherwise
checked after the fact. This hook denies the edit up front.

Modes
  PreToolUse payload (default): reads the hook JSON on stdin. Denies Edit/Write/MultiEdit/
    NotebookEdit on a protected path, and Bash commands that write to one, unless the current
    branch matches a records pattern. Allow = exit 0 and no output; deny = a PreToolUse
    `permissionDecision: deny`. It never returns `ask` (an `ask` forces a prompt even in
    bypass mode). Malformed JSON, no git repo or an unreadable config all allow.
  --staged: pre-commit mode. Exit 1 listing staged protected files when not on a records
    branch; exit 0 otherwise.
  --config PATH: read the protected list and branch patterns from PATH (relative to the
    checkout) instead of `.devex/records-guard.json`, so a sibling guard (for example one that
    protects harness config) reuses this engine unchanged. `config-guard.py` is that sibling.

Which checkout judges an edit. The edited path's own checkout does, not the session's `cwd`:
an Edit/Write is resolved from its absolute `file_path`, a Bash command from the paths
`bashwrites.py` (beside this file) says it writes, each against the git toplevel that owns
that path; config and branch come from that checkout. A path in no git checkout falls back to
`cwd`.

Config (optional) `.devex/records-guard.json`:
  {"protected": ["docs/ROADMAP.md", "docs/STATUS.md", "CHANGELOG.md"],
   "branch_patterns": ["records/*", "records-*"]}
Bash writes are resolved statically: `cd`, `git -C`, globs, variables, `bash -c` and
interpreter one-liners are followed (see bashwrites.py); if that module is absent the old
text heuristic (a protected name plus a write indicator) is the only check, and it is
used only when that module is absent, so a resolved write is judged solely by its owning checkout. Stderr and /dev/null redirections (`2>&1`, `>/dev/null`) are not
treated as writes. The one edge that bites: names built at run time from input are not
resolved; keep --staged in pre-commit as the backstop.
"""

from __future__ import annotations

import fnmatch
import importlib.util
import json
import os
import re
import subprocess
import sys

DEFAULT_PROTECTED = ["ROADMAP.md", "STATUS.md", "CHANGELOG.md",
                     "docs/ROADMAP.md", "docs/STATUS.md"]
DEFAULT_BRANCHES = ["records/*", "records-*"]
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
WRITE_HINTS = re.compile(
    r"(>>?|\btee\b|\bsed\s+(?:-[a-zA-Z]*i|--in-place)|\bperl\s+-[a-zA-Z]*i|\bmv\b|\bcp\b"
    r"|\brm\b|\btruncate\b|\bdd\b|\bpython[0-9.]*\b.*\bwrite|\bgit\s+(?:checkout|restore)\b)"
)


# Sibling guards (config-guard.py) set these before calling main(): the config file and the
# defaults used when it is missing, and globs that stay protected whatever the file says.
SETTINGS = {
    "config": os.path.join(".devex", "records-guard.json"),
    "protected": DEFAULT_PROTECTED,
    "branches": DEFAULT_BRANCHES,
    "always": [],
    "label": "records-guard",
    "noun": "delivery record",
    "branch_noun": "a records branch",
    "advice": "Note the record change in the PR body.",
}


def load_config(cwd: str) -> tuple[list[str], list[str]]:
    config = SETTINGS["config"]
    path = config if os.path.isabs(config) else os.path.join(cwd, config)
    protected, branches = list(SETTINGS["protected"]), list(SETTINGS["branches"])
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        protected = [str(p) for p in data.get("protected", protected)]
        branches = [str(b) for b in data.get("branch_patterns", branches)]
    except (OSError, ValueError, AttributeError, TypeError):
        pass
    protected += [p for p in SETTINGS["always"] if p not in protected]
    return protected, branches


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


def resolved_writes(command: str, cwd: str) -> list[str] | None:
    """Absolute paths `command` writes, via bashwrites.py beside this file; None if unavailable."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bashwrites.py")
    try:
        spec = importlib.util.spec_from_file_location("devex_bashwrites", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return list(module.writes(command, cwd))
    except Exception:  # absent or broken resolver: the text heuristic is the fallback
        return None


def current_branch(cwd: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
                             capture_output=True, text=True, timeout=10, check=True)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        pass
    try:  # unborn branch: rev-parse fails with no commits, symbolic-ref still names it
        out = subprocess.run(["git", "-C", cwd, "symbolic-ref", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=10, check=True)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def on_records_branch(branch: str | None, patterns: list[str]) -> bool:
    return branch is not None and any(fnmatch.fnmatch(branch, p) for p in patterns)


def is_protected(path: str, cwd: str, protected: list[str]) -> bool:
    absolute = path if os.path.isabs(path) else os.path.join(cwd, path)
    rel = os.path.relpath(os.path.realpath(absolute), os.path.realpath(cwd))
    rel = rel.replace(os.sep, "/")
    return any(rel == p or fnmatch.fnmatch(rel, p) for p in protected)


NOISE_REDIRECTS = re.compile(r"(?:&>|\d*>>?)\s*/dev/(?:null|stderr|stdout)|\d*>&\d+")


def command_writes_protected(command: str, protected: list[str]) -> str | None:
    command_for_hints = NOISE_REDIRECTS.sub(" ", command)
    for target in protected:
        if target in command and WRITE_HINTS.search(command_for_hints):
            return target
    return None


def deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


def staged_mode(cwd: str) -> int:
    protected, branches = load_config(cwd)
    try:
        out = subprocess.run(["git", "-C", cwd, "diff", "--cached", "--name-only"],
                             capture_output=True, text=True, timeout=30, check=True)
    except (OSError, subprocess.SubprocessError):
        return 0
    hits = [f for f in out.stdout.splitlines() if is_protected(f, cwd, protected)]
    if hits and not on_records_branch(current_branch(cwd), branches):
        sys.stderr.write(f"{SETTINGS['label']}: protected files staged outside an allowed branch:\n")
        for name in hits:
            sys.stderr.write(f"  {name}\n")
        sys.stderr.write("Move the change to a branch matching " + ", ".join(branches) + ".\n")
        return 1
    return 0


def violation(path: str, cwd: str) -> tuple[str, list[str]] | None:
    """(path, branch patterns) when `path` is protected in its owning checkout and that
    checkout is not on an allowed branch; None otherwise."""
    root = owner_root(path, cwd)
    protected, branches = load_config(root)
    if not is_protected(path, root, protected):
        return None
    branch = current_branch(root)
    if branch is None or on_records_branch(branch, branches):
        return None
    return path, branches


def payload_mode() -> int:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            return 0
    except (ValueError, OSError):
        return 0
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0
    cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else os.getcwd()

    found = None
    if tool in EDIT_TOOLS:
        path = tool_input.get("file_path") or tool_input.get("notebook_path")
        if isinstance(path, str):
            found = violation(path, cwd)
    elif tool == "Bash" and isinstance(tool_input.get("command"), str):
        command = tool_input["command"]
        resolved = resolved_writes(command, cwd)
        for path in resolved or []:
            found = violation(path, cwd)
            if found:
                break
        if found is None and resolved is None:  # no resolver: the text heuristic is the fallback
            protected, branches = load_config(cwd)
            name = command_writes_protected(command, protected)
            branch = current_branch(cwd)
            if name and branch is not None and not on_records_branch(branch, branches):
                found = (name, branches)
    if found is None:
        return 0
    target, branches = found
    deny(f"{SETTINGS['label']}: {target} is a protected {SETTINGS['noun']}; edit it only on "
         f"{SETTINGS['branch_noun']} ({', '.join(branches)}). {SETTINGS['advice']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if "--config" in args:
        at = args.index("--config")
        if at + 1 >= len(args):
            sys.stderr.write("records-guard: --config needs a path\n")
            return 2
        SETTINGS["config"] = args[at + 1]
    if "--staged" in args:
        return staged_mode(os.getcwd())
    return payload_mode()


if __name__ == "__main__":
    sys.exit(main())
