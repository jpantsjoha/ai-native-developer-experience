#!/usr/bin/env python3
"""Read-only inspection of an existing repository to pre-fill an operating profile.

Emits `inferred` findings — machine guesses, each backed by an evidence pointer — for the
seven project-awareness areas. Guarantees:

- **Read-only.** It only reads files; it never writes to the target repository.
- **Never infers authority.** Roles, accountability, and approval rights are never
  guessed. `CODEOWNERS` handles are surfaced as *candidates* only, at low confidence.
- **Vendor-neutral.** Detectors are a plain list, easy to extend; no stack is privileged.

The output is a review surface: each finding renders the exact
`inferred — source: <evidence>; confirm: <role>` string to paste into the profile, where a
named human confirms it (replacing it with a verified fact) before the profile can become
`active`. Unconfirmed inference blocks promotion (enforced by validate_operating_model.py).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    """One machine-inferred profile value with its evidence and required confirmer."""

    area: int
    field: str
    value: str
    evidence: str
    confidence: str  # high | medium | low
    confirm: str  # role that must confirm before `active`

    def as_profile_value(self) -> str:
        return f"inferred — source: {self.evidence}; confirm: {self.confirm}"


AREA_NAMES = {
    1: "Vision & scope",
    2: "Team & roster",
    3: "Technical stack",
    4: "Tooling",
    5: "Cloud & governance",
    6: "Automation",
    7: "Delivery controls",
}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def inspect_vision(repo: Path) -> list[Finding]:
    readme = repo / "README.md"
    if not readme.is_file():
        return []
    for line in _read(readme).splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return [
                Finding(
                    1, "Product vision (from README title)", stripped[2:].strip(),
                    "README.md", "low", "product owner",
                )
            ]
    return []


def inspect_team(repo: Path) -> list[Finding]:
    for rel in ("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"):
        codeowners = repo / rel
        if not codeowners.is_file():
            continue
        handles = sorted(set(re.findall(r"@([\w./-]+)", _read(codeowners))))
        if not handles:
            return []
        # Names are candidates only. Role and authority are never inferred.
        return [
            Finding(
                2, "Roster candidates (role/authority NOT inferred)",
                ", ".join("@" + handle for handle in handles[:10]),
                rel, "low", "product owner",
            )
        ]
    return []


def inspect_stack(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    package = repo / "package.json"
    if package.is_file():
        try:
            data = json.loads(_read(package) or "{}")
        except json.JSONDecodeError:
            data = {}
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        language = "TypeScript" if (repo / "tsconfig.json").is_file() or "typescript" in deps else "JavaScript"
        findings.append(Finding(3, "Language", language, "package.json", "high", "lead architect"))
        framework = None
        for name, label in (
            ("react", "React"), ("vue", "Vue"), ("@angular/core", "Angular"),
            ("next", "Next.js"), ("svelte", "Svelte"), ("express", "Express"),
        ):
            if name in deps:
                framework = label
                break
        if "vscode" in (data.get("engines") or {}) or data.get("contributes"):
            framework = "VS Code extension"
        if framework:
            findings.append(Finding(3, "Framework", framework, "package.json", "high", "lead architect"))
    if (repo / "pyproject.toml").is_file() or (repo / "requirements.txt").is_file():
        evidence = "pyproject.toml" if (repo / "pyproject.toml").is_file() else "requirements.txt"
        findings.append(Finding(3, "Language", "Python", evidence, "high", "lead architect"))
        text = _read(repo / evidence).lower()
        for name, label in (("django", "Django"), ("fastapi", "FastAPI"), ("flask", "Flask")):
            if name in text:
                findings.append(Finding(3, "Framework", label, evidence, "medium", "lead architect"))
                break
    if (repo / "go.mod").is_file():
        findings.append(Finding(3, "Language", "Go", "go.mod", "high", "lead architect"))
    if (repo / "Cargo.toml").is_file():
        findings.append(Finding(3, "Language", "Rust", "Cargo.toml", "high", "lead architect"))
    if (repo / "pom.xml").is_file() or (repo / "build.gradle").is_file():
        evidence = "pom.xml" if (repo / "pom.xml").is_file() else "build.gradle"
        findings.append(Finding(3, "Language", "Java/JVM", evidence, "high", "lead architect"))
    if (repo / "Dockerfile").is_file():
        findings.append(Finding(3, "Runtime", "Containerised (Docker)", "Dockerfile", "high", "lead architect"))
    return findings


def inspect_tooling(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    detectors = (
        ("Linter", (".eslintrc", ".eslintrc.json", ".eslintrc.js", ".eslintrc.cjs", ".ruff.toml", "ruff.toml", ".flake8", ".rubocop.yml")),
        ("Formatter", (".prettierrc", ".prettierrc.json", ".prettierrc.js")),
        ("Type checker", ("tsconfig.json", "mypy.ini")),
        ("Test framework", ("pytest.ini", "tox.ini", "jest.config.js", "jest.config.ts", "vitest.config.ts")),
    )
    for field_name, files in detectors:
        for candidate in files:
            if (repo / candidate).is_file():
                findings.append(Finding(4, field_name, f"present ({candidate})", candidate, "medium", "lead developer"))
                break
    makefile = repo / "Makefile"
    if makefile.is_file():
        targets = sorted(set(re.findall(r"(?m)^([A-Za-z][\w-]*):", _read(makefile))))
        if targets:
            findings.append(Finding(4, "Make targets", ", ".join(targets[:12]), "Makefile", "high", "lead developer"))
    return findings


def inspect_cloud(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    has_tf = any(repo.glob("*.tf")) or any(
        (repo / d).is_dir() and any((repo / d).glob("*.tf"))
        for d in ("terraform", "infra", "infrastructure", "deploy")
    )
    if has_tf:
        findings.append(Finding(5, "Infrastructure as code", "Terraform (*.tf present)", "*.tf", "medium", "head of data / security"))
    manifests = "".join(_read(repo / m).lower() for m in ("package.json", "requirements.txt", "pyproject.toml", "go.mod"))
    for needle, label in (("google-cloud", "Google Cloud"), ("boto3", "AWS"), ("aws-sdk", "AWS"), ("azure-", "Azure")):
        if needle in manifests:
            findings.append(Finding(5, "Cloud vendor (from dependencies)", label, "dependency manifest", "low", "lead architect"))
            break
    return findings


def inspect_automation(repo: Path) -> list[Finding]:
    workflows = repo / ".github" / "workflows"
    if workflows.is_dir():
        names = sorted(p.name for p in workflows.glob("*.y*ml"))
        if names:
            listed = ", ".join(names[:6])
            return [Finding(6, "CI/CD", f"GitHub Actions ({len(names)} workflow(s): {listed})", ".github/workflows/", "high", "operations / SRE")]
    return []


def inspect_delivery(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    for rel, label in (("CONTRIBUTING.md", "CONTRIBUTING.md"), (".github/PULL_REQUEST_TEMPLATE.md", "PR template")):
        if (repo / rel).is_file():
            findings.append(Finding(7, "Contribution convention", label, rel, "medium", "delivery lead"))
    for adr_dir in ("ADR", "docs/adr", "docs/adrs", "architecture/decisions"):
        directory = repo / adr_dir
        if directory.is_dir() and any(directory.glob("*.md")):
            findings.append(Finding(7, "Existing ADR location", adr_dir, adr_dir, "high", "delivery lead"))
            break
    return findings


INSPECTORS = (
    inspect_vision, inspect_team, inspect_stack,
    inspect_tooling, inspect_cloud, inspect_automation, inspect_delivery,
)


def inspect(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    for inspector in INSPECTORS:
        findings.extend(inspector(repo))
    return findings


def render(findings: list[Finding]) -> str:
    if not findings:
        return "No inferable evidence found. Ground every profile field from the team.\n"
    lines = [
        "# Inferred profile findings (review required)",
        "",
        "Each finding is a machine guess backed by an evidence pointer. Paste the marker",
        "into the operating profile, then a named human confirms it (replaces it with a",
        "verified fact) before the profile can become `active`. Authority, roles, and",
        "accountability are never inferred.",
        "",
    ]
    by_area: dict[int, list[Finding]] = {}
    for finding in findings:
        by_area.setdefault(finding.area, []).append(finding)
    for area in sorted(by_area):
        lines.append(f"## Area {area} — {AREA_NAMES.get(area, '')}")
        lines.append("")
        for finding in by_area[area]:
            lines.append(f"- **{finding.field}**: {finding.value}")
            lines.append(f"  `{finding.as_profile_value()}` _(confidence: {finding.confidence})_")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only repository inspection for operating-profile backfill."
    )
    parser.add_argument("repo", nargs="?", default=".", help="Path to the existing repository.")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"error: {repo} is not a directory", file=sys.stderr)
        return 2
    print(render(inspect(repo)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
