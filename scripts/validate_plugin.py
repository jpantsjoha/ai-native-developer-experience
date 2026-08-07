#!/usr/bin/env python3
"""Packaging validator for the join-the-team plugin.

Two gates live here, and they answer different questions.

**Drift** — the canonical skills live in `.agents/skills/`; each harness manifest is a thin
projection of that one contract. The drift gate fails when the projections skew: manifest
name/version drift, dead skill references, a broken `skills/` discovery alias, or a hook
that points at a missing script.

**Conformance** — the plugin targets Agent Plugins 1.0.0 (https://agent-plugins.org/
specification) and Agent Skills (https://agentskills.io/specification). The conformance
gate re-implements the published schemas' load-bearing rules against the on-disk package:
root manifest shape, skill frontmatter, fixed-location path safety, and MCP configuration.

The conformance gate is deliberately hand-rolled and standard-library only — the validator
must run offline, in CI, with no third-party dependency. The cost is that a specification
version bump means re-reading the published schema, not just editing this file. ADR-002
records that obligation.

Exit 0 = PASS, 1 = findings.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT_MANIFEST = "plugin.json"
MANIFESTS = [
    ROOT_MANIFEST,
    ".kimi-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    "gemini-extension.json",
]
MARKETPLACE = ".claude-plugin/marketplace.json"
MCP_CONFIG = "mcp.json"

PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"

# Agent Plugins 1.0.0 plugin.schema.json — `additionalProperties: false`.
ROOT_KEYS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}
AUTHOR_KEYS = {"name", "email", "url"}

# Plugin names allow periods; skill names do not. Both ban leading/trailing and
# consecutive separators, and both cap at 64 characters.
PLUGIN_NAME_RE = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SKILL_NAME_RE = re.compile(r"^(?!.*--)[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
NAMESPACE_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$")
NAME_MAX = 64
DESCRIPTION_MAX = 1024

# Agent Plugins 1.0.0 mcp.schema.json — closed union, one key set per transport.
MCP_SERVER_KEYS = {
    "stdio": {"type", "command", "args", "env", "cwd"},
    "streamable-http": {"type", "url", "headers"},
    "sse": {"type", "url", "headers"},
}
MCP_REQUIRED_KEYS = {
    "stdio": {"type", "command"},
    "streamable-http": {"type", "url"},
    "sse": {"type", "url"},
}
CWD_RE = re.compile(r"^(?:\./|\$\{PLUGIN_ROOT\}(?:/|$)|\$\{PLUGIN_DATA\}(?:/|$))")
RESERVED_ENV = {"PLUGIN_ROOT", "PLUGIN_DATA"}
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1", "[::1]"}


def load_json(root: Path, rel: str, errors: list[str]) -> dict | None:
    """Read a JSON document relative to the package root, recording read failures."""
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
    """Return the sorted names of immediate child directories that hold a SKILL.md."""
    if not base.is_dir():
        return []
    return sorted(
        entry.name
        for entry in base.iterdir()
        if entry.is_dir() and (entry / "SKILL.md").is_file()
    )


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Parse the leading YAML frontmatter block into flat string scalars.

    Returns None when the document does not open with a `---` fence. Only top-level
    `key: value` scalars are read — that is all the Agent Skills frontmatter contract
    requires, and a full YAML parser is not available in the standard library. Surrounding
    matched quotes are stripped so a quoted description compares like an unquoted one.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            continue
        value = match.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        fields[match.group(1)] = value
    return None  # unterminated frontmatter block


def within_root(path: Path, root: Path) -> bool:
    """True when `path` resolves inside `root` after symlink resolution."""
    try:
        return path.resolve().is_relative_to(root)
    except (OSError, ValueError):
        return False


def check_manifest_coherence(root: Path, errors: list[str]) -> None:
    """Fail when the vendor manifest projections disagree on plugin name or version."""
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


def check_root_manifest(root: Path, errors: list[str]) -> None:
    """Validate the root plugin.json against Agent Plugins 1.0.0 plugin.schema.json."""
    manifest = load_json(root, ROOT_MANIFEST, errors)
    if manifest is None:
        return

    schema = manifest.get("$schema")
    if schema != PLUGIN_SCHEMA:
        errors.append(f"{ROOT_MANIFEST}: $schema must be {PLUGIN_SCHEMA!r}, found {schema!r}")

    name = manifest.get("name")
    if not isinstance(name, str) or not name:
        errors.append(f"{ROOT_MANIFEST}: name is required and must be a non-empty string")
    else:
        if len(name) > NAME_MAX:
            errors.append(f"{ROOT_MANIFEST}: name exceeds {NAME_MAX} characters")
        if not PLUGIN_NAME_RE.match(name):
            errors.append(f"{ROOT_MANIFEST}: name {name!r} violates the spec name pattern")

    unknown = sorted(set(manifest) - ROOT_KEYS)
    if unknown:
        errors.append(
            f"{ROOT_MANIFEST}: unknown top-level fields (schema forbids extras): {unknown}"
        )

    author = manifest.get("author")
    if author is not None:
        if not isinstance(author, dict):
            errors.append(f"{ROOT_MANIFEST}: author must be an object")
        else:
            extra = sorted(set(author) - AUTHOR_KEYS)
            if extra:
                errors.append(f"{ROOT_MANIFEST}: author has unknown fields: {extra}")

    for field in ("version", "description", "homepage", "repository", "license"):
        value = manifest.get(field)
        if value is not None and not isinstance(value, str):
            errors.append(f"{ROOT_MANIFEST}: {field} must be a string")

    keywords = manifest.get("keywords")
    if keywords is not None:
        if not isinstance(keywords, list) or not all(isinstance(k, str) for k in keywords):
            errors.append(f"{ROOT_MANIFEST}: keywords must be an array of strings")

    check_extensions(root, manifest.get("extensions"), errors)


def check_extensions(root: Path, extensions: object, errors: list[str]) -> None:
    """Validate the `extensions` block and prove every declared path still exists.

    The spec assigns no meaning to namespace contents, so this only enforces the schema
    shape plus one local rule: a declared plugin-relative path must resolve on disk and
    stay inside the package. A declaration that points at a moved file is a lie the
    package would otherwise ship silently.
    """
    if extensions is None:
        return
    if not isinstance(extensions, dict):
        errors.append(f"{ROOT_MANIFEST}: extensions must be an object")
        return

    for namespace, payload in extensions.items():
        if not NAMESPACE_RE.match(namespace):
            errors.append(
                f"{ROOT_MANIFEST}: extension key {namespace!r} is not a reverse-domain namespace"
            )
        if not isinstance(payload, dict):
            errors.append(f"{ROOT_MANIFEST}: extension {namespace!r} must map to an object")
            continue
        for key, value in payload.items():
            if not isinstance(value, str) or not value.startswith("./"):
                continue
            target = root / value
            if not target.exists():
                errors.append(
                    f"{ROOT_MANIFEST}: extension {namespace}.{key} points at missing path {value!r}"
                )
            elif not within_root(target, root):
                errors.append(
                    f"{ROOT_MANIFEST}: extension {namespace}.{key} escapes the plugin root: {value!r}"
                )


def check_skills(root: Path, errors: list[str]) -> None:
    """Validate skill frontmatter against Agent Skills, and the `skills/` alias against it."""
    canonical_base = root / ".agents" / "skills"
    canonical = skill_dirs(canonical_base)
    if not canonical:
        errors.append("no skills found under .agents/skills")
        return

    for name in canonical:
        skill_file = canonical_base / name / "SKILL.md"
        fields = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        if fields is None:
            errors.append(f"skill {name}: SKILL.md has no closed YAML frontmatter block")
            continue

        declared = fields.get("name")
        if not declared:
            errors.append(f"skill {name}: frontmatter is missing the required name field")
        elif declared != name:
            errors.append(f"skill {name}: frontmatter name is {declared!r}, expected {name!r}")
        elif len(declared) > NAME_MAX or not SKILL_NAME_RE.match(declared):
            errors.append(f"skill {name}: name violates the Agent Skills name pattern")

        description = fields.get("description")
        if not description:
            errors.append(f"skill {name}: frontmatter is missing a non-empty description")
        elif len(description) > DESCRIPTION_MAX:
            errors.append(
                f"skill {name}: description is {len(description)} characters, "
                f"limit is {DESCRIPTION_MAX}"
            )

    alias = root / "skills"
    if not alias.is_dir():
        errors.append("root skills/ discovery alias is missing or broken")
        return
    if skill_dirs(alias) != canonical:
        errors.append("root skills/ alias skill set differs from .agents/skills")


def check_skills_path_safety(root: Path, errors: list[str]) -> None:
    """Enforce the spec's path-safety rule on the `skills/` fixed location.

    `.agents/skills/` is canonical and `skills/` is the spec's fixed discovery location,
    so the alias is the one seam where a package could point discovery outside itself.
    The link must stay relative — an absolute target would not survive a clone — and must
    resolve inside the package root after symlink resolution.
    """
    alias = root / "skills"
    if not alias.exists():
        errors.append("skills/ fixed location is missing (spec component location)")
        return
    if not alias.is_symlink():
        return  # A real directory at the fixed location is equally conformant.
    target = os.readlink(alias)
    if os.path.isabs(target):
        errors.append(f"skills/ symlink target must be relative, found {target!r}")
    if not within_root(alias, root):
        errors.append(f"skills/ symlink escapes the plugin root: {target!r}")


def check_mcp_config(root: Path, errors: list[str]) -> None:
    """Validate a root mcp.json against Agent Plugins 1.0.0, if one is shipped.

    The file is optional; this package intentionally ships none, because the governed-seam
    template in `.agents/mcp_config.json` names example servers a client must never spawn.
    The check exists so that the day a real mcp.json lands, it lands conformant.
    """
    path = root / MCP_CONFIG
    if not path.is_file():
        return

    config = load_json(root, MCP_CONFIG, errors)
    if config is None:
        return

    if config.get("$schema") != MCP_SCHEMA:
        errors.append(f"{MCP_CONFIG}: $schema must be {MCP_SCHEMA!r}")
    extra = sorted(set(config) - {"$schema", "mcpServers"})
    if extra:
        errors.append(f"{MCP_CONFIG}: unknown top-level fields: {extra}")

    servers = config.get("mcpServers")
    if not isinstance(servers, dict):
        errors.append(f"{MCP_CONFIG}: mcpServers is required and must be an object")
        return

    for server_name, server in servers.items():
        check_mcp_server(server_name, server, errors)


def check_mcp_server(server_name: str, server: object, errors: list[str]) -> None:
    """Validate one MCP server entry against the closed transport union."""
    label = f"{MCP_CONFIG}: server {server_name!r}"
    if not isinstance(server, dict):
        errors.append(f"{label} must be an object")
        return

    transport = server.get("type")
    if transport not in MCP_SERVER_KEYS:
        errors.append(
            f"{label} has type {transport!r}; expected one of {sorted(MCP_SERVER_KEYS)}"
        )
        return

    missing = sorted(MCP_REQUIRED_KEYS[transport] - set(server))
    if missing:
        errors.append(f"{label} is missing required fields: {missing}")
    unknown = sorted(set(server) - MCP_SERVER_KEYS[transport])
    if unknown:
        errors.append(f"{label} has fields not allowed for {transport}: {unknown}")

    if transport == "stdio":
        command = server.get("command")
        if isinstance(command, str) and len(command.split()) != 1:
            errors.append(f"{label} command must be a single token, found {command!r}")
        env = server.get("env")
        if isinstance(env, dict):
            reserved = sorted(RESERVED_ENV & set(env))
            if reserved:
                errors.append(f"{label} env must not declare reserved variables: {reserved}")
        cwd = server.get("cwd")
        if isinstance(cwd, str) and not CWD_RE.match(cwd):
            errors.append(f"{label} cwd must be ./, ${{PLUGIN_ROOT}}, or ${{PLUGIN_DATA}} rooted")
        return

    url = server.get("url")
    if isinstance(url, str):
        parts = urlsplit(url)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            errors.append(f"{label} url must be an absolute http(s) URL")
        elif parts.username or parts.password or parts.fragment:
            errors.append(f"{label} url must not carry user info or a fragment")
        elif parts.scheme == "http" and parts.hostname not in LOOPBACK_HOSTS:
            errors.append(f"{label} non-loopback url must use https")


def check_hooks(root: Path, errors: list[str]) -> None:
    """Fail when the session-start hook points at a missing or non-executable script."""
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
    parser.add_argument(
        "--spec-only",
        action="store_true",
        help="run only the Agent Plugins / Agent Skills conformance gate",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []

    check_root_manifest(root, errors)
    check_skills(root, errors)
    check_skills_path_safety(root, errors)
    check_mcp_config(root, errors)
    if not args.spec_only:
        check_manifest_coherence(root, errors)
        check_hooks(root, errors)

    for error in errors:
        print(f"DRIFT: {error}", file=sys.stderr)
    if errors:
        return 1
    scope = "Agent Plugins 1.0.0 conformance" if args.spec_only else "plugin-packaging"
    print(f"PASS {scope} validation (0 findings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
