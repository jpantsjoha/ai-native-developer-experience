#!/usr/bin/env python3
"""Install a safe, version-bound operating-model seed into a target repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


MANUAL_VERSION = "2.2.0"
SURFACE_FILES = {
    "agents": "AGENTS.md",
    "claude": "CLAUDE.md",
    "gemini": "GEMINI.md",
}


# Opt-in design/records harness steps: name -> (one-line purpose, [(asset, destination)]).
# Nothing here is installed unless named with --adopt; a dry run lists every step.
ADOPT_STEPS = {
    "records-guard": (
        "deny edits to ROADMAP/STATUS/CHANGELOG off a records branch (PreToolUse and --staged)",
        [("records-guard.py", ".devex/hooks/records-guard.py"),
         ("bashwrites.py", ".devex/hooks/bashwrites.py")],
    ),
    "config-guard": (
        "deny edits to the harness config (.devex/*.json, settings) off a harness branch",
        [("config-guard.py", ".devex/hooks/config-guard.py")],
    ),
    "pre-commit": (
        "git pre-commit checks and the clone-local installer (run install-precommit.py or "
        "--install-precommit)",
        [("pre-commit-checks.py", ".devex/hooks/pre-commit-checks.py"),
         ("install-precommit.py", ".devex/hooks/install-precommit.py")],
    ),
    "registration-audit": (
        "fail when a test script is registered with no runner and has no reasoned exclusion",
        [("registration-audit.py", ".devex/tools/registration-audit.py")],
    ),
    "gate-log": (
        "print a gate log path keyed by worktree and commit",
        [("gate-log.py", ".devex/tools/gate-log.py")],
    ),
    "ui-context": (
        "once per session, remind the agent to load the design skill on UI paths",
        [("ui-context.py", ".devex/hooks/ui-context.py")],
    ),
    "post-edit-ratchet": (
        "run the literal ratchet on each edited file; block with file:line on regression",
        [("post-edit-ratchet.py", ".devex/hooks/post-edit-ratchet.py"),
         ("literal-ratchet.py", ".devex/hooks/literal-ratchet.py")],
    ),
    "ratchet-config": (
        "starter literal-ratchet config (edit globs and rules; then --update-baseline once)",
        [("ratchet.config.example.json", ".devex/ratchet.config.json")],
    ),
}
# A step that loads another step's file needs it beside it.
ADOPT_NEEDS = {"config-guard": ["records-guard"]}
HOOK_EVENTS = {
    "records-guard": ("PreToolUse", "Edit|Write|MultiEdit|NotebookEdit|Bash"),
    "config-guard": ("PreToolUse", "Edit|Write|MultiEdit|NotebookEdit|Bash"),
    "ui-context": ("PreToolUse", "Edit|Write|MultiEdit"),
    "post-edit-ratchet": ("PostToolUse", "Edit|Write|MultiEdit"),
}


@dataclass(frozen=True)
class Artifact:
    """One destination and the exact bytes the initializer intends to write."""

    destination: Path
    content: bytes
    preserve_existing: bool = False


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
        "--adopt",
        action="append",
        choices=(*ADOPT_STEPS, "all"),
        help="Opt in to a design/records harness step; repeat as needed (default: none). "
        "Files are copied under .devex/, never overwritten and never registered in settings.",
    )
    parser.add_argument(
        "--adopt-only",
        action="store_true",
        help="For a repository that already has its seed: skip the operating-model files and "
        "run only the --adopt / --register-settings / --install-precommit / --make-targets "
        "steps. Dry-run unless --apply is given; never overwrites.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="With --adopt-only: perform the steps the dry run listed.",
    )
    parser.add_argument(
        "--register-settings",
        action="store_true",
        help="Merge the hook entries of the adopted (or already installed) steps into "
        ".claude/settings.json; only the 'hooks' key is touched, entries already present are "
        "kept, an unreadable file is refused.",
    )
    parser.add_argument(
        "--install-precommit",
        action="store_true",
        help="Install the harness pre-commit into this clone's own git hooks directory "
        "(adopts the pre-commit step; never writes outside the clone or to core.hooksPath).",
    )
    parser.add_argument(
        "--make-targets",
        action="store_true",
        help="Write .devex/harness.mk (harness-install, harness-status, ratchet, "
        "ratchet-raise, registration-audit) and add one include line to an existing Makefile.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preflight every destination without writing anything.",
    )
    args = parser.parse_args()
    if args.apply and not args.adopt_only:
        parser.error("--apply only goes with --adopt-only")
    if args.apply and args.dry_run:
        parser.error("--apply and --dry-run contradict each other")
    if args.adopt_only and not (args.adopt or args.register_settings
                                or args.install_precommit or args.make_targets):
        parser.error("--adopt-only needs --adopt, --register-settings, --install-precommit "
                     "or --make-targets")
    return args


def selected_surfaces(values: list[str] | None) -> list[str]:
    """Resolve repeated surface flags into a stable, de-duplicated list."""

    if not values or "all" in values:
        return list(SURFACE_FILES)
    return [name for name in SURFACE_FILES if name in values]


def selected_adoptions(values: list[str] | None) -> list[str]:
    """Resolve --adopt flags into a stable list of opt-in step names."""

    if not values:
        return []
    wanted = set(ADOPT_STEPS) if "all" in values else set(values)
    for name in list(wanted):
        wanted.update(ADOPT_NEEDS.get(name, []))
    return [name for name in ADOPT_STEPS if name in wanted]


def assets_dir() -> Path:
    """Directory holding the byte-identical harness mirrors."""

    return Path(__file__).resolve().parent.parent / "assets" / "design-harness"


def hook_command(name: str) -> str:
    """Settings command for a hook step; $CLAUDE_PROJECT_DIR finds it from any session cwd."""

    return f'python3 "$CLAUDE_PROJECT_DIR"/.devex/hooks/{name}.py'


def plan_settings(target: Path, steps: list[str]) -> tuple[dict | None, list[str], str | None]:
    """Merge hook entries into .claude/settings.json in memory.

    Returns (new content or None when nothing changes, descriptions of additions, error).
    Only the top-level 'hooks' key is touched; permissions and every other key are kept.
    """

    path = target / ".claude" / "settings.json"
    data: dict = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return None, [], f"{path} is not readable JSON ({exc}); refusing to touch it"
        if not isinstance(data, dict) or not isinstance(data.get("hooks", {}), dict):
            return None, [], f"{path} has an unexpected shape; refusing to touch it"
    merged = json.loads(json.dumps(data))
    hooks = merged.setdefault("hooks", {})
    added = []
    for step in steps:
        if step not in HOOK_EVENTS:
            continue
        event, matcher = HOOK_EVENTS[step]
        command = hook_command(step)
        groups = hooks.setdefault(event, [])
        if not isinstance(groups, list):
            return None, [], f"{path}: hooks.{event} is not a list; refusing to touch it"
        present = any(
            isinstance(h, dict) and h.get("command") == command
            for g in groups if isinstance(g, dict)
            for h in g.get("hooks", []) if isinstance(g.get("hooks", []), list)
        )
        if not present:
            groups.append({"matcher": matcher, "hooks": [{"type": "command", "command": command}]})
            added.append(f"{event} {step}")
    if not added:
        return None, [], None
    return merged, added, None


def plan_make_targets(target: Path) -> tuple[Artifact, str | None]:
    """The harness.mk artifact and the include line to add to an existing Makefile, if any."""

    artifact = Artifact(target / ".devex" / "harness.mk",
                        (assets_dir() / "harness.mk").read_bytes(), preserve_existing=True)
    makefile = target / "Makefile"
    if makefile.is_file() and "harness.mk" not in makefile.read_text(encoding="utf-8"):
        return artifact, "-include .devex/harness.mk"
    return artifact, None


def adopt_artifacts(target: Path, steps: list[str]) -> list[Artifact]:
    """Render opt-in harness files; existing different files are preserved, not replaced."""

    assets = assets_dir()
    rendered = []
    for step in steps:
        for asset, destination in ADOPT_STEPS[step][1]:
            rendered.append(
                Artifact((target / destination), (assets / asset).read_bytes(),
                         preserve_existing=True)
            )
    return rendered


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

    def render_markdown_template(filename: str) -> bytes:
        """Render project identity while retaining adoption placeholders."""

        text = (assets / filename).read_text(encoding="utf-8")
        return text.replace("<Project Name>", project_name).encode("utf-8")

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
        Artifact(
            operating_root / "DELIVERY-WORKFLOW.md",
            render_markdown_template("DELIVERY-WORKFLOW.template.md"),
            preserve_existing=True,
        ),
        Artifact(
            target / "docs" / "VISION.md",
            render_markdown_template("VISION.template.md"),
            preserve_existing=True,
        ),
        Artifact(
            target / "docs" / "ROADMAP.md",
            render_markdown_template("ROADMAP.template.md"),
            preserve_existing=True,
        ),
        Artifact(
            target / "docs" / "STATUS.md",
            render_markdown_template("STATUS.template.md"),
            preserve_existing=True,
        ),
        Artifact(
            target / "CHANGELOG.md",
            render_markdown_template("CHANGELOG.template.md"),
            preserve_existing=True,
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


def preflight(
    artifacts: list[Artifact],
) -> tuple[list[Artifact], list[Path], list[Path]]:
    """Classify new outputs, contract conflicts, and project records to preserve."""

    pending: list[Artifact] = []
    conflicts: list[Path] = []
    preserved: list[Path] = []
    for artifact in artifacts:
        if not artifact.destination.exists():
            pending.append(artifact)
        elif artifact.destination.read_bytes() != artifact.content:
            if artifact.preserve_existing:
                preserved.append(artifact.destination)
            else:
                conflicts.append(artifact.destination)
    return pending, conflicts, preserved


def run_precommit_installer(target: Path, dry_run: bool) -> int:
    """Run install-precommit.py (the installed copy, else the asset) against the target clone."""

    script = target / ".devex" / "hooks" / "install-precommit.py"
    if not script.is_file():
        script = assets_dir() / "install-precommit.py"
    command = [sys.executable, str(script), "--root", str(target)]
    if dry_run:
        command.append("--dry-run")
    return subprocess.run(command).returncode


def main() -> int:
    """Preflight the full file set, then install without overwriting any file."""

    args = parse_args()
    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        print(f"ERROR target is not a directory: {target}", file=sys.stderr)
        return 2

    # --adopt-only is dry-run until --apply: the plan is always read before anything is written.
    dry_run = args.dry_run or (args.adopt_only and not args.apply)
    adopt_flags = list(args.adopt or [])
    if args.install_precommit:
        adopt_flags.append("pre-commit")
    adoptions = selected_adoptions(adopt_flags)

    artifacts: list[Artifact] = []
    if not args.adopt_only:
        surfaces = selected_surfaces(args.surface)
        artifacts = render_artifacts(target, args.project_name or target.name, surfaces)
    artifacts += adopt_artifacts(target, adoptions)
    mk_include = None
    if args.make_targets:
        mk_artifact, mk_include = plan_make_targets(target)
        artifacts.append(mk_artifact)

    settings_data, settings_added = None, []
    if args.register_settings:
        installed = [n for n in HOOK_EVENTS
                     if any((target / d).is_file() for _a, d in ADOPT_STEPS[n][1][:1])]
        steps = [n for n in ADOPT_STEPS if n in set(adoptions) | set(installed)]
        settings_data, settings_added, error = plan_settings(target, steps)
        if error:
            print(f"ERROR {error}", file=sys.stderr)
            return 2

    pending, conflicts, preserved = preflight(artifacts)
    if conflicts:
        print("ERROR refusing to overwrite existing, different files:", file=sys.stderr)
        for path in conflicts:
            print(f"  - {path}", file=sys.stderr)
        print(
            "Merge the shared contract deliberately, then rerun validation.",
            file=sys.stderr,
        )
        return 2

    action = "would create" if dry_run else "created"
    if not dry_run:
        for artifact in pending:
            artifact.destination.parent.mkdir(parents=True, exist_ok=True)
            artifact.destination.write_bytes(artifact.content)
            if artifact.destination.suffix == ".py":
                artifact.destination.chmod(0o755)

    for artifact in pending:
        print(f"{action}: {artifact.destination.relative_to(target)}")
    for path in preserved:
        print(f"preserved existing: {path.relative_to(target)}")
    unchanged = len(artifacts) - len(pending) - len(preserved)
    if unchanged:
        print(f"unchanged: {unchanged} matching file(s)")

    for name, (purpose, _files) in ADOPT_STEPS.items():
        kept = {target / dest for _asset, dest in ADOPT_STEPS[name][1]} & set(preserved)
        if name in adoptions:
            state = "preserved" if kept else "adopted"
        else:
            state = "opt-in, not installed"
        print(f"{state}: --adopt {name} - {purpose}")

    if mk_include:
        makefile = target / "Makefile"
        print(f"{'would append' if dry_run else 'appended'} to Makefile: {mk_include}")
        if not dry_run:
            text = makefile.read_text(encoding="utf-8")
            makefile.write_text(text + ("" if text.endswith("\n") else "\n") + mk_include + "\n",
                                encoding="utf-8")
    elif args.make_targets and not (target / "Makefile").is_file():
        print("NEXT no Makefile here: add `-include .devex/harness.mk` to yours")

    if args.register_settings:
        for entry in settings_added:
            print(f"{'would add' if dry_run else 'added'} hook to .claude/settings.json: {entry}")
        if not settings_added:
            print("unchanged: .claude/settings.json already registers these hooks")
        elif not dry_run and settings_data is not None:
            path = target / ".claude" / "settings.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(settings_data, indent=2) + "\n", encoding="utf-8")
    else:
        for name in adoptions:
            if name in HOOK_EVENTS:
                event, matcher = HOOK_EVENTS[name]
                print(f"NEXT register {name} yourself in .claude/settings.json under hooks."
                      f"{event} (matcher \"{matcher}\"): command "
                      f"\"python3 $CLAUDE_PROJECT_DIR/.devex/hooks/{name}.py\"; "
                      "nothing is enabled automatically (or rerun with --register-settings)")

    if args.install_precommit:
        code = run_precommit_installer(target, dry_run)
        if code:
            return code

    if dry_run:
        print("PASS dry-run preflight found no conflicts")
        if args.adopt_only and not args.dry_run:
            print("NEXT rerun with --apply to perform the steps above")
    elif args.adopt_only:
        print("PASS adopted the harness steps; the operating-model seed was not touched")
    else:
        print(
            f"PASS installed operating manual {MANUAL_VERSION} with a draft project seed"
        )
        print(
            "NEXT ground the vision and workflow, initialise the roadmap/status, and "
            "resolve the profile's day-one activation minimum"
        )
        validator = Path(__file__).resolve().with_name("validate_operating_model.py")
        print("NEXT run: " + shlex.join(
            [sys.executable, str(validator), "--target", str(target)]
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
