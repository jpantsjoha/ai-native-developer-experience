#!/usr/bin/env python3
"""Drift validator for the join-the-team plugin packaging layer.

The canonical skills live in `.agents/skills/`; each harness manifest is a thin
projection of that one contract. This script fails when the projections drift:
manifest name/version skew, dead skill references, frontmatter/dirname mismatch,
a broken `skills/` discovery alias, or a hook that points at a missing script.

Standard library only. Exit 0 = PASS, 1 = drift detected.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

MANIFESTS = [
    ".kimi-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    "gemini-extension.json",
]
MARKETPLACE = ".claude-plugin/marketplace.json"

NAME_RE = re.compile(r"^name:\s*([a-z0-9-]+)\s*$", re.MULTILINE)


def load_json(root: Path, rel: str, errors: list[str]) -> dict | None:
    path = root / rel
    if not path.is_file():
        errors.append(f"missing manifest: {rel}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{rel}: invalid JSON: {exc}")
        return None


def skill_dirs(base: Path) -> list[str]:
    if not base.is_dir():
        return []
    return sorted(
        entry.name
        for entry in base.iterdir()
        if entry.is_dir() and (entry / "SKILL.md").is_file()
    )


def check_manifest_coherence(root: Path, errors: list[str]) -> None:
    loaded = {rel: load_json(root, rel, errors) for rel in MANIFESTS}
    marketplace = load_json(root, MARKETPLACE, errors)
    if marketplace is not None:
        plugins = marketplace.get("plugins") or []
        if len(plugins) != 1:
            errors.append(f"{MARKETPLACE}: expected exactly one plugin entry")
        elif isinstance(plugins[0], dict):
            loaded[f"{MARKETPLACE} plugins[0]"] = plugins[0]

    identities = {
        rel: (doc.get("name"), doc.get("version"))
        for rel, doc in loaded.items()
        if doc is not None
    }
    distinct = set(identities.values())
    if len(distinct) > 1:
        errors.append(
            "manifest name/version drift: "
            + ", ".join(f"{rel}={identity!r}" for rel, identity in identities.items())
        )

    kimi = loaded.get(".kimi-plugin/plugin.json")
    if kimi:
        skills_field = kimi.get("skills", "")
        if not (root / skills_field).is_dir():
            errors.append(f"kimi manifest skills path does not resolve: {skills_field!r}")
        session_skill = (kimi.get("sessionStart") or {}).get("skill")
        if session_skill and session_skill not in skill_dirs(root / ".agents" / "skills"):
            errors.append(f"kimi sessionStart skill not found on disk: {session_skill!r}")

    gemini = loaded.get("gemini-extension.json")
    if gemini:
        context_file = gemini.get("contextFileName", "")
        if context_file and not (root / context_file).is_file():
            errors.append(f"gemini contextFileName does not resolve: {context_file!r}")


def check_skills(root: Path, errors: list[str]) -> None:
    canonical = skill_dirs(root / ".agents" / "skills")
    if not canonical:
        errors.append("no skills found under .agents/skills")
        return
    for name in canonical:
        text = (root / ".agents" / "skills" / name / "SKILL.md").read_text(
            encoding="utf-8"
        )[:500]
        match = NAME_RE.search(text)
        if not match or match.group(1) != name:
            found = match.group(1) if match else "none"
            errors.append(f"skill {name}: frontmatter name is {found!r}")

    alias = root / "skills"
    if not alias.is_dir():
        errors.append("root skills/ discovery alias is missing or broken")
    elif skill_dirs(alias) != canonical:
        errors.append("root skills/ alias skill set differs from .agents/skills")


def check_hooks(root: Path, errors: list[str]) -> None:
    hooks = load_json(root, "hooks/hooks.json", errors)
    if hooks is None:
        return
    command = (
        (hooks.get("hooks", {}).get("SessionStart") or [{}])[0]
        .get("hooks", [{}])[0]
        .get("command", "")
    )
    match = re.search(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"]+)", command)
    if not match:
        errors.append(f"hooks.json: cannot resolve hook command {command!r}")
        return
    script = root / match.group(1)
    if not script.is_file():
        errors.append(f"hooks.json references missing script: {match.group(1)}")
    elif not os.access(script, os.X_OK):
        errors.append(f"hook script is not executable: {match.group(1)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root to validate")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []
    check_manifest_coherence(root, errors)
    check_skills(root, errors)
    check_hooks(root, errors)

    for error in errors:
        print(f"DRIFT: {error}", file=sys.stderr)
    if errors:
        return 1
    print("PASS plugin-packaging validation (0 drift findings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
