# Keeping the context graph coherent — on-demand freshness as a day-0 capability

> **Improvement fed back from a live project (a Python + TypeScript trading platform, 2026-08-24).** A semantic
> code graph can reduce repeated exploration — it answers "where is X / who calls
> Y / what is this file's API" from a prebuilt index instead of re-grepping. But an index is
> a snapshot, and a snapshot **rots silently**: the agent keeps reasoning from a structure
> that no longer matches the tree, and nothing errors. Stale context is worse than no
> context, because it can appear confidently correct. This pattern starts refreshes at
> useful lifecycle points; its limits below still require explicit freshness verification.

## The failure it removes

**Audit clarification, 2026-09-26:** this document records a historical adoption
pattern, not a current benchmark or a guarantee of graph coherence. The guard
below is an mtime heuristic. Its writer lock serialises rebuild attempts; query
readers do not acquire that lock, so it does not prove queries cannot see an
in-progress build. Prefer the pinned indexer's verified freshness behaviour; test
any additional guard before treating it as a correctness control.

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

- **Cheap when apparently fresh.** One `find` for configured source extensions newer than the graph, then exit.
  Idempotent — safe to call on every trigger.
- **Rebuilds only when stale.** Newest source mtime vs graph mtime. `--force` overrides.
- **Writer serialisation.** An atomic `mkdir` lock avoids concurrent rebuild attempts
  while held. It does not coordinate readers or prove atomic graph publication;
  age-based stale-lock removal also needs scrutiny for long-running builds.
- **Incremental where supported.** The indexer may reuse unchanged files. Measure
  rebuild time for the pinned version and repository before adding it to hot paths.

**Trigger 1 — git hooks** (`.git/hooks/post-merge`, `post-checkout`, `post-rewrite`): the
graph goes stale exactly when the tree changes, so refresh there, in the background. Gate
`post-checkout` to branch checkouts (`$3 == 1`) so file-level checkouts don't churn.

**Trigger 2 — agent SessionStart hook** (project-local settings, **not** the plugin core):
run the guard `async` to start a refresh without blocking session startup. Verify
completion/freshness before relying on its output.
This is the "ensure *I* have an up-to-date graph on demand" half — tied to when the agent
actually needs it.

**Trigger 3 — manual / on-demand**: call the guard before any graph-heavy task; `--force`
after a large external change the mtime heuristic can't see.

## Wiring it into a bootstrapped project (the day-0 checklist)

1. Drop `scripts/context-graph-refresh.sh` into the project (or point at a shared copy).
   Set `CGF_GRAPH`, `CGF_BUILD_CMD`, `CGF_EXTS` if the project's indexer isn't the graft default.
2. Inspect `git config --get core.hooksPath` and preserve existing hook chains before
   adding the three triggers. Their guard invocation can be backgrounded:
   ```bash
   bash scripts/context-graph-refresh.sh >/dev/null 2>&1 &
   # post-rewrite: same. post-checkout: guard on [ "$3" = "1" ].
   ```
   `.git/hooks` is not necessarily the active location, and `.git` may be a worktree
   pointer file. Use the configured hook directory; namespace graph/cache state
   per worktree so one branch cannot overwrite another branch's context.
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

## Guardrails carried over from the graft security review

- Do **not** run an indexer's `init` if it rewrites global agent settings, nor a `--deep` mode
  that ships source to a third-party LLM, nor a local `viz` server with an open network issue.
  Wire only the reviewed capabilities (project-scoped MCP + a build command).
  This limits configuration/data-exposure scope; it does not eliminate package,
  hook or supply-chain risk, and past findings need re-checking on upgrade.
- Pin the indexer version; re-check on upgrade.
- Treat the graph as **derived, gitignored** state — never committed, always rebuildable.

## Lessons from the adopted integrations

- **Context before broad exploration, source before consequential claims.** Use
  graph navigation for symbols, callers, interfaces and bounded worker/reviewer
  context. Check load-bearing claims against current source and tests. The graph
  is a derived structural map, not the vision-to-release delivery record.
- **Record the effective surface.** FeedEval ADR-035 adopted root-pinned dependency
  and committed Claude shims; exam-prep ADR-0065 repeats that pattern but remains
  proposed. Per-developer MCP is a separate choice. A Claude hook's existence does
  not prove Codex/Gemini runtime parity. The observed shim also has global fallback
  resolution: a manifest pin alone does not prove which package was loaded.
- **Missing query evidence is not an empty graph.** During the earlier FeedEval
  audit, the attempted query failed with invocation/no-graph diagnostics. This
  follow-up found the graph file and installed 0.10.1 package. Recheck CLI syntax,
  working directory, version and graph freshness before diagnosing absence; use
  source fallback when a successful query cannot be obtained.
- **Do not overstate freshness.** The guard scans configured file extensions, not
  Git's tracked-file inventory. Mtime checks can miss deletion, renamed/older files,
  unsupported languages and preserved timestamps; suppressed scan errors can look
  fresh. Rebuild exits do not alone prove expected graph output. These are open
  hardening tasks, not guarantees supplied by the current helper.
- **Budget overlapping refresh mechanisms.** Upstream currently documents query
  auto-refresh; verify the pinned version's implementation before also adding
  session/git-trigger rebuilds. A background start is not completion evidence.
- **Treat savings as estimates.** Historical ADR query estimates and upstream
  benchmarks are not measured end-to-end savings for this audit. Evaluate repeated
  exploration, latency, actual known token cost and accepted outcomes on matched
  tasks before choosing a default for every project.

Upgrade/freshness acceptance should exercise changed and deleted files, branch and
worktree switches, concurrent build/query, missing package, failed build and fallback
resolution. Name unsupported cases; do not silently call stale output authoritative.
See [the upstream project](https://github.com/trailhq/Graft) for current capabilities,
and [the integration map](../INTEGRATIONS.md#graft--adopted-context-provider) for the
bounded recommendation. These notes do not install or upgrade Graft.
