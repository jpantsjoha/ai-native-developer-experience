# Keeping the context graph coherent — on-demand freshness as a day-0 capability

> **Improvement fed back from a live project (a Python + TypeScript trading platform, 2026-08-24).** A semantic
> code graph makes an agent cheaper and more accurate — it answers "where is X / who calls
> Y / what is this file's API" from a prebuilt index instead of re-grepping. But an index is
> a snapshot, and a snapshot **rots silently**: the agent keeps reasoning from a structure
> that no longer matches the tree, and nothing errors. Stale context is worse than no
> context, because it is confidently wrong. This pattern makes the graph self-heal so an
> agent never plans against a stale map.

> **Graft is now Trail-code (checked 2026-11-25).** The indexer this pattern was built on,
> graft (`@nanonets/graft`), was renamed Trail-code: repository
> [`trailhq/Trail-Code`](https://github.com/trailhq/Trail-Code), npm package
> [`@trailhq/trail-code`](https://www.npmjs.com/package/@trailhq/trail-code), command `trail`.
> The code map is still called the graft map and is still built to
> `graft/.graph/wiring.json`; the `graft` command and the old package still run the same
> code. Trail-code also adds "learnings", read from your past sessions and PR reviews,
> which brings new guardrails below. Mentions of graft in the reference-project story
> are historical. See [INTEGRATIONS.md](../INTEGRATIONS.md#context-graph) for the
> current version and licence.

## The failure it removes

In the reference project the graph (graft: 13k nodes / 28k edges across Python + TS) was
**5 days and ~640 commits stale** before anyone noticed. Nothing surfaced it — the agent
had been answering structural questions against a June snapshot in an August tree. Freshness
was a manual chore (`graft build`) that, being a chore, was skipped. **Detection is a
property of process, not of effort** — so the fix is a process, not a reminder.

## The pattern — one idempotent guard, three triggers

A single guard script decides *whether* to rebuild; three triggers decide *when* to run it.
The guard is the invariant; the triggers are just the places staleness can be introduced.

```
                 ┌──────────────────────────────────────────────┐
  git advances → │  post-merge / post-checkout / post-rewrite    │──┐
  (pull/rebase)  └──────────────────────────────────────────────┘  │
                 ┌──────────────────────────────────────────────┐  │   ┌─────────────────────┐
  agent starts → │  Claude/agent SessionStart hook (async)       │──┼──▶│ context-graph-       │
                 └──────────────────────────────────────────────┘  │   │ refresh.sh (guard)  │
                 ┌──────────────────────────────────────────────┐  │   │  • stale? one find  │
  human/agent  → │  manual: context-graph-refresh.sh [--force]   │──┘   │  • lock (no stampede)│
                 └──────────────────────────────────────────────┘      │  • incremental build │
                                                                        └─────────────────────┘
```

**The guard** (`scripts/context-graph-refresh.sh`, portable, env-configurable):

- **Cheap when fresh.** One `find` for any tracked source newer than the graph, then exit.
  Idempotent — safe to call on every trigger.
- **Rebuilds only when stale.** Newest source mtime vs graph mtime. `--force` overrides.
- **Single-flight.** An atomic `mkdir` lock means the git hook, the session hook and a manual
  run never stampede — a half-built graph is never queried mid-write. **Coherence, not just
  freshness.**
- **Incremental.** Unchanged files replay from cache, so a rebuild is seconds, not minutes,
  which is what lets it sit on hot paths like a branch switch.

**Trigger 1 — git hooks** (`.git/hooks/post-merge`, `post-checkout`, `post-rewrite`): the
graph goes stale exactly when the tree changes, so refresh there, in the background. Gate
`post-checkout` to branch checkouts (`$3 == 1`) so file-level checkouts don't churn.

**Trigger 2 — agent SessionStart hook** (project-local settings, **not** the plugin core):
run the guard `async` so a new session self-heals staleness before it leans on the graph.
This is the "ensure *I* have an up-to-date graph on demand" half — tied to when the agent
actually needs it.

**Trigger 3 — manual / on-demand**: call the guard before any graph-heavy task; `--force`
after a large external change the mtime heuristic can't see.

## Wiring it into a bootstrapped project (the day-0 checklist)

1. Drop `scripts/context-graph-refresh.sh` into the project (or point at a shared copy).
   Set `CGF_GRAPH`, `CGF_BUILD_CMD`, `CGF_EXTS` if the project's indexer isn't the Trail-code default
   (`DO_NOT_TRACK=1 npx -y @trailhq/trail-code@0.30.5 build`, writing `graft/.graph/wiring.json`).
2. Install the three git hooks — each a one-liner backgrounding the guard:
   ```bash
   echo 'bash scripts/context-graph-refresh.sh >/dev/null 2>&1 &' >> .git/hooks/post-merge
   # post-rewrite: same. post-checkout: guard on [ "$3" = "1" ].
   ```
   Git hooks are per-clone (not committed); worktrees share them via the common git dir.
3. Add a SessionStart hook to the agent's **machine-local** settings — never the committed
   plugin config, because it references an absolute local path and must not reach CI or a
   teammate. For Claude Code that is `.claude/settings.local.json` (gitignored):
   ```json
   { "hooks": { "SessionStart": [ { "hooks": [
       { "type": "command", "command": "bash scripts/context-graph-refresh.sh >/dev/null 2>&1 &", "async": true }
   ] } ] } }
   ```
4. Ensure the graph directory is gitignored-but-greppable (the guard keeps its lock and log
   beside the graph, so they are ignored with it), and the indexer version is pinned.

## Reference implementation

The reference project (2026-08-24): the guard script, three git hooks in `.git/hooks/`, a
SessionStart hook in `.claude/settings.local.json`, graft pinned to `0.10.1`. Guard verified:
FRESH→skip in <1s; a forced rebuild parsed 1,002 files clean. This portable copy generalises it: any indexer via `CGF_BUILD_CMD`,
any language via `CGF_EXTS`.

**Reference pin, 2026-11-25:** the reference pin of graft `0.10.1` is now Trail-code
`0.30.5` (npm `@trailhq/trail-code`, published 2026-11-17; the old `@nanonets/graft`
package is at `0.30.1`). The guard script's default build command uses the new package
with `DO_NOT_TRACK=1`.

**Guard tested against 0.30.5, 2026-11-25,** on a copy of this repository (22 source
files), with `CGF_BUILD_CMD="DO_NOT_TRACK=1 trail build"` and a global install of the same
0.30.5, so the `npx` fetch in the default command was not exercised:

| Run | Result |
|---|---|
| First run, no graph | Rebuilt; `graft/.graph/wiring.json` written (407 nodes, 989 edges) in 0.6 s |
| Second run, nothing changed | `FRESH`, skipped in 0.05 s |
| After touching a `.py` file | Rebuilt |
| `--force` | Rebuilt; 22 of 22 files replayed from Trail-code's cache |

The default graph path matches what 0.30.5 writes. Two things the test turned up:

- `trail build` edits the repository on its first run: it appends `/graft/` to
  `.gitignore` and creates a `.ignore` file that re-admits `graft/` to ripgrep. Both are
  benign, but they show up as changes in `git status`; commit them once, deliberately.
- Trail-code also indexes shell scripts, but the guard's default `CGF_EXTS` is
  `py ts tsx js`, so editing only a `.sh` file leaves the graph stale. Add `sh` (and any
  other indexed language) to `CGF_EXTS` in projects where it matters.

## Guardrails carried over from the graft security review

These came from the graft review and still apply to Trail-code. The last three were added
on 2026-11-25 for what Trail-code added; sources are its
[README](https://github.com/trailhq/Trail-Code#what-stays-on-your-machine) and
[TELEMETRY.md](https://github.com/trailhq/Trail-Code/blob/main/TELEMETRY.md).

- Do **not** run an indexer's `init` if it rewrites global agent settings, nor a `--deep` mode
  that ships source to a third-party LLM, nor a local `viz` server with an open network issue.
  Wire the index manually (project-scoped MCP + a build command) — same value, none of the risk.
- Pin the indexer version; re-check on upgrade.
- **Do not run `trail init` on client work without the client's agreement.** It does more
  than build the index: it reads your own messages from the repo's past Claude Code
  transcripts (through your Claude Code, so they go to Anthropic and count toward your
  usage), and, when `gh` is signed in, the review comments on the repo's last 50 merged
  PRs. It turns what it finds into learnings and writes them into the repo's `.trail/`
  for committing, or to `~/.trail` in "just me" mode. It also adds hooks and a statusline to
  Claude Code, and `--agents` removes its wiring from other agents' user-level files unless
  `--no-global` is passed. If you do run it, run `trail init --dry-run` first and review
  every learning before it is committed.
- **Telemetry is on by default.** Trail-code sends anonymous usage events, posted at most
  once a day by a background process. Set `DO_NOT_TRACK=1` in every environment that runs
  the indexer (shell, git hooks, the SessionStart hook), or run `trail telemetry disable`
  once per machine. The guard script's default build command sets `DO_NOT_TRACK=1`; a custom
  `CGF_BUILD_CMD` must set it itself. CI variables (`CI`, `GITHUB_ACTIONS`) turn it off.
  Set it **before the first command**: on the 2026-11-25 test machine, the first `trail`
  command had already queued a usage event before `trail telemetry disable` ran. Whether
  that event was sent was not checked.
- **The old `graft` command is not a way round these.** `graft` and `@nanonets/graft` run the
  same Trail-code, telemetry included.
- Treat the graph as **derived, gitignored** state — never committed, always rebuildable.
