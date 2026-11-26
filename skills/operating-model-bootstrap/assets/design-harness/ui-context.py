#!/usr/bin/env python3
"""ui-context: remind the agent, once per session, to load the design skill on UI paths.

Why it exists: UI drift starts when an agent edits a view without the project's design
baseline in context. On the first edit of a UI path in a session this hook adds one line of
context naming the skill; later edits stay quiet. It never denies and never returns `ask`.

Config (optional) `.devex/ui-context.json`, read from the checkout that owns the edited path
(not the session `cwd`):
  {"ui_globs": ["**/*.swift", "**/*.css"], "skill": "design-steward"}
`skill` is a skill name (`design-steward`) or a path to a skill file (`skills/design/SKILL.md`,
anything with a `/` or ending `.md`); the message says which. Globs use the same matcher as
the literal ratchet: `**/` crosses directories, a trailing `**` matches everything beneath,
`*` stays inside one segment.
State: a marker file per session id under $DEVEX_STATE_DIR (default: the system temp dir).
The one edge that bites: without a session_id in the payload the reminder repeats.
Malformed JSON allows silently.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile

DEFAULT_GLOBS = ["**/*.swift", "**/*.kt", "**/*.css", "**/*.scss", "**/*.tsx", "**/*.jsx",
                 "**/*.vue", "**/*.svelte", "**/*.html", "**/*.qml", "**/*.xml"]
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a path glob (`**` crosses directories, `*` does not) to a regex.

    Identical to the matcher in literal_ratchet.py; a test fails if they diverge.
    """
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


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
    path = tool_input.get("file_path")
    if not isinstance(path, str):
        return 0
    session_cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else os.getcwd()
    cwd = owner_root(path, session_cwd)
    globs, skill = DEFAULT_GLOBS, "design-steward"
    try:
        with open(os.path.join(cwd, ".devex", "ui-context.json"), encoding="utf-8") as handle:
            data = json.load(handle)
        globs = [str(g) for g in data.get("ui_globs", globs)]
        skill = str(data.get("skill", skill))
    except (OSError, ValueError, AttributeError, TypeError):
        pass
    rel = os.path.relpath(path, cwd).replace(os.sep, "/") if os.path.isabs(path) else path
    if not any(glob_to_regex(g).match(rel) for g in globs):
        return 0

    session = str(payload.get("session_id") or "")
    if session:
        state_dir = os.environ.get("DEVEX_STATE_DIR") or tempfile.gettempdir()
        marker = os.path.join(state_dir, "devex-ui-context-" + re.sub(r"[^A-Za-z0-9_.-]", "_", session))
        if os.path.exists(marker):
            return 0
        try:
            with open(marker, "w", encoding="utf-8") as handle:
                handle.write("1\n")
        except OSError:
            pass
    is_path = "/" in skill or skill.endswith(".md")
    how = f"read the design skill at `{skill}`" if is_path else f"load the `{skill}` skill"
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": f"UI path {rel}: {how} and the project's design baseline "
                             "before editing; use tokens, not literals.",
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
