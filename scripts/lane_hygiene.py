#!/usr/bin/env python3
"""Read-only lane hygiene report: which worktrees and branches are done and removable.

The operating manual (2.2.0) makes lane cleanup part of COMPLETE. Cleanup needs evidence
that a lane's change is integrated, and squash or rebase merges change commit IDs, so
ancestry alone under-reports. This report checks three ways, all offline:

1. ancestry: the tip is reachable from the base;
2. rebase/cherry-pick: every lane commit has a patch-equivalent commit on the base, and the
   lane holds no merge commits (`git cherry` cannot see content a merge brought in);
3. squash: the lane's combined diff has the same patch-id as one base commit.

With `--pr-state` it also asks `gh` for a merged pull request into the base branch whose
head is the current tip.

A lane whose tip lies on the base's first-parent history has no commits of its own: it is
freshly cut or was fast-forwarded. That cannot be told apart offline, so it is reported for
review, never as removable. Remote branches are judged only against the same remote's
copy of the base, on one remote (`--remote`, default `origin`), and long-lived names
(main, master, develop, dev, trunk, release/*, hotfix/*, gh-pages) are never candidates,
locally or remotely.

Limits: patch-id matching cannot see a base commit that was later reverted, or an unrelated
base commit with an identical patch. The report suggests; a person decides.

It never deletes, prunes, fetches, or writes refs, objects, or index files. It prints the
commands a person may choose to run. Exit 0 = report produced (with `--strict`, 1 when
removable items exist); 2 = the repository or base could not be read.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Stop `git status` refreshing the index: this report must not write anything.
GIT_ENV = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}
LONG_LIVED = re.compile(r"^(main|master|develop|dev|trunk|gh-pages|release/.+|hotfix/.+)$")
REMOVABLE = {"remove-candidate", "stale-metadata", "branch-remove-candidate",
             "remote-branch-candidate", "stale-registration"}


class HygieneError(RuntimeError):
    """The repository, base ref, or an input file could not be read."""


def git(root: Path, *args: str, check: bool = True, stdin: str | None = None) -> str:
    """Run one read-only git command and return stdout; raise on failure if `check`."""
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                            text=True, env=GIT_ENV, input=stdin)
    if check and result.returncode != 0:
        raise HygieneError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def resolve_base(root: Path, base: str | None) -> str:
    """Return the base ref: the given one, else origin/HEAD's target, else `main`."""
    if not base:
        head = git(root, "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD",
                   check=False).strip()
        base = head or "main"
    if not git(root, "rev-parse", "-q", "--verify", f"{base}^{{commit}}",
               check=False).strip():
        raise HygieneError(f"base ref not found: {base}")
    return base


def patch_id(diff_text: str, root: Path) -> set[str]:
    """Stable patch-ids for a diff stream; an empty diff yields an empty set."""
    if not diff_text.strip():
        return set()
    out = git(root, "patch-id", "--stable", stdin=diff_text)
    return {line.split()[0] for line in out.splitlines() if line.strip()}


def integration(root: Path, tip: str, base: str) -> str | None:
    """Return how `tip` is integrated into `base`, or None if not shown offline."""
    if subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", tip, base],
                      env=GIT_ENV, capture_output=True).returncode == 0:
        return "ancestry"
    merge_base = git(root, "merge-base", base, tip, check=False).strip()
    if not merge_base:
        return None
    has_merges = bool(git(root, "rev-list", "--merges", f"{merge_base}..{tip}").strip())
    cherry = [line for line in git(root, "cherry", base, tip).splitlines() if line.strip()]
    if not has_merges and cherry and all(line.startswith("-") for line in cherry):
        return "patch-equivalent"
    combined = patch_id(git(root, "diff", merge_base, tip), root)
    if combined:
        base_ids = patch_id(git(root, "log", "-p", "--no-merges", "--format=commit %H",
                                f"{merge_base}..{base}"), root)
        if combined <= base_ids:
            return "squash-equivalent"
    return None


def merged_pr(root: Path, branch: str, tip: str, base_branch: str) -> str | None:
    """Return 'pr #N' when gh reports a PR merged into `base_branch` whose head is `tip`."""
    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--head", branch, "--state", "merged",
             "--json", "number,headRefOid,baseRefName"], cwd=root, capture_output=True,
            text=True)
    except OSError:
        return None
    if result.returncode != 0:
        return None
    for pr in json.loads(result.stdout or "[]"):
        if pr.get("headRefOid") == tip and pr.get("baseRefName") == base_branch:
            return f"pr #{pr['number']}"
    return None


def first_parent_chain(root: Path, base: str) -> set[str]:
    """Commits on the base's first-parent history: tips here have no work of their own."""
    return set(git(root, "rev-list", "--first-parent", base).split())


@dataclass
class Item:
    """One reported worktree, branch, or plugin registration and its verdict."""
    kind: str
    name: str
    category: str
    reason: str
    suggestion: str = ""
    detail: dict = field(default_factory=dict)


def parse_worktrees(root: Path) -> list[dict]:
    """Parse `git worktree list --porcelain` into dicts; the first is the primary."""
    entries, current = [], {}
    for line in git(root, "worktree", "list", "--porcelain").splitlines() + [""]:
        if not line:
            if current:
                entries.append(current)
            current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value or True
    return entries


def how_integrated(root: Path, branch: str | None, tip: str, base: str,
                   base_branch: str, use_pr: bool) -> str | None:
    """Combine the offline checks with the optional PR-state check."""
    found = integration(root, tip, base)
    if not found and use_pr and branch:
        found = merged_pr(root, branch, tip, base_branch)
    return found


def report(root: Path, base: str, use_pr: bool = False,
           installed_plugins: Path | None = None, remote: str = "origin") -> dict:
    """Build the full hygiene report without changing the repository."""
    root = Path(git(root, "rev-parse", "--show-toplevel").strip())
    remotes_known = set(git(root, "remote").split())
    head, _, rest = base.partition("/")
    base_branch = rest if rest and head in remotes_known else base
    trunk = first_parent_chain(root, base)
    no_work = ("no commits of its own (freshly cut or fast-forwarded); "
               "confirm before removing")
    items: list[Item] = []
    worktree_branches: set[str] = set()
    current = Path.cwd().resolve()

    for index, entry in enumerate(parse_worktrees(root)):
        path = Path(entry["worktree"])
        branch = entry.get("branch", "")
        short = branch.removeprefix("refs/heads/") if isinstance(branch, str) else ""
        if short:
            worktree_branches.add(short)
        label = f"{path} [{short or 'detached'}]"
        if index == 0:
            items.append(Item("worktree", label, "primary", "main checkout; never a candidate"))
            continue
        if entry.get("prunable") or not path.exists():
            items.append(Item("worktree", label, "stale-metadata",
                              "worktree path no longer exists",
                              "git worktree prune --dry-run --verbose"))
            continue
        if entry.get("locked"):
            items.append(Item("worktree", label, "locked", "locked; left alone"))
            continue
        dirty = [line for line in git(path, "status", "--porcelain").splitlines() if line]
        if dirty:
            items.append(Item("worktree", label, "keep-dirty",
                              f"{len(dirty)} uncommitted change(s); preserve",
                              detail={"changes": len(dirty)}))
            continue
        tip = entry.get("HEAD", "")
        if short and LONG_LIVED.match(short):
            items.append(Item("worktree", label, "active", "long-lived branch; never a candidate"))
            continue
        if tip in trunk:
            items.append(Item("worktree", label, "review-no-unique-commits", no_work))
            continue
        found = how_integrated(root, short or None, tip, base, base_branch, use_pr)
        here = path.resolve() == current or current.is_relative_to(path.resolve())
        if found:
            suggestion = f"git worktree remove {shlex.quote(str(path))}"
            if short:
                suggestion += f" && git branch -d {shlex.quote(short)}"
            reason = f"clean; integrated into {base} by {found}"
            ignored = [line for line in git(path, "status", "--porcelain", "--ignored")
                       .splitlines() if line.startswith("!!")]
            if ignored:
                reason += (f"; {len(ignored)} ignored path(s) such as .env or build output "
                           "would be deleted with it")
            if here:
                reason += "; this is the current directory, leave it first"
            items.append(Item("worktree", label, "remove-candidate", reason, suggestion,
                              {"integration": found, "ignored_paths": len(ignored)}))
        else:
            items.append(Item("worktree", label, "active",
                              f"not shown integrated into {base}"))

    refs = git(root, "for-each-ref", "refs/heads",
               "--format=%(refname:short)%09%(objectname)%09%(upstream:track)")
    for line in refs.splitlines():
        name, tip, track = (line.split("\t") + ["", ""])[:3]
        if name in worktree_branches or name == base_branch or LONG_LIVED.match(name):
            continue
        if tip in trunk:
            items.append(Item("branch", name, "review-no-unique-commits", no_work))
            continue
        found = how_integrated(root, name, tip, base, base_branch, use_pr)
        if found:
            items.append(Item("branch", name, "branch-remove-candidate",
                              f"integrated into {base} by {found}",
                              f"git branch -d {shlex.quote(name)}", {"integration": found}))
        elif "gone" in track:
            items.append(Item("branch", name, "review-gone-upstream",
                              "upstream deleted but change not shown integrated"))

    remote_base = f"{remote}/{base_branch}"
    if git(root, "rev-parse", "-q", "--verify", f"refs/remotes/{remote_base}",
           check=False).strip():
        remote_trunk = first_parent_chain(root, remote_base)
        refs = git(root, "for-each-ref", f"refs/remotes/{remote}",
                   "--format=%(refname:short)%09%(objectname)%09%(symref)")
        for line in refs.splitlines():
            name, tip, symref = (line.split("\t") + ["", ""])[:3]
            branch = name.removeprefix(f"{remote}/")
            if symref or branch in {"HEAD", base_branch} or LONG_LIVED.match(branch):
                continue
            if tip in remote_trunk:
                continue
            found = integration(root, tip, remote_base)
            if found:
                items.append(Item(
                    "remote-branch", name, "remote-branch-candidate",
                    f"integrated into {remote_base} by {found} (as of last fetch); "
                    "confirm you own it before deleting",
                    f"git push {shlex.quote(remote)} --delete {shlex.quote(branch)}",
                    {"integration": found}))

    if installed_plugins:
        try:
            data = json.loads(installed_plugins.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise HygieneError(f"cannot read {installed_plugins}: {error}") from error
        for plugin, installs in (data.get("plugins") or {}).items():
            for install in installs:
                project = install.get("projectPath")
                if project and not Path(project).exists():
                    items.append(Item("plugin-registration", f"{plugin} @ {project}",
                                      "stale-registration",
                                      "project-scope registration for a deleted path",
                                      "remove via the host's plugin uninstall for that scope"))

    counts: dict[str, int] = {}
    for item in items:
        counts[item.category] = counts.get(item.category, 0) + 1
    return {"root": str(root), "base": base, "read_only": True,
            "counts": counts, "items": [asdict(item) for item in items]}


def render(result: dict) -> str:
    """Human-readable report grouped by verdict; suggestions are never executed."""
    lines = [f"Lane hygiene for {result['root']} against {result['base']} (read-only;"
             " remote refs as of the last fetch)"]
    order = ["remove-candidate", "branch-remove-candidate", "remote-branch-candidate",
             "stale-metadata", "stale-registration", "keep-dirty", "review-gone-upstream",
             "review-no-unique-commits", "active", "locked", "primary"]
    for category in order:
        group = [item for item in result["items"] if item["category"] == category]
        if not group:
            continue
        lines.append(f"\n{category} ({len(group)})")
        for item in group:
            lines.append(f"  {item['name']}: {item['reason']}")
            if item["suggestion"]:
                lines.append(f"    suggested, not run: {item['suggestion']}")
    removable = sum(result["counts"].get(c, 0) for c in REMOVABLE)
    lines.append(f"\n{removable} removable item(s). Nothing was changed.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point; see the module docstring for exit codes."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="Repository or worktree path.")
    parser.add_argument("--base", help="Integration base ref (default: origin/HEAD, else main).")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 when removable items exist.")
    parser.add_argument("--pr-state", action="store_true",
                        help="Also accept a merged PR (via gh) whose head is the tip.")
    parser.add_argument("--installed-plugins", type=Path,
                        help="Host plugin registry JSON to check for deleted project paths.")
    parser.add_argument("--remote", default="origin",
                        help="The one remote whose branches are checked (default: origin).")
    args = parser.parse_args(argv)
    try:
        root = Path(args.root).expanduser().resolve()
        result = report(root, resolve_base(root, args.base), args.pr_state,
                        args.installed_plugins, args.remote)
    except HygieneError as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2) if args.json else render(result))
    removable = sum(result["counts"].get(c, 0) for c in REMOVABLE)
    return 1 if args.strict and removable else 0


if __name__ == "__main__":
    sys.exit(main())
