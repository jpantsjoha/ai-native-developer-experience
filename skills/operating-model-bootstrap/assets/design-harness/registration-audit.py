#!/usr/bin/env python3
"""registration-audit: every test script is registered with a runner, or excluded with a reason.

Why it exists: a test file nobody runs is green by omission. A script dropped into `test/`
passes review, runs nowhere, and the suite stays green. This audit lists the files that match
`scripts` and fails for each one whose path or file name appears in no `runners` file (a
Makefile, a package.json, a driver script) unless `allow` names it with a reason.

Config `.devex/test-registration.json` (paths relative to --root, `**` crosses directories):
  {"scripts": ["test/**/*.test.sh", "tests/**/*.sh"],
   "runners": ["Makefile", "package.json", "test/**/*.js"],
   "allow": [{"path": "test/legacy.test.sh", "reason": "run by test/driver.js"}]}
Exit: 0 clean, 1 findings, 2 config error. Findings: an unregistered script, an allow entry
with no reason, a stale allow entry (file gone, or now registered so the entry is dead).
The one edge that bites: "registered" is a text match on the file name, so a runner that
mentions the script in a comment counts; keep runner globs to files that execute tests.
Python 3 standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".build", "build", "dist", "__pycache__", ".venv"}


def glob_to_regex(pattern: str) -> re.Pattern[str]:
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


def walk(root: Path) -> list[str]:
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            found.append(Path(dirpath, name).relative_to(root).as_posix())
    return found


def audit(root: Path, config: dict) -> list[str]:
    scripts = [glob_to_regex(g) for g in config.get("scripts") or []]
    runners = [glob_to_regex(g) for g in config.get("runners") or []]
    if not scripts or not runners:
        raise ValueError("config needs non-empty 'scripts' and 'runners' lists")
    allow = config.get("allow") or []
    files = walk(root)
    targets = [f for f in files if any(p.match(f) for p in scripts)]
    runner_text = {}
    for rel in files:
        if any(p.match(rel) for p in runners):
            try:
                runner_text[rel] = (root / rel).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

    def registered(rel: str) -> bool:
        name = os.path.basename(rel)
        return any(runner != rel and (rel in text or name in text)
                   for runner, text in runner_text.items())

    findings = []
    allowed = {}
    for entry in allow:
        path = entry.get("path") if isinstance(entry, dict) else None
        reason = (entry.get("reason") or "").strip() if isinstance(entry, dict) else ""
        if not isinstance(path, str):
            findings.append("allow entry needs a 'path'")
            continue
        if not reason:
            findings.append(f"allow entry {path}: needs a reason")
        allowed[path] = reason
    for rel in targets:
        if registered(rel):
            if rel in allowed:
                findings.append(f"allow entry {rel}: stale, the script is registered now")
        elif rel not in allowed:
            findings.append(f"{rel}: not registered with any runner and not in allow")
    for path in allowed:
        if path not in targets:
            findings.append(f"allow entry {path}: stale, no such test script")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("--config", default=".devex/test-registration.json")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    config_path = Path(args.config)
    config_path = config_path if config_path.is_absolute() else root / config_path
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        findings = audit(root, config)
    except (OSError, ValueError, AttributeError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    for line in findings:
        print(f"FAIL registration-audit: {line}", file=sys.stderr)
    if not findings:
        print("PASS registration-audit")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
