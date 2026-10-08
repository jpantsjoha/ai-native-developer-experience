#!/usr/bin/env python3
"""Validate an operating-model seed without provider SDKs or YAML dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
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
# A machine-backfilled field: `inferred — source: <evidence>; confirm: <role>`.
# Inference supports design/R0/R1 but must be human-confirmed before `active`.
INFERRED = re.compile(r"\binferred\s*[—–-]\s*source\s*:", re.IGNORECASE)


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

    inferred = INFERRED.findall(text)
    if status == "active" or require_active:
        findings.require(
            not inferred,
            f"{path}: active profile has {len(inferred)} unconfirmed inferred field(s); "
            "a human must verify each before promotion to active",
        )
    elif inferred:
        findings.warnings.append(
            f"{path}: seed has {len(inferred)} inferred field(s) awaiting human confirmation"
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



RELEASE_FIELDS = {
    "mode": "Release mode",
    "build_trigger": "Build trigger",
    "build_executor": "Build executor",
    "promotion_trigger": "Promotion trigger",
    "release_owner": "Release owner",
    "release_decision": "Release decision",
}
RELEASE_RECEIPTS = {"approval", "build", "validation", "review", "rollback", "observation_plan"}


def release_file(target: Path, value: object, label: str, findings: Findings) -> Path | None:
    """Resolve a nonempty local receipt; absolute paths and escaping symlinks fail."""

    if not isinstance(value, str) or not value.strip() or Path(value).is_absolute():
        findings.errors.append(f"release {label}: expected project-relative file")
        return None
    try:
        path = (target / value).resolve()
        if not path.is_relative_to(target):
            raise ValueError("outside project")
        if not path.is_file():
            findings.errors.append(f"release {label}: missing file {value}")
            return None
        if not path.read_bytes().strip():
            findings.errors.append(f"release {label}: empty file {value}")
            return None
        return path
    except (OSError, ValueError, RuntimeError):
        findings.errors.append(f"release {label}: unreadable or non-project-relative file")
        return None


def unique_json_object(pairs: list[tuple[str, object]]) -> dict:
    """Reject duplicate JSON keys rather than silently trusting the last value."""

    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def validate_release(target: Path, evidence: str, candidate: str, findings: Findings) -> None:
    """Check declared release structure only; neither receipts nor authority are authenticated."""

    profile = target / PROFILE_REL
    if not profile.is_file():
        return  # validate_profile already reports this
    text = profile.read_text(encoding="utf-8")
    policy = {}
    for key, label in RELEASE_FIELDS.items():
        matches = re.findall(rf"^\*\*{label}:\*\*[^\S\n]*(.*?)\s*$", text, re.MULTILINE)
        value = matches[0].strip(" `") if len(matches) == 1 else ""
        findings.require(bool(value) and not PLACEHOLDER.search(value),
                         f"release policy: {label} must have one resolved value")
        policy[key] = value
    findings.require(policy["mode"] in {"tag-ci", "approved-alternative"},
                     "release policy: unknown release mode")
    findings.require(policy["build_trigger"] in {"tag", "manual", "pipeline"},
                     "release policy: unknown build trigger")
    findings.require(policy["build_executor"] in {"ci", "controlled-runner"},
                     "release policy: unknown build executor")
    findings.require(policy["promotion_trigger"] in {"tag", "separate-approval"},
                     "release policy: unknown promotion trigger")
    if policy["mode"] == "tag-ci":
        findings.require(policy["build_trigger"] == "tag" and policy["build_executor"] == "ci",
                         "release policy: tag-ci requires tag build trigger and ci executor")
    if policy["promotion_trigger"] == "tag":
        findings.require(policy["build_trigger"] == "tag",
                         "release policy: tag promotion requires tag build trigger")
    decision = release_file(target, policy["release_decision"], "decision", findings)
    findings.require(bool(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", candidate)),
                     "release candidate: expected full SHA-1 or SHA-256 identity")
    path = release_file(target, evidence, "evidence record", findings)
    if path is None:
        return
    try:
        record = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_json_object)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        findings.errors.append(f"release evidence: invalid JSON ({type(exc).__name__})")
        return
    fields = {"schema_version", "policy", "candidate", "artifact_sha256", "decision_sha256",
              "review_candidate", "review_verdict", "receipts"}
    if not isinstance(record, dict) or set(record) != fields:
        findings.errors.append("release evidence: missing or unknown fields")
        return
    findings.require(type(record["schema_version"]) is int and record["schema_version"] == 1,
                     "release evidence: unsupported schema_version")
    findings.require(decision is not None and record["decision_sha256"] == sha256(decision),
                     "release evidence: decision digest differs from current decision")
    findings.require(record["policy"] == policy, "release evidence: policy differs from profile")
    findings.require(record["candidate"] == candidate and record["review_candidate"] == candidate,
                     "release evidence: candidate/review identity differs from requested candidate")
    artifact = record["artifact_sha256"]
    findings.require(isinstance(artifact, str) and bool(re.fullmatch(r"[0-9a-f]{64}", artifact)),
                     "release evidence: missing or invalid artifact_sha256")
    findings.require(record["review_verdict"] == "PASS", "release evidence: review must be PASS")
    receipts = record["receipts"]
    if not isinstance(receipts, dict) or set(receipts) != RELEASE_RECEIPTS:
        findings.errors.append("release receipts: missing or unknown required receipts")
        return
    for key, value in receipts.items():
        release_file(target, value, key, findings)


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
    parser.add_argument("--release-evidence", help="Release preflight JSON, relative to target.")
    parser.add_argument("--candidate", help="Expected full release candidate SHA/tree digest.")
    args = parser.parse_args()
    if (args.release_evidence is None) != (args.candidate is None):
        parser.error("--release-evidence and --candidate must be supplied together")
    if args.release_evidence is not None and (not args.release_evidence.strip() or not args.candidate.strip()):
        parser.error("release evidence and candidate must be nonempty")
    if args.template_root and args.release_evidence:
        parser.error("release preflight requires --target, not --template-root")
    return args


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
            target / PROFILE_REL, version, digest, args.require_active or bool(args.release_evidence), findings
        )
        if args.release_evidence:
            validate_release(target, args.release_evidence, args.candidate, findings)
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
    if args.release_evidence:
        print("PASS release structure only — not approval, authenticated evidence or observed delivery")
    print(f"PASS operating-model validation ({len(findings.warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
