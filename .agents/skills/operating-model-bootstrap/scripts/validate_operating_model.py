#!/usr/bin/env python3
"""Validate an operating-model seed without provider SDKs or YAML dependencies."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


MANUAL_REL = Path("docs/operating-model/OPERATING-MANUAL.md")
PROFILE_REL = Path("docs/operating-model/PROJECT-OPERATING-PROFILE.md")
ADAPTER_NAMES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md")
CONTRACT_START = "<!-- operating-model-contract:start -->"
CONTRACT_END = "<!-- operating-model-contract:end -->"
PLACEHOLDER = re.compile(r"<[^>\n]+>")


@dataclass
class Findings:
    """Collect deterministic failures and non-blocking readiness warnings."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def require(self, condition: bool, message: str) -> None:
        """Record a failed invariant without stopping the remaining audit."""

        if not condition:
            self.errors.append(message)


def sha256(path: Path) -> str:
    """Hash the exact adopted manual bytes."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def bold_field(text: str, label: str) -> str | None:
    """Read one Markdown `**Label:** value` field."""

    match = re.search(rf"^\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$", text, re.MULTILINE)
    return match.group(1).strip(" `") if match else None


def yaml_scalar(text: str, key: str) -> str | None:
    """Read the first simple YAML scalar for a known template key."""

    match = re.search(rf"^\s*{re.escape(key)}:\s*(.*?)\s*$", text, re.MULTILINE)
    return match.group(1).strip(" '\"") if match else None


def protected_contract(text: str, path: Path, findings: Findings) -> str | None:
    """Extract the shared generated block used for cross-surface drift checks."""

    findings.require(
        text.count(CONTRACT_START) == 1, f"{path}: missing/duplicate start marker"
    )
    findings.require(
        text.count(CONTRACT_END) == 1, f"{path}: missing/duplicate end marker"
    )
    if text.count(CONTRACT_START) != 1 or text.count(CONTRACT_END) != 1:
        return None
    block = text.split(CONTRACT_START, 1)[1].split(CONTRACT_END, 1)[0]
    return "\n".join(line.rstrip() for line in block.strip().splitlines())


def validate_manual(path: Path, findings: Findings) -> tuple[str, str]:
    """Validate immutable-kernel metadata and return its version and digest."""

    if not path.is_file():
        findings.errors.append(f"missing adopted manual: {path}")
        return "", ""
    text = path.read_text(encoding="utf-8")
    version = bold_field(text, "Version") or ""
    findings.require(bool(version), f"{path}: missing Version metadata")
    findings.require(
        not PLACEHOLDER.search(text), f"{path}: immutable manual contains a placeholder"
    )
    findings.require(
        "model-, vendor-, and IDE-neutral" in text,
        f"{path}: portability contract is missing",
    )
    return version, sha256(path)


def validate_profile(
    path: Path,
    version: str,
    digest: str,
    require_active: bool,
    findings: Findings,
) -> None:
    """Check profile binding and distinguish a usable seed from active rigor."""

    if not path.is_file():
        findings.errors.append(f"missing project profile: {path}")
        return
    text = path.read_text(encoding="utf-8")
    profile_version = bold_field(text, "Manual version")
    profile_digest = bold_field(text, "Manual SHA-256")
    status = bold_field(text, "Adoption status")
    findings.require(
        profile_version == version,
        f"{path}: manual version does not match adopted manual",
    )
    findings.require(
        profile_digest == digest,
        f"{path}: manual SHA-256 does not match adopted manual",
    )
    findings.require(
        status in {"seed", "active", "superseded"}, f"{path}: invalid adoption status"
    )
    if require_active:
        findings.require(
            status == "active", f"{path}: active profile required, found {status!r}"
        )

    unresolved = sorted(set(PLACEHOLDER.findall(text)))
    if status == "active" or require_active:
        findings.require(
            not unresolved,
            f"{path}: active profile has {len(unresolved)} unresolved placeholders",
        )
    elif unresolved:
        findings.warnings.append(
            f"{path}: seed has {len(unresolved)} placeholder types; resolve the day-one minimum"
        )
    if status == "seed":
        findings.warnings.append(
            f"{path}: seed supports design/R0/R1 only; R2/R3 requires active controls"
        )
    elif status == "superseded":
        findings.warnings.append(
            f"{path}: profile is superseded and must not govern new work"
        )


def validate_adapters(
    paths: list[Path],
    version: str,
    digest: str,
    findings: Findings,
    allow_placeholder_digest: bool = False,
) -> None:
    """Require every installed surface to carry one identical protected contract."""

    findings.require(bool(paths), "no operating-model surface adapter found")
    blocks: dict[Path, str] = {}
    for path in paths:
        if not path.is_file():
            findings.errors.append(f"missing adapter: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        block = protected_contract(text, path, findings)
        if block is None:
            continue
        blocks[path] = block
        findings.require(
            f"Manual version: `{version}`" in block,
            f"{path}: protected block has wrong manual version",
        )
        expected_digest = "<manual-sha256>" if allow_placeholder_digest else digest
        findings.require(
            f"Manual SHA-256: `{expected_digest}`" in block,
            f"{path}: protected block has wrong manual digest",
        )
        if not allow_placeholder_digest:
            findings.require(
                not PLACEHOLDER.search(block),
                f"{path}: protected block has a placeholder",
            )

    findings.require(
        len(set(blocks.values())) <= 1,
        "surface adapter protected blocks have semantic drift",
    )


def validate_task_artifact(
    path: Path, version: str, digest: str, kind: str, findings: Findings
) -> str | None:
    """Check a resolved checkpoint/evidence file and return candidate identity."""

    if not path.is_file():
        findings.errors.append(f"missing {kind}: {path}")
        return None
    text = path.read_text(encoding="utf-8")
    findings.require(
        not PLACEHOLDER.search(text), f"{path}: unresolved task placeholders"
    )
    findings.require(
        yaml_scalar(text, "manual_version") == version, f"{path}: wrong manual version"
    )
    findings.require(
        yaml_scalar(text, "manual_sha256") == digest, f"{path}: wrong manual digest"
    )
    if kind == "checkpoint":
        findings.require(
            yaml_scalar(text, "risk_tier") in {"R0", "R1", "R2", "R3"},
            f"{path}: invalid risk tier",
        )
        candidate = yaml_scalar(text, "candidate_sha_or_tree_digest")
    else:
        candidate = yaml_scalar(text, "sha_or_digest")
    findings.require(
        bool(candidate and candidate.strip()), f"{path}: missing candidate identity"
    )
    return candidate


def validate_templates(root: Path, findings: Findings) -> None:
    """Validate the distributed source assets before they are installed elsewhere."""

    manual = root / "assets" / "OPERATING-MANUAL.md"
    version, _ = validate_manual(manual, findings)
    expected = {
        "PROJECT-OPERATING-PROFILE.template.md": (
            "Manual SHA-256",
            "Day-one seed minimum",
        ),
        "CHECKPOINT.template.yaml": (
            "candidate_sha_or_tree_digest",
            "RISK_CLASSIFIED|AUTHORIZED",
        ),
        "EVIDENCE-MANIFEST.template.yaml": ("candidate:", "review:"),
    }
    for filename, markers in expected.items():
        path = root / "assets" / filename
        if not path.is_file():
            findings.errors.append(f"missing source template: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            findings.require(
                marker in text, f"{path}: missing required marker {marker!r}"
            )
        findings.require(
            bool(PLACEHOLDER.search(text)),
            f"{path}: template has no adoption placeholders",
        )
        findings.require(
            yaml_scalar(text, "manual_version") == version
            if filename.endswith(".yaml")
            else bold_field(text, "Manual version") == version,
            f"{path}: source template has wrong manual version",
        )

    planning_seed = {
        "VISION.template.md": ("## Current focus", "Product Owner"),
        "DELIVERY-WORKFLOW.template.md": ("## Lifecycle", "Re-planning trigger"),
        "ROADMAP.template.md": ("## Now", "Product Owner gate"),
        "STATUS.template.md": ("## Blocked", "## Plan changes"),
        "CHANGELOG.template.md": ("## Unreleased", "### Added"),
    }
    for filename, markers in planning_seed.items():
        path = root / "assets" / filename
        if not path.is_file():
            findings.errors.append(f"missing planning seed template: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            findings.require(
                marker in text, f"{path}: missing required marker {marker!r}"
            )
        if filename != "CHANGELOG.template.md":
            findings.require(
                bool(PLACEHOLDER.search(text)),
                f"{path}: template has no adoption placeholders",
            )

    adapters = [
        root / "assets" / "adapters" / f"{name}.template" for name in ADAPTER_NAMES
    ]
    validate_adapters(adapters, version, "", findings, allow_placeholder_digest=True)


def parse_args() -> argparse.Namespace:
    """Parse validation mode and optional exact task artifacts."""

    parser = argparse.ArgumentParser(
        description="Validate operating-model coherence and binding."
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Adopted project root (default: current directory).",
    )
    parser.add_argument(
        "--template-root", help="Validate the skill source directory instead."
    )
    parser.add_argument(
        "--require-active", action="store_true", help="Reject seed/superseded profiles."
    )
    parser.add_argument(
        "--adapter",
        action="append",
        help="Adapter path relative to target; repeatable.",
    )
    parser.add_argument(
        "--checkpoint",
        action="append",
        default=[],
        help="Resolved checkpoint; repeatable.",
    )
    parser.add_argument(
        "--evidence",
        action="append",
        default=[],
        help="Resolved evidence manifest; repeatable.",
    )
    return parser.parse_args()


def main() -> int:
    """Run all applicable checks and emit a stable pass/fail summary."""

    args = parse_args()
    findings = Findings()
    if args.template_root:
        validate_templates(Path(args.template_root).expanduser().resolve(), findings)
    else:
        target = Path(args.target).expanduser().resolve()
        if not target.is_dir():
            print(f"ERROR target is not a directory: {target}", file=sys.stderr)
            return 2
        version, digest = validate_manual(target / MANUAL_REL, findings)
        validate_profile(
            target / PROFILE_REL, version, digest, args.require_active, findings
        )
        adapters = (
            [target / path for path in args.adapter]
            if args.adapter
            else [target / name for name in ADAPTER_NAMES if (target / name).is_file()]
        )
        validate_adapters(adapters, version, digest, findings)

        checkpoint_candidates = [
            validate_task_artifact(
                target / path, version, digest, "checkpoint", findings
            )
            for path in args.checkpoint
        ]
        evidence_candidates = [
            validate_task_artifact(target / path, version, digest, "evidence", findings)
            for path in args.evidence
        ]
        if checkpoint_candidates or evidence_candidates:
            findings.require(
                len(checkpoint_candidates) == len(evidence_candidates),
                "checkpoint and evidence manifest counts differ",
            )
            for index, (checkpoint_candidate, evidence_candidate) in enumerate(
                zip(checkpoint_candidates, evidence_candidates, strict=False), start=1
            ):
                findings.require(
                    checkpoint_candidate == evidence_candidate,
                    f"checkpoint/evidence pair {index} bind to different candidates",
                )

    for warning in findings.warnings:
        print(f"WARN {warning}")
    for error in findings.errors:
        print(f"FAIL {error}", file=sys.stderr)
    if findings.errors:
        print(
            f"FAIL operating-model validation: {len(findings.errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print(f"PASS operating-model validation ({len(findings.warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
