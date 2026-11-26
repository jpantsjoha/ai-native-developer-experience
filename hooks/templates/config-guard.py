#!/usr/bin/env python3
"""config-guard: the harness's own config is editable only on a harness branch.

Why it exists: a ratchet baseline, a guard config or the hook registration is what stops
drift; an agent that can edit them on any branch can loosen the gate it is working under.
This is a sibling of records-guard.py: same engine (loaded from beside this file), same
payload contract, same path-owner resolution, but it reads `.devex/config-guard.json` and
protects the harness files instead of the delivery records. Deny only, never `ask`;
`--staged` is the pre-commit mode.

Config (optional) `.devex/config-guard.json`:
  {"protected": [".devex/ratchet.baseline.json", ".claude/settings.json"],
   "branch_patterns": ["harness/*", "records-*"]}
Defaults when the file is absent: every `.devex/*.json`, `.devex/baseline-raise.txt`,
`.devex/hooks/*`, `.claude/settings.json`; branches `harness/*` and `records/*`.
The one edge that bites: `.devex/*.json` is protected whatever the config lists, so an
unknown or new config file under `.devex/` is guarded by default, and a config that omits
the glob cannot weaken it. The same rule is why an edit to this config is itself denied
off a harness branch.
"""

from __future__ import annotations

import importlib.util
import os
import sys

ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "records-guard.py")
DEFAULT_PROTECTED = [".devex/*.json", ".devex/baseline-raise.txt", ".devex/hooks/*",
                     ".claude/settings.json"]
DEFAULT_BRANCHES = ["harness/*", "records/*"]


def load_engine():
    spec = importlib.util.spec_from_file_location("devex_records_guard", ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    try:
        engine = load_engine()
    except (OSError, ImportError, SyntaxError):
        return 0  # no engine beside this file: allow, never block on a broken install
    engine.SETTINGS.update({
        "config": os.path.join(".devex", "config-guard.json"),
        "protected": DEFAULT_PROTECTED,
        "branches": DEFAULT_BRANCHES,
        "always": [".devex/*.json"],
        "label": "config-guard",
        "noun": "harness config file",
        "branch_noun": "a harness branch",
        "advice": "Change it on a harness branch and say why in the PR body.",
    })
    return engine.main(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    sys.exit(main())
