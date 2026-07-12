#!/usr/bin/env python3
"""Install a safe, version-bound operating-model seed into a target repository."""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


MANUAL_VERSION = "2.1.0"
SURFACE_FILES = {
    "agents": "AGENTS.md",
    "claude": "CLAUDE.md",
    "gemini": "GEMINI.md",
}


@dataclass(frozen=True)
class Artifact:
    """One destination and the exact bytes the initializer intends to write."""

    destination: Path
    content: bytes


def sha256(content: bytes) -> str:
    """Return a lowercase SHA-256 digest for immutable content."""

    return hashlib.sha256(content).hexdigest()


def parse_args() -> argparse.Namespace:
    """Parse the deliberately small, non-destructive initializer interface."""

    parser = argparse.ArgumentParser(
        description="Install the day-one operating-model seed without overwriting files."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target project directory (default: current directory).",
    )
    parser.add_argument(
        "--project-name",
        help="Project name written into the profile (default: target directory name).",
    )
    parser.add_argument(
        "--surface",
        action="append",
        choices=(*SURFACE_FILES, "all"),
        help="Adapter to install; repeat as needed (default: all three).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preflight every destination without writing anything.",
    )
    return parser.parse_args()


def selected_surfaces(values: list[str] | None) -> list[str]:
    """Resolve repeated surface flags into a stable, de-duplicated list."""

    if not values or "all" in values:
        return list(SURFACE_FILES)
    return [name for name in SURFACE_FILES if name in values]


def render_artifacts(
    target: Path, project_name: str, surfaces: list[str]
) -> list[Artifact]:
    """Render all output in memory so conflicts are found before the first write."""

    skill_root = Path(__file__).resolve().parent.parent
    assets = skill_root / "assets"
    manual = (assets / "OPERATING-MANUAL.md").read_bytes()
    manual_digest = sha256(manual)
    today = date.today().isoformat()

    profile = (assets / "PROJECT-OPERATING-PROFILE.template.md").read_text(
        encoding="utf-8"
    )
    replacements = {
        "<Project Name>": project_name,
        "<digest>": manual_digest,
        "<seed|active|superseded>": "seed",
        "<YYYY-MM-DD>": today,
    }
    for original, replacement in replacements.items():
        profile = profile.replace(original, replacement)

    operating_root = target / "docs" / "operating-model"
    rendered = [
        Artifact(operating_root / "OPERATING-MANUAL.md", manual),
        Artifact(
            operating_root / "PROJECT-OPERATING-PROFILE.md",
            profile.encode("utf-8"),
        ),
        Artifact(
            operating_root / "templates" / "CHECKPOINT.template.yaml",
            (assets / "CHECKPOINT.template.yaml").read_bytes(),
        ),
        Artifact(
            operating_root / "templates" / "EVIDENCE-MANIFEST.template.yaml",
            (assets / "EVIDENCE-MANIFEST.template.yaml").read_bytes(),
        ),
    ]

    for surface in surfaces:
        adapter = (
            assets / "adapters" / f"{SURFACE_FILES[surface]}.template"
        ).read_text(encoding="utf-8")
        adapter = adapter.replace("<manual-sha256>", manual_digest)
        rendered.append(
            Artifact(target / SURFACE_FILES[surface], adapter.encode("utf-8"))
        )

    return rendered


def preflight(artifacts: list[Artifact]) -> tuple[list[Artifact], list[Path]]:
    """Return new outputs and conflicting existing outputs; identical files are safe."""

    pending: list[Artifact] = []
    conflicts: list[Path] = []
    for artifact in artifacts:
        if not artifact.destination.exists():
            pending.append(artifact)
        elif artifact.destination.read_bytes() != artifact.content:
            conflicts.append(artifact.destination)
    return pending, conflicts


def main() -> int:
    """Preflight the full file set, then install without overwriting any file."""

    args = parse_args()
    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        print(f"ERROR target is not a directory: {target}", file=sys.stderr)
        return 2

    surfaces = selected_surfaces(args.surface)

    artifacts = render_artifacts(target, args.project_name or target.name, surfaces)
    pending, conflicts = preflight(artifacts)
    if conflicts:
        print("ERROR refusing to overwrite existing, different files:", file=sys.stderr)
        for path in conflicts:
            print(f"  - {path}", file=sys.stderr)
        print(
            "Merge the shared contract deliberately, then rerun validation.",
            file=sys.stderr,
        )
        return 2

    action = "would create" if args.dry_run else "created"
    if not args.dry_run:
        for artifact in pending:
            artifact.destination.parent.mkdir(parents=True, exist_ok=True)
            artifact.destination.write_bytes(artifact.content)

    for artifact in pending:
        print(f"{action}: {artifact.destination.relative_to(target)}")
    unchanged = len(artifacts) - len(pending)
    if unchanged:
        print(f"unchanged: {unchanged} matching file(s)")

    if args.dry_run:
        print("PASS dry-run preflight found no conflicts")
    else:
        print(
            f"PASS installed operating manual {MANUAL_VERSION} with a draft project seed"
        )
        print("NEXT ground and resolve the profile's day-one activation minimum")
        print(
            "NEXT run: python3 .agents/skills/operating-model-bootstrap/scripts/"
            "validate_operating_model.py --target ."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
