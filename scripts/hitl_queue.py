#!/usr/bin/env python3
"""Validate and migrate the local human-in-the-loop queue (AMH-001 FR-2, FR-3).

validate: checks every queue file under HITL/OPERATOR/ and skips cleanly (exit 0)
          when none exists, as on a fresh clone or in CI.
migrate:  copies open items from a named source file into the queue. Without --yes
          it only lists what it would copy. It never edits the source file.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

COLUMNS = [
    "Item", "Type", "Role", "Ref", "Unblocks", "Cost if wrong",
    "Reversibility", "Recommendation", "Raised", "Due", "Record",
]
TYPES = {"decision", "action", "observation"}
REVERSIBILITY = {"cheap", "costly", "one-way"}
EMPTY_OK = {"Unblocks", "Cost if wrong", "Recommendation", "Due"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def valid_date(value: str) -> bool:
    if not DATE.match(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True
REF = re.compile(r"^(#\d+|local|pending)$")
RECORD = re.compile(r"^(#\d+|ADR-\d+|STATUS)$")
QUEUE_DIR = Path("HITL/OPERATOR")
QUEUE_NAME = re.compile(r"^(Master|[A-Za-z0-9][A-Za-z0-9-]*)-TODO\.md$")


def split_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", body)]


def queue_files(root: Path) -> list[Path]:
    folder = root / QUEUE_DIR
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir() if p.is_file() and QUEUE_NAME.match(p.name))


def check_table(text: str, label: str) -> list[str]:
    errors: list[str] = []
    lines = [ln for ln in text.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return [f"{label}: no table found"]
    header = split_row(lines[0])
    if header != COLUMNS:
        return [f"{label}: columns must be exactly {COLUMNS}, found {header}"]
    sep = split_row(lines[1])
    if len(sep) != len(COLUMNS) or not all(re.fullmatch(r":?-{3,}:?", c) for c in sep):
        errors.append(f"{label}: line 2 of the table must be the separator row")
    for number, line in enumerate(lines[2:], start=3):
        cells = split_row(line)
        where = f"{label} row {number - 2}"
        if len(cells) != len(COLUMNS):
            errors.append(f"{where}: {len(cells)} cells, expected {len(COLUMNS)}")
            continue
        row = dict(zip(COLUMNS, cells))
        for name, value in row.items():
            if not value and name not in EMPTY_OK:
                errors.append(f"{where}: {name} is empty")
            elif not value:
                errors.append(f"{where}: {name} is empty; write - for none")
        if row["Type"] and row["Type"] not in TYPES:
            errors.append(f"{where}: unknown Type {row['Type']!r}")
        if row["Reversibility"] and row["Reversibility"] not in REVERSIBILITY:
            errors.append(f"{where}: unknown Reversibility {row['Reversibility']!r}")
        if row["Ref"] and not REF.match(row["Ref"]):
            errors.append(f"{where}: Ref must be #N, local or pending")
        if row["Record"] and not RECORD.match(row["Record"]):
            errors.append(f"{where}: Record must be #N, ADR-NNN or STATUS")
        if row["Raised"] and not valid_date(row["Raised"]):
            errors.append(f"{where}: Raised must be YYYY-MM-DD")
        if row["Due"] not in ("", "-") and not valid_date(row["Due"]):
            errors.append(f"{where}: Due must be YYYY-MM-DD or -")
    return errors


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def validate(root: Path) -> int:
    files = queue_files(root)
    if not files:
        print("hitl queue: none present, skipped")
        return 0
    errors: list[str] = []
    in_git = git(root, "rev-parse", "--git-dir").returncode == 0
    for path in files:
        rel = path.relative_to(root).as_posix()
        if in_git:
            if git(root, "ls-files", "--error-unmatch", rel).returncode == 0:
                errors.append(f"{rel}: is tracked by git; queue files must never be committed")
            if git(root, "check-ignore", "-q", rel).returncode != 0:
                errors.append(f"{rel}: is not git-ignored")
        errors += check_table(path.read_text(encoding="utf-8"), rel)
    for err in errors:
        print(f"ERROR: {err}", file=sys.stderr)
    if errors:
        return 1
    print(f"hitl queue: {len(files)} file(s) valid")
    return 0


ISSUE_LINK = re.compile(r"/issues/(\d+)")


def clean(cell: str) -> str:
    return re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell).replace("|", "/").strip()


def source_items(text: str) -> tuple[list[dict], list[str]]:
    """Open items from tables headed Decision/Item and from unchecked checkboxes."""
    items: list[dict] = []
    problems: list[str] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and i + 1 < len(lines):
            head = [h.lower() for h in split_row(line)]
            if head and head[0] in ("decision", "item") and "reversibility" in head and re.search(r"-{3,}", lines[i + 1]):
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith("|"):
                    cells = split_row(lines[j])
                    row = dict(zip(head, cells))
                    raw = row.get(head[0], "")
                    link = ISSUE_LINK.search(raw)
                    rev = clean(row.get("reversibility", "")).lower()
                    if rev not in REVERSIBILITY:
                        problems.append(f"line {j + 1}: Reversibility missing or unknown; not copied")
                    else:
                        items.append({
                            "Item": clean(raw),
                            "Type": "decision" if head[0] == "decision" else "action",
                            "Ref": f"#{link.group(1)}" if link else "local",
                            "Unblocks": clean(row.get("unblocks", "")) or "-",
                            "Reversibility": rev,
                            "Recommendation": clean(row.get("recommendation", "")) or "-",
                        })
                    j += 1
                i = j
                continue
        m = re.match(r"^\s*[-*] \[ \] (.+)$", line)
        if m:
            problems.append(f"line {i + 1}: checkbox has no Reversibility; not copied")
        i += 1
    return items, problems


def migrate(root: Path, source: Path, queue: str, role: str, yes: bool, today: str) -> int:
    text = source.read_bytes().decode("utf-8")
    items, problems = source_items(text)
    for p in problems:
        print(f"SKIP: {p}", file=sys.stderr)
    target = root / QUEUE_DIR / queue
    rows = []
    for it in items:
        record = it["Ref"] if it["Ref"].startswith("#") else "STATUS"
        rows.append([
            it["Item"], it["Type"], role, it["Ref"], it["Unblocks"], "-",
            it["Reversibility"], it["Recommendation"], today, "-", record,
        ])
    print(f"{len(rows)} open item(s) from {source.name}; target {target.relative_to(root)}")
    if not yes:
        print("dry run: pass --yes to copy; the source file is never edited")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    added = 0
    if target.exists():
        body = target.read_text(encoding="utf-8")
        errs = check_table(body, target.name)
        if errs:
            print("\n".join(errs), file=sys.stderr)
            return 1
        out = body.rstrip("\n") + "\n"
    else:
        out = "| " + " | ".join(COLUMNS) + " |\n| " + " | ".join("---" for _ in COLUMNS) + " |\n"
    existing = set()
    if target.exists():
        for ln in out.splitlines()[2:]:
            c = split_row(ln)
            if len(c) == len(COLUMNS):
                existing.add((c[0], c[3]))
    for r in rows:
        if (r[0].replace("|", "/"), r[3]) in existing:
            print(f"already present: {r[0][:60]}")
            continue
        existing.add((r[0].replace("|", "/"), r[3]))
        added += 1
        out += "| " + " | ".join(c.replace("|", "/") for c in r) + " |\n"
    target.write_text(out, encoding="utf-8")
    print(f"wrote {added} row(s)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("--root", default=".")
    m = sub.add_parser("migrate")
    m.add_argument("--root", default=".")
    m.add_argument("--source", required=True)
    m.add_argument("--queue", default="Master-TODO.md")
    m.add_argument("--role", default="operator")
    m.add_argument("--yes", action="store_true")
    m.add_argument("--today", default=date.today().isoformat())
    a = p.parse_args()
    root = Path(a.root).resolve()
    if a.cmd == "validate":
        return validate(root)
    if not QUEUE_NAME.match(a.queue):
        print("ERROR: --queue must be Master-TODO.md or <gh-id>-TODO.md", file=sys.stderr)
        return 2
    return migrate(root, Path(a.source), a.queue, a.role, a.yes, a.today)


if __name__ == "__main__":
    sys.exit(main())
