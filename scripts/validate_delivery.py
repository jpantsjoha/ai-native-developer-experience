#!/usr/bin/env python3
"""Offline structural delivery gate; validates records, never executes their commands.

Policy inventories canonical documents and Markdown record roots; records own state.
PASS proves the declared structural checks only, not semantic truth or approval.
See docs/DETERMINISTIC-GATES.md for the supported Markdown grammar and trust boundary.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ID = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[0-9]+")
STATES = {
    "spec": {"Draft", "Accepted", "In progress", "In review", "Done", "Blocked", "Superseded"},
    "epic": {"Draft", "Accepted", "Ready", "In progress", "In review", "Done", "Blocked", "Parked", "Superseded"},
    "task": {"Proposed", "Ready", "In progress", "In review", "Done", "Blocked", "Parked", "Superseded"},
    "decision": {"Proposed", "Accepted", "Rejected", "Superseded"},
}
SCOPE = "offline structural delivery records; not execution, approval or release proof"


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    """Reject duplicate JSON keys instead of accepting last-value-wins policies."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def prose(text: str) -> tuple[str, list[str]]:
    """Mask supported examples; refuse ambiguous/multiline inline-code syntax.

    A deliberately narrow grammar avoids guessing CommonMark block precedence.
    Exact single-line code spans are masked before interpreting comment openers.
    """
    output = []
    errors = []
    fence = None
    i = 0
    while i < len(text):
        if i == 0 or text[i - 1] == "\n":
            end = text.find("\n", i)
            end = len(text) if end < 0 else end + 1
            line = text[i:end]
            marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\n"))
            if fence:
                if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                    fence = None
                output.append("\n" if line.endswith("\n") else "")
                i = end
                continue
            if marker or line.startswith(("    ", "\t")):
                fence = marker[1] if marker else None
                output.append("\n" if line.endswith("\n") else "")
                i = end
                continue
        if text.startswith("<!--", i):
            end = text.find("-->", i + 4)
            end = len(text) if end < 0 else end + 3
            output.append("\n" * text[i:end].count("\n"))
            i = end
        elif text[i] == "\\" and i + 1 < len(text):
            # Preserve escapes so they cannot introduce comment/code delimiters.
            output.append(text[i:i + 2])
            i += 2
        elif text[i] == "`":
            end = i
            while end < len(text) and text[end] == "`":
                end += 1
            delimiter = text[i:end]
            limit = text.find("\n", end)
            limit = len(text) if limit < 0 else limit
            close = re.compile(r"(?<!`)" + re.escape(delimiter) + r"(?!`)").search(text, end, limit)
            if close:
                output.append(" " + "\n" * text[i:close.end()].count("\n"))
                i = close.end()
            else:
                line_number = text.count("\n", 0, i) + 1
                errors.append(f"line {line_number}: unmatched or multiline inline backticks; escape a literal or use a fenced example")
                output.append(delimiter)
                i = end
        else:
            output.append(text[i])
            i += 1
    return "".join(output), errors


def fields(text: str, label: str) -> list[str]:
    """Read all single-line bold fields; callers reject missing or duplicate values."""
    return re.findall(rf"^ {{0,3}}\*\*{re.escape(label)}:\*\*[ \t]*(.*)$", text, re.M)


def links(text: str) -> tuple[list[str], list[str]]:
    """Extract inline and defined reference destinations, reporting explicit ambiguity.

    Balanced parentheses and angle destinations are supported. Bare shortcut brackets
    without a definition are ordinary prose; full/collapsed references must resolve.
    """
    definitions = {}
    errors = []
    targets = []
    definition_re = re.compile(r'^ {0,3}\[([^]\n]+)\]:[ \t]*(<[^>\n]+>|\S+)(?:[ \t]+.*)?$', re.M)
    for match in definition_re.finditer(text):
        label = " ".join(match[1].split()).casefold()
        if label in definitions:
            errors.append(f"duplicate reference definition: {label}")
        definitions[label] = match[2].strip("<>")
        targets.append(definitions[label])
    text = definition_re.sub("", text)
    i = 0
    brackets = []
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == "[":
            brackets.append(i + 1)
            i += 1
            continue
        if text[i] != "]" or not brackets:
            i += 1
            continue
        # Process inner labels as they close, even inside ordinary prose brackets.
        start = brackets.pop()
        i += 1
        label = " ".join(text[start:i - 1].split()).casefold()
        if i < len(text) and text[i] == "(":
            i += 1
            start = i
            depth = 1
            angle = False
            quote = None
            while i < len(text) and depth:
                char = text[i]
                if char == "\\":
                    i += 2
                    continue
                if quote:
                    if char == quote:
                        quote = None
                elif char in {"'", '"'} and depth == 1 and i > start and text[i - 1].isspace():
                    quote = char
                elif char == "<":
                    angle = True
                elif char == ">":
                    angle = False
                elif not angle:
                    depth += (char == "(") - (char == ")")
                i += 1
            if depth:
                errors.append(f"unterminated inline link: {label}")
                break
            destination = text[start:i - 1].strip()
            if destination.startswith("<"):
                end = destination.find(">")
                target = destination[1:end] if end >= 0 else ""
            else:
                target = destination.split(maxsplit=1)[0] if destination else ""
            targets.append(re.sub(r"\\([\\()\[\] ])", r"\1", target))
        elif i < len(text) and text[i] == "[":
            end = text.find("]", i + 1)
            if end < 0:
                errors.append(f"unterminated reference: {label}")
                break
            key = " ".join(text[i + 1:end].split()).casefold() or label
            if key not in definitions:
                errors.append(f"undefined reference: {key}")
            i = end + 1
        elif label in definitions:
            targets.append(definitions[label])
    return targets, errors


class Gate:
    """Accumulate stable findings while refusing unsafe paths and incomplete records."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.findings: list[dict[str, str]] = []
        self.texts: dict[Path, str] = {}
        self.records: dict[str, dict] = {}

    def fail(self, code: str, path: object, message: str) -> None:
        """Record a finding without treating an exception as success."""
        if isinstance(path, Path) and path.is_relative_to(self.root):
            path = path.relative_to(self.root)
        finding = {"code": code, "path": str(path), "message": message}
        if finding not in self.findings:
            self.findings.append(finding)

    def visible(self, text: str, path: Path) -> str:
        """Return supported prose and refuse unsupported masking syntax explicitly."""
        masked, errors = prose(text)
        for error in errors:
            self.fail("GRAMMAR", path, error)
        return masked

    def path(self, value: str, base: Path) -> Path | None:
        """Resolve a repository-relative path; symlink and platform escapes refuse."""
        try:
            if not value or "\\" in value or re.match(r"^[A-Za-z]:", value) or Path(value).is_absolute():
                raise ValueError("not a portable relative path")
            path = (base / value).resolve()
            if not path.is_relative_to(self.root):
                raise ValueError("path escapes repository")
            return path
        except (OSError, RuntimeError, ValueError) as exc:
            self.fail("PATH", value, str(exc))
            return None

    def read(self, path: Path) -> str | None:
        """Read bounded UTF-8 regular files; empty/unreadable inputs are findings."""
        if path in self.texts:
            return self.texts[path]
        try:
            if not path.is_file() or path.stat().st_size > 1_000_000:
                raise ValueError("missing, non-regular or over 1 MB")
            text = path.read_text(encoding="utf-8")
            if not text.strip():
                self.fail("EMPTY", path, "required file is empty")
                return None
            self.texts[path] = text
            return text
        except (OSError, UnicodeError, ValueError) as exc:
            self.fail("FILE", path, str(exc))
            return None

    def policy(self, relative: str) -> dict | None:
        """Load a closed, nonempty project inventory with no duplicate JSON keys."""
        path = self.path(relative, self.root)
        text = self.read(path) if path else None
        try:
            policy = json.loads(text or "", object_pairs_hook=unique_object)
            if not isinstance(policy, dict) or set(policy) != {"version", "documents", "records"}:
                raise ValueError("expected version, documents and records only")
            if type(policy["version"]) is not int or policy["version"] != 1:
                raise ValueError("version must be integer 1")
            for key in ("documents", "records"):
                group = policy[key]
                if not isinstance(group, dict) or not group or any(
                    not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip()
                    for k, v in group.items()
                ):
                    raise ValueError(f"{key} must be a nonempty string mapping")
            if not {"vision", "roadmap", "status", "changelog"} <= policy["documents"].keys():
                raise ValueError("documents must name vision, roadmap, status and changelog")
            if not policy["records"].keys() <= STATES.keys():
                raise ValueError("unknown record kind")
            return policy
        except (ValueError, TypeError) as exc:
            self.fail("POLICY", relative, str(exc))
            return None

    def local_link(self, target: str, source: Path) -> Path | None:
        """Check local link existence; never fetch remote URLs or execute anything."""
        try:
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                return None
            path = self.path(unquote(url.path), source.parent)
            if path and not path.exists():
                self.fail("LINK", source, f"missing local target: {target}")
                return None
            return path
        except ValueError as exc:
            self.fail("LINK", source, f"invalid destination: {exc}")
            return None

    def record(self, path: Path, kind: str) -> None:
        """Read one ID/state contract, requiring unambiguous visible metadata."""
        raw = self.read(path)
        if raw is None:
            return
        text = self.visible(raw, path)
        identities = (re.findall(r"^# (ADR-[0-9]+):[^\n]*$", text, re.M) if kind == "decision"
                      else fields(text, {"spec": "Spec ID", "epic": "Epic ID", "task": "Task ID"}[kind]))
        states = fields(text, "Status")
        if kind == "decision":
            states += [s.split(" — ", 1)[0].strip() for s in
                       re.findall(r"^## Status[ \t]*\n(?:[ \t]*\n)*([^\n]+)", text, re.M)]
        if len(identities) != 1 or not ID.fullmatch(identities[0]):
            self.fail("ID", path, "exactly one valid stable ID required")
            return
        identity = identities[0]
        if identity in self.records:
            self.fail("DUPLICATE_ID", path, f"ID already declared: {identity}")
            return
        state = states[0] if len(states) == 1 else ""
        if state not in STATES[kind]:
            self.fail("STATUS", path, f"one recognised {kind} status required")
        record = {"kind": kind, "state": state, "path": path}
        for label, code in (("Parent", "PARENT"), ("Depends on", "DEPENDENCY"),
                            ("Superseded by", "SUPERSESSION"), ("Evidence", "EVIDENCE")):
            values = fields(text, label)
            if len(values) > 1 or (values and not values[0].strip()):
                self.fail(code, path, f"ambiguous/empty {label} metadata")
            record[label] = values[0] if len(values) == 1 else ""
        self.records[identity] = record
        if state == "Done":
            targets, errors = links(record["Evidence"])
            evidence = [self.local_link(t, path) for t in targets]
            valid = bool(evidence) and not errors and all(
                p is not None and p.is_file() and p.stat().st_size > 0 for p in evidence
            )
            if not valid:
                self.fail("EVIDENCE", path, "Done requires nonempty local evidence files; existence is not proof")

    def relationships(self) -> None:
        """Validate references and directed dependency/successor graphs without inference."""
        dependencies = {}
        successors = {}
        for identity, record in self.records.items():
            path = record["path"]
            parent = record["Parent"]
            if record["kind"] == "task" or parent:
                if (record["kind"] != "task" or parent not in self.records
                        or self.records[parent]["kind"] != "epic"):
                    self.fail("PARENT", path, "task Parent must identify an existing epic")
            deps = [v.strip() for v in record["Depends on"].split(",")] if record["Depends on"] else []
            dependencies[identity] = deps
            for dependency in deps:
                if dependency not in self.records or dependency == identity:
                    self.fail("DEPENDENCY", path, f"missing/self dependency: {dependency}")
            successor = record["Superseded by"]
            successors[identity] = [successor] if successor else []
            if record["state"] == "Superseded" or successor:
                if (record["state"] != "Superseded" or successor == identity
                        or successor not in self.records or self.records[successor]["kind"] != record["kind"]):
                    self.fail("SUPERSESSION", path, "Superseded requires a different existing successor of the same kind")
        for graph, code in ((dependencies, "CYCLE"), (successors, "SUPERSESSION")):
            pending = {key: set(values) & graph.keys() for key, values in graph.items()}
            while pending:
                leaves = {key for key, values in pending.items() if not values}
                if not leaves:
                    self.fail(code, ".delivery.json", "cyclic references: " + ", ".join(sorted(pending)))
                    break
                pending = {key: values - leaves for key, values in pending.items() if key not in leaves}

    def run(self, policy_path: str) -> dict:
        """Validate a declared inventory and return machine-readable scoped findings."""
        policy = self.policy(policy_path)
        documents = set()
        visited = set()
        if policy:
            for value in policy["documents"].values():
                path = self.path(value, self.root)
                if path and self.read(path) is not None:
                    documents.add(path)
            for kind, value in policy["records"].items():
                directory = self.path(value, self.root)
                paths = []
                if directory and directory.is_dir():
                    # pathlib glob can suppress scan errors; an incomplete scan must fail.
                    def scan_error(error: OSError) -> None:
                        raise error

                    for parent, directories, filenames in os.walk(directory, onerror=scan_error):
                        for name in directories:
                            if (Path(parent) / name).is_symlink():
                                self.fail("INVENTORY", value, "symlinked record directories are unsupported")
                        paths.extend(Path(parent) / name for name in filenames if name.endswith(".md"))
                    paths.sort()
                if not paths:
                    self.fail("INVENTORY", value, "required record root is missing or contains no Markdown records")
                for source in paths:
                    path = self.path(str(source.relative_to(self.root)), self.root)
                    if not path:
                        continue
                    if path in visited:
                        self.fail("INVENTORY", path, "overlapping record roots or aliases")
                        continue
                    visited.add(path)
                    documents.add(path)
                    self.record(path, kind)
            self.relationships()
            for path in sorted(documents):
                raw = self.read(path)
                if raw is None:
                    continue
                targets, errors = links(self.visible(raw, path))
                for error in errors:
                    self.fail("LINK", path, error)
                for target in targets:
                    self.local_link(target, path)
        return {"status": "FAIL" if self.findings else "PASS", "scope": SCOPE,
                "documents_checked": len(documents), "records_checked": len(self.records),
                "findings": self.findings}


def main() -> int:
    """Run offline validation; findings return 1 and unexpected I/O errors return 2."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--policy", default=".delivery.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = Gate(Path(args.root)).run(args.policy)
        code = 0 if report["status"] == "PASS" else 1
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        report = {"status": "FAIL", "scope": SCOPE, "documents_checked": 0,
                  "records_checked": 0, "findings": [{"code": "HARNESS_ERROR",
                  "path": args.root, "message": str(exc)}]}
        code = 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for finding in report["findings"]:
            print(f"FAIL {finding['code']} {finding['path']}: {finding['message']}", file=sys.stderr)
        print(f"{report['status']} delivery validation: {report['documents_checked']} documents, "
              f"{report['records_checked']} records; {SCOPE}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
