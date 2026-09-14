# Keeping the context graph coherent — on-demand freshness as a day-0 capability

> **Improvement fed back from a live project (a Python + TypeScript trading platform, 2026-08-24).** A semantic
> code graph makes an agent cheaper and more accurate — it answers "where is X / who calls
> Y / what is this file's API" from a prebuilt index instead of re-grepping. But an index is
> a snapshot, and a snapshot **rots silently**: the agent keeps reasoning from a structure
> that no longer matches the tree, and nothing errors. Stale context is worse than no
> context, because it is confidently wrong. This pattern makes the graph self-heal so an
> agent never plans against a stale map.

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
   Set `CGF_GRAPH`, `CGF_BUILD_CMD`, `CGF_EXTS` if the project's indexer isn't the graft default.
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
4. Ensure the graph directory is gitignored-but-greppable, and the indexer version is pinned.

## Reference implementation

The reference project (2026-08-24): the guard script, three git hooks in `.git/hooks/`, a
SessionStart hook in `.claude/settings.local.json`, graft pinned to `0.10.1`. Guard verified:
FRESH→skip in <1s; a forced rebuild parsed 1,002 files clean. This portable copy generalises it: any indexer via `CGF_BUILD_CMD`,
any language via `CGF_EXTS`.

## Guardrails carried over from the graft security review

- Do **not** run an indexer's `init` if it rewrites global agent settings, nor a `--deep` mode
  that ships source to a third-party LLM, nor a local `viz` server with an open network issue.
  Wire the index manually (project-scoped MCP + a build command) — same value, none of the risk.
- Pin the indexer version; re-check on upgrade.
- Treat the graph as **derived, gitignored** state — never committed, always rebuildable.
