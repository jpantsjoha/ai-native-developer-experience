#!/usr/bin/env python3
"""Stack-neutral literal ratchet: literal counts per (rule, file) may fall, never rise.

Why it exists: a design system or code standard is only enforced if hand-written literals
(colours, sizes, magic strings) stop growing. This engine counts regex matches per rule per
file against a committed baseline and fails when a count rises or a new (rule, file) pair
appears. It is deterministic, offline and standard-library only.

Config (JSON) — all paths are relative to --root:
  {"baseline": ".devex/ratchet.baseline.json",
   "globs":  ["**/*.swift", "**/*.css"],          # files scanned by default
   "exempt": ["**/DesignTokens.swift"],           # never scanned (the token source files)
   "rules":  [{"id": "css-hex", "regex": "#[0-9a-fA-F]{6}\\b",
               "globs": ["**/*.css"], "exempt": [], "message": "use a token"}]}

Exit: 0 clean, 1 regression, 2 usage/config error or refused baseline raise.

Raise discipline (`--check-raise BASE_REF`): a baseline that rose against BASE_REF, or gained a
(rule, file) pair for a rule BASE_REF already had, needs a note (config key `raise_note`,
default `.devex/baseline-raise.txt`) that changed since BASE_REF, with one line per raise:
`<rule> <file|*> <reason>`. A missing note, an unchanged note, a line with no reason and a
line that matches no raise (stale or wrong file) all fail with exit 1. A rule absent from the
BASE_REF baseline is an initial baseline and needs no line. Run it in the PR gate: it holds on
any branch name, so no branch pattern has to stand in for review.
The one edge that bites: --update-baseline only ever lowers counts (or creates the first
baseline); a rise needs a deliberate, reviewed edit of the baseline file. The same holds
for a new rule or a new file: --update-baseline refuses a (rule, file) pair the baseline does
not list, so a new pair enters only by a reviewed edit of the baseline file.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".build", "build", "dist", "__pycache__", ".venv"}
MAX_LINES_REPORTED = 5


class ConfigError(Exception):
    """Raised for an unusable config or baseline; mapped to exit code 2."""


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a path glob (`**` crosses directories, `*` does not) to a regex."""
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


def matches_any(path: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(p.match(path) for p in patterns)


def load_json(path: Path, what: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"cannot read {what} {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"{what} {path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"{what} {path} must be a JSON object")
    return data


def compile_config(config: dict) -> dict:
    """Validate the config and precompile globs and regexes."""
    rules = config.get("rules")
    if not isinstance(rules, list) or not rules:
        raise ConfigError("config needs a non-empty 'rules' list")
    default_globs = config.get("globs") or ["**/*"]
    compiled, seen = [], set()
    for rule in rules:
        rid, regex = rule.get("id"), rule.get("regex")
        if not isinstance(rid, str) or not isinstance(regex, str):
            raise ConfigError("every rule needs string 'id' and 'regex'")
        if rid in seen:
            raise ConfigError(f"duplicate rule id {rid!r}")
        seen.add(rid)
        try:
            pattern = re.compile(regex)
        except re.error as exc:
            raise ConfigError(f"rule {rid!r}: bad regex: {exc}") from exc
        compiled.append({
            "id": rid,
            "regex": pattern,
            "message": rule.get("message", ""),
            "globs": [glob_to_regex(g) for g in rule.get("globs") or default_globs],
            "exempt": [glob_to_regex(g) for g in rule.get("exempt") or []],
        })
    return {
        "baseline": config.get("baseline", ".devex/ratchet.baseline.json"),
        "exempt": [glob_to_regex(g) for g in config.get("exempt") or []],
        "rules": compiled,
    }


def list_files(root: Path) -> list[str]:
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            found.append(Path(dirpath, name).relative_to(root).as_posix())
    return found


def normalise_files(root: Path, files: list[str]) -> list[str]:
    """Map --files entries to root-relative posix paths; drop anything outside root."""
    kept = []
    for raw in files:
        path = Path(raw)
        path = path if path.is_absolute() else root / path
        try:
            kept.append(path.resolve().relative_to(root).as_posix())
        except ValueError:
            continue
    return sorted(set(kept))


def scan(root: Path, cfg: dict, files: list[str]) -> tuple[dict, dict]:
    """Return ({rule: {file: count}}, {(rule, file): [line numbers]})."""
    counts: dict[str, dict[str, int]] = {r["id"]: {} for r in cfg["rules"]}
    lines: dict[tuple[str, str], list[int]] = {}
    for rel in files:
        if matches_any(rel, cfg["exempt"]):
            continue
        applicable = [
            r for r in cfg["rules"]
            if matches_any(rel, r["globs"]) and not matches_any(rel, r["exempt"])
        ]
        if not applicable:
            continue
        full = root / rel
        try:
            text = full.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for rule in applicable:
                hits = len(rule["regex"].findall(line))
                if hits:
                    counts[rule["id"]][rel] = counts[rule["id"]].get(rel, 0) + hits
                    lines.setdefault((rule["id"], rel), []).append(lineno)
    return counts, lines


def compare(current: dict, baseline: dict) -> list[dict]:
    """List regressions: a count above baseline, or a new (rule, file) pair."""
    regressions = []
    for rule, per_file in sorted(current.items()):
        for rel, count in sorted(per_file.items()):
            allowed = baseline.get(rule, {}).get(rel)
            if allowed is None:
                regressions.append({"rule": rule, "file": rel, "kind": "new",
                                    "baseline": 0, "current": count})
            elif count > allowed:
                regressions.append({"rule": rule, "file": rel, "kind": "rise",
                                    "baseline": allowed, "current": count})
    return regressions


def read_baseline(path: Path) -> dict | None:
    if not path.exists():
        return None
    data = load_json(path, "baseline")
    counts = data.get("counts")
    if not isinstance(counts, dict):
        raise ConfigError(f"baseline {path} needs a 'counts' object")
    return counts


def write_baseline(path: Path, counts: dict) -> None:
    pruned = {r: {f: c for f, c in sorted(fs.items()) if c > 0}
              for r, fs in sorted(counts.items())}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": 1, "counts": pruned}, indent=2, sort_keys=True)
                    + "\n", encoding="utf-8")


def git_show(root: Path, ref: str, rel: str) -> str | None:
    """File content at `ref`, or None when git or the path is unavailable there."""
    try:
        out = subprocess.run(["git", "-C", str(root), "show", f"{ref}:{rel}"],
                             capture_output=True, text=True, timeout=30, check=True)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout


def baseline_raises(base: dict, current: dict) -> list[tuple[str, str, int, int]]:
    """(rule, file, base count, current count) for each rise, and each new file of a known rule."""
    raises = []
    for rule, per_file in sorted(current.items()):
        if rule not in base:
            continue
        for rel, count in sorted(per_file.items()):
            before = base[rule].get(rel, 0)
            if count > before:
                raises.append((rule, rel, before, count))
    return raises


def check_raise(root: Path, config_path: Path, ref: str) -> tuple[int, list[str]]:
    """Enforce the raise note; returns (exit code, report lines)."""
    raw = load_json(config_path, "config")
    cfg = compile_config(raw)
    note_rel = str(raw.get("raise_note", ".devex/baseline-raise.txt"))
    current = read_baseline(root / cfg["baseline"]) or {}
    verify = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "--quiet",
                             f"{ref}^{{commit}}"], capture_output=True, text=True)
    if verify.returncode != 0:
        raise ConfigError(f"cannot resolve base ref {ref!r}; refusing to pass unchecked")
    base_text = git_show(root, ref, cfg["baseline"])
    if base_text is None:
        return 0, [f"PASS raise-check: no baseline at {ref}; initial baseline"]
    try:
        base = json.loads(base_text).get("counts")
    except (ValueError, AttributeError):
        base = None
    if not isinstance(base, dict):
        raise ConfigError(f"baseline at {ref} needs a 'counts' object")
    raises = baseline_raises(base, current)
    if not raises:
        return 0, ["PASS raise-check: no baseline raise against " + ref]
    report, failed = [], False
    note_path = root / note_rel
    base_note = git_show(root, ref, note_rel)
    try:
        note_text = note_path.read_text(encoding="utf-8")
    except OSError:
        note_text = None
    if note_text is None:
        return 1, [f"FAIL raise-check: baseline rose against {ref} but {note_rel} is missing"] + [
            f"  {r}: {f} {b} -> {c}" for r, f, b, c in raises]
    if base_note is not None and base_note == note_text:
        return 1, [f"FAIL raise-check: baseline rose against {ref} but {note_rel} is unchanged "
                   "since then (stale note)"] + [f"  {r}: {f} {b} -> {c}" for r, f, b, c in raises]
    entries = []
    for number, line in enumerate(note_text.splitlines(), start=1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        parts = text.split(None, 2)
        if len(parts) < 3 or not parts[2].strip():
            report.append(f"FAIL raise-check: {note_rel}:{number}: needs '<rule> <file|*> <reason>'")
            failed = True
            continue
        entries.append((number, parts[0], parts[1], parts[2]))
    used = set()
    for rule, rel, before, after in raises:
        hit = next((e for e in entries if e[1] == rule and e[2] in (rel, "*")), None)
        if hit is None:
            report.append(f"FAIL raise-check: [{rule}] {rel} {before} -> {after} has no line in {note_rel}")
            failed = True
        else:
            used.add(hit[0])
            report.append(f"covered: [{rule}] {rel} {before} -> {after}: {hit[3]}")
    for number, rule, rel, _reason in entries:
        if number not in used:
            report.append(f"FAIL raise-check: {note_rel}:{number}: '{rule} {rel}' matches no raise (stale or wrong file)")
            failed = True
    report.append("FAIL raise-check" if failed else f"PASS raise-check: {len(raises)} raise(s) covered")
    return (1 if failed else 0), report


def run(args: argparse.Namespace) -> tuple[int, dict]:
    root = Path(args.root).resolve()
    config_path = Path(args.config)
    config_path = config_path if config_path.is_absolute() else root / config_path
    cfg = compile_config(load_json(config_path, "config"))
    baseline_path = root / cfg["baseline"]
    baseline = read_baseline(baseline_path)

    partial = args.files is not None
    files = normalise_files(root, args.files) if partial else list_files(root)
    current, lines = scan(root, cfg, files)

    if args.update_baseline:
        if baseline is None:
            write_baseline(baseline_path, current)
            return 0, {"status": "baseline-created", "regressions": []}
        refused = compare(current, baseline)
        if refused:
            return 2, {"status": "refused", "regressions": refused, "lines": lines}
        merged = {r: dict(fs) for r, fs in baseline.items()}
        for rule in current:
            merged.setdefault(rule, {})
        scope = set(files) if partial else None
        for rule, per_file in merged.items():
            for rel in list(per_file):
                if scope is None or rel in scope:
                    new = current.get(rule, {}).get(rel, 0)
                    per_file[rel] = new
        write_baseline(baseline_path, merged)
        return 0, {"status": "baseline-updated", "regressions": []}

    if baseline is None:
        raise ConfigError(f"no baseline at {baseline_path}; run with --update-baseline once")
    regressions = compare(current, baseline)
    return (1 if regressions else 0), {
        "status": "regression" if regressions else "ok",
        "regressions": regressions, "lines": lines,
    }


def render_text(code: int, result: dict, messages: dict[str, str]) -> str:
    out = []
    for reg in result["regressions"]:
        where = result.get("lines", {}).get((reg["rule"], reg["file"]), [])
        first = ",".join(str(n) for n in where[:MAX_LINES_REPORTED])
        label = ("new literal in file" if reg["kind"] == "new" else
                 f"count rose {reg['baseline']} -> {reg['current']}")
        line_ref = f"{reg['file']}:{where[0]}" if where else reg["file"]
        extra = f" (lines {first})" if first else ""
        note = f" - {messages[reg['rule']]}" if messages.get(reg["rule"]) else ""
        out.append(f"{line_ref}: [{reg['rule']}] {label}{extra}{note}")
    if result["status"] == "refused":
        out.append("REFUSED: --update-baseline will not raise a count or add a pair")
    elif result["status"] == "regression":
        out.append(f"FAIL ratchet: {len(result['regressions'])} regression(s)")
    else:
        out.append(f"PASS ratchet ({result['status']})")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", default=".", help="project root (default: cwd)")
    parser.add_argument("--config", default=".devex/ratchet.config.json")
    parser.add_argument("--files", nargs="+", help="check only these files (staged/edited)")
    parser.add_argument("--update-baseline", action="store_true",
                        help="write the baseline; refuses to raise any count")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--check-raise", metavar="BASE_REF",
                        help="fail when the baseline rose against BASE_REF without a changed, "
                        "reasoned note line per raise (see the module docstring)")
    args = parser.parse_args(argv)
    if args.check_raise:
        try:
            root = Path(args.root).resolve()
            config_path = Path(args.config)
            config_path = config_path if config_path.is_absolute() else root / config_path
            code, lines = check_raise(root, config_path, args.check_raise)
        except ConfigError as exc:
            print(f"ERROR {exc}", file=sys.stderr)
            return 2
        print("\n".join(lines), file=sys.stderr if code else sys.stdout)
        return code
    try:
        code, result = run(args)
        messages = {}
        try:
            cfg_path = Path(args.config)
            cfg_path = cfg_path if cfg_path.is_absolute() else Path(args.root).resolve() / cfg_path
            messages = {r["id"]: r.get("message", "")
                        for r in load_json(cfg_path, "config").get("rules", [])}
        except ConfigError:
            pass
    except ConfigError as exc:
        if args.json:
            print(json.dumps({"status": "error", "error": str(exc)}))
        else:
            print(f"ERROR {exc}", file=sys.stderr)
        return 2
    if args.json:
        printable = dict(result)
        printable["lines"] = {f"{r}::{f}": n for (r, f), n in result.get("lines", {}).items()}
        printable["exit"] = code
        print(json.dumps(printable, indent=2, sort_keys=True))
    else:
        print(render_text(code, result, messages), file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
