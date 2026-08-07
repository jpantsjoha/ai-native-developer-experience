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
HOOKS_ROOT_MANIFEST = "hooks.json"

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
# Official SemVer 2.0.0 pattern. Local rule: the standard only recommends SemVer.
# ASCII [0-9] throughout, never \d — Python's \d matches Unicode digits, so "1.2٢.3"
# would otherwise pass. Applied with fullmatch(), because `$` also permits a trailing
# newline and "1.2.3\n" is not a version.
SEMVER_RE = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
)

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


def escapes_via_traversal(value: str) -> bool:
    """True when a rooted path expression climbs above the root it declares.

    The published MCP schema anchors only the *prefix* of `cwd` and states that
    filesystem containment is validated separately. Checking the prefix alone accepts
    `./../outside` and `${PLUGIN_ROOT}/../outside`, so the suffix is normalised here and
    any component that escapes is rejected.
    """
    suffix = re.sub(r"^(?:\./|\$\{PLUGIN_ROOT\}/?|\$\{PLUGIN_DATA\}/?)", "", value)
    # A Windows client resolves backslash as a separator, so `./..\outside` escapes there
    # while looking like one innocent component to a slash-only split.
    suffix = suffix.replace("\\", "/")
    depth = 0
    for part in suffix.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            depth -= 1
            if depth < 0:
                return True
        else:
            depth += 1
    return False


def resolves_in_root(cwd: str, root: Path) -> bool:
    """True when a root-relative `cwd` still lands inside the package after symlinks.

    Only `./` and `${PLUGIN_ROOT}`-rooted values can be checked on disk; `${PLUGIN_DATA}`
    is a client-managed directory that does not exist at validation time. A value that
    does not yet exist is accepted — this checks escape, not presence.
    """
    if cwd.startswith("${PLUGIN_DATA}"):
        return True
    relative = re.sub(r"^(?:\./|\$\{PLUGIN_ROOT\}/?)", "", cwd).replace("\\", "/")
    if not relative:
        return True
    candidate = root / relative
    existing = candidate
    while not existing.exists() and existing != existing.parent:
        existing = existing.parent
    return within_root(existing, root)


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
        if session_skill and session_skill not in skill_dirs(root / "skills"):
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

    # Local hygiene, stricter than the standard: `version` is optional in the schema and
    # SemVer is only "recommended". This project's release process is tag-based SemVer, so
    # a missing or malformed version would ship a release nobody can order. Without this,
    # a version of "banana" repeated across every manifest passes both gates.
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER_RE.fullmatch(version):
        errors.append(
            f"{ROOT_MANIFEST}: version must be SemVer (local rule), found {version!r}"
        )

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
    """Validate skill frontmatter against Agent Skills, and the alias against it.

    `skills/` is canonical — it is the Agent Plugins fixed discovery location and the one
    real directory, so it survives installers that flatten or drop symlinks.
    `.agents/skills/` is the alias kept for runners (Codex, Kimi) that discover there
    natively.
    """
    canonical_base = root / "skills"
    canonical = skill_dirs(canonical_base)
    if not canonical:
        errors.append("no skills found under skills/")
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

    alias = root / ".agents" / "skills"
    if not alias.is_dir():
        errors.append(".agents/skills discovery alias is missing or broken")
        return
    if skill_dirs(alias) != canonical:
        errors.append(".agents/skills alias skill set differs from canonical skills/")


def check_skills_path_safety(root: Path, errors: list[str]) -> None:
    """Enforce path safety and require the fixed location to be a real directory.

    Live install testing showed why this matters: Codex's install cache drops a symlink at
    `skills/`, leaving a conformant client with zero skills at the spec's fixed location.
    So `skills/` must be a real directory. The `.agents/skills` alias may be a symlink, but
    it must stay relative — an absolute target would not survive a clone — and must resolve
    inside the package root.
    """
    fixed = root / "skills"
    if not fixed.exists():
        errors.append("skills/ fixed location is missing (spec component location)")
    elif fixed.is_symlink():
        errors.append(
            "skills/ must be a real directory, not a symlink — installers that flatten "
            "packages drop it and the spec's fixed discovery location disappears"
        )

    alias = root / ".agents" / "skills"
    if not alias.exists():
        return  # The alias is optional; only its shape is constrained.
    if not alias.is_symlink():
        return
    target = os.readlink(alias)
    if os.path.isabs(target):
        errors.append(f".agents/skills symlink target must be relative, found {target!r}")
    if not within_root(alias, root):
        errors.append(f".agents/skills symlink escapes the plugin root: {target!r}")


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
        check_mcp_server(server_name, server, errors, root)


def check_mcp_server(
    server_name: str, server: object, errors: list[str], root: Path | None = None
) -> None:
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
        if not isinstance(command, str) or not command:
            errors.append(f"{label} command must be a non-empty string, found {command!r}")
        elif len(command.split()) != 1:
            errors.append(f"{label} command must be a single token, found {command!r}")

        if "args" in server:
            args = server["args"]
            if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
                errors.append(f"{label} args must be an array of strings")

        if "env" in server:
            env = server["env"]
            if not isinstance(env, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in env.items()
            ):
                errors.append(f"{label} env must be an object of string values")
            else:
                reserved = sorted(RESERVED_ENV & set(env))
                if reserved:
                    errors.append(
                        f"{label} env must not declare reserved variables: {reserved}"
                    )

        if "cwd" in server:
            cwd = server["cwd"]
            if not isinstance(cwd, str):
                errors.append(f"{label} cwd must be a string")
            elif not CWD_RE.match(cwd):
                errors.append(
                    f"{label} cwd must be ./, ${{PLUGIN_ROOT}}, or ${{PLUGIN_DATA}} rooted"
                )
            elif escapes_via_traversal(cwd):
                # The published schema only anchors the prefix and defers containment to
                # the client. A prefix check alone accepts "./../outside", which would run
                # the server beyond the plugin or data boundary.
                errors.append(f"{label} cwd must not traverse outside its root: {cwd!r}")
            elif root is not None and not resolves_in_root(cwd, root):
                # Lexical checks cannot see an in-root symlink pointing elsewhere:
                # "${PLUGIN_ROOT}/escape/work" counts as two ordinary components while
                # landing outside the package. ${PLUGIN_DATA} is client-managed and not
                # resolvable here, so only root-relative forms are checked on disk.
                errors.append(
                    f"{label} cwd resolves outside the plugin root via a symlink: {cwd!r}"
                )
        return

    url = server.get("url")
    if not isinstance(url, str) or not url:
        errors.append(f"{label} url must be a non-empty string, found {url!r}")
    else:
        parts = urlsplit(url)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            errors.append(f"{label} url must be an absolute http(s) URL")
        elif parts.username or parts.password or parts.fragment:
            errors.append(f"{label} url must not carry user info or a fragment")
        elif parts.scheme == "http" and parts.hostname not in LOOPBACK_HOSTS:
            errors.append(f"{label} non-loopback url must use https")

    if "headers" in server:
        headers = server["headers"]
        if not isinstance(headers, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in headers.items()
        ):
            errors.append(f"{label} headers must be an object of string values")


def check_hooks(root: Path, errors: list[str]) -> None:
    """Validate both hook manifests and require them to stay byte-identical.

    Two copies exist because two clients look in different places: Claude Code reads
    `hooks/hooks.json`, and Antigravity (`agy`) reads `hooks.json` at the package root.
    Shipping only the nested one meant Antigravity silently registered no session-start
    hook in every release up to 0.2.0. Duplication is the price of that; this check is
    what stops the duplicate drifting.
    """
    manifests = ["hooks/hooks.json", HOOKS_ROOT_MANIFEST]
    contents: dict[str, str] = {}

    for rel in manifests:
        hooks = load_json(root, rel, errors)
        if hooks is None:
            continue
        contents[rel] = (root / rel).read_text(encoding="utf-8")
        command = (
            (hooks.get("hooks", {}).get("SessionStart") or [{}])[0]
            .get("hooks", [{}])[0]
            .get("command", "")
        )
        match = re.search(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"]+)", command)
        if not match:
            errors.append(f"{rel}: cannot resolve hook command {command!r}")
            continue
        script = root / match.group(1)
        if not script.is_file():
            errors.append(f"{rel} references missing script: {match.group(1)}")
        elif not os.access(script, os.X_OK):
            errors.append(f"hook script is not executable: {match.group(1)}")

    if len(contents) == len(manifests) and len(set(contents.values())) != 1:
        errors.append(
            f"hook manifest drift: {manifests[0]} and {HOOKS_ROOT_MANIFEST} must be identical"
        )


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
