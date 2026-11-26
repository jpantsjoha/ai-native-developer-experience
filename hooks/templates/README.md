# Hook templates (opt-in)

These are templates. Nothing here is registered in `hooks/hooks.json` and nothing is
enabled globally. `operating-model-bootstrap` copies them into a project only when the
operator opts in (`--adopt records-guard`, `ui-context`, `post-edit-ratchet`,
`ratchet-config`); a dry run lists the steps and writes nothing.

| Template | Event | What it does |
|---|---|---|
| `records-guard.py` | PreToolUse, or `--staged` pre-commit | Denies edits to protected records (ROADMAP, STATUS, CHANGELOG) off a records branch |
| `ui-context.py` | PreToolUse | Once per session, reminds the agent to load the design skill on UI paths |
| `post-edit-ratchet.py` | PostToolUse | Runs `literal-ratchet.py` on the edited file; blocks with file:line on regression |
| `config-guard.py` | PreToolUse, or `--staged` | Sibling of `records-guard.py`: denies edits to the harness config (`.devex/*.json` always, baseline, hooks, `.claude/settings.json`) off a harness branch |
| `bashwrites.py` | (library) | Resolves the absolute paths a Bash command writes; `records-guard.py` loads it from beside itself |
| `pre-commit-checks.py`, `install-precommit.py` | git pre-commit | The shared git path for every writer; the installer is clone-local (see the chain contract below) |
| `harness.mk` | make | `harness-install`, `harness-status`, `ratchet`, `ratchet-raise`, `registration-audit` targets |

Two tools ship beside them (`scripts/registration_audit.py`, `scripts/gate_log.py`, adopted as
`registration-audit` and `gate-log` into `.devex/tools/`): the first fails a test script that no
runner mentions and that has no reasoned exclusion (`.devex/test-registration.json`); the second
prints a gate log path keyed by worktree and commit, so two lanes never read each other's log.

All three answer allow or deny only, never `ask` (an `ask` forces a prompt even in bypass
mode), and allow on malformed input. Python 3 standard library only.

Which checkout judges an edit. The three payload hooks judge the edited path's own git
checkout, not the session `cwd`: an Edit or Write is resolved from its absolute `file_path`,
a Bash command from the paths `bashwrites.py` says it writes (following `cd`, `git -C`,
globs, variables, `bash -c` and interpreter one-liners). Config and branch come from that
checkout; a path in no checkout falls back to `cwd`. `records-guard.py --config PATH` reads
another config file with the same engine (that is how `config-guard.py` works).

Limits and baseline. `records-guard.py` ignores stderr and `/dev/null` redirections. Names
built at run time from input, and `printf` with a format string, are not resolved by
`bashwrites.py`; keep `--staged` in pre-commit as the backstop. In `literal_ratchet.py`, `--update-baseline` only
lowers counts; a new rule or file (a new rule/file pair) enters the baseline by a reviewed
edit of the baseline file, never by `--update-baseline`.

Raise discipline. `literal_ratchet.py --check-raise BASE_REF` fails when the baseline rose
against BASE_REF (or a known rule gained a file) without a note (`raise_note` in the config,
default `.devex/baseline-raise.txt`) that changed since BASE_REF and has a line
`<rule> <file|*> <reason>` per raise. A rule new since BASE_REF is an initial baseline. Run it
in the PR gate; it holds on any branch name. `config-guard.py` protects the note.

Pre-commit and the `core.hooksPath` chain contract. `install-precommit.py` writes one
dispatcher to `<git-common-dir>/hooks/pre-commit`, shared by the clone and its linked
worktrees. At commit time it runs a chained earlier hook (kept as `pre-commit.pre-harness`),
then `$(git rev-parse --show-toplevel)/.devex/hooks/pre-commit-checks.py`; it bakes no
checkout path, so removing the worktree it was installed from breaks nothing, and a branch
without the script prints a note and still commits. The hooks directory is resolved from
`git rev-parse --git-common-dir`, never `git rev-parse --git-path hooks` (which follows a
global `core.hooksPath`). The installer refuses a hooks directory that resolves outside the
clone, never writes `core.hooksPath` and never writes outside the clone. If `core.hooksPath`
is set, git ignores the clone's hooks directory: the dispatcher it points at must run
`"$(git rev-parse --git-common-dir)/hooks/pre-commit"` (not `.git/hooks/pre-commit`, which does
not exist in a linked worktree); the installer prints that line.

Bootstrap writers. `operating-model-bootstrap` (all dry-run first, never overwriting):
`--adopt-only` skips the operating-model seed for a repository that already has one and is a
dry run until `--apply`; `--register-settings` merges the hook entries into
`.claude/settings.json` (only the `hooks` key; permissions and every other key untouched);
`--install-precommit` runs the installer; `--make-targets` writes `.devex/harness.mk` and one
include line into an existing Makefile.

The canonical copies live here and in `scripts/literal_ratchet.py`; byte-identical mirrors
sit under `skills/operating-model-bootstrap/assets/design-harness/` so a skill-only install
can adopt them. A test fails if the mirrors drift; refresh with
`python3 scripts/sync_design_harness.py`.
