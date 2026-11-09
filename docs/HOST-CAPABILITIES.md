# Host capabilities

DevEx Charter is a contract layer, not a harness. The same risk tiers, handoffs, review
and Definition of Done apply on every host. What changes per host is how the contract is
loaded and enforced. This page records that difference so each control maps to a native
capability, an adapter, or an explicit "not established".

## The matrix

| Capability | Claude Code | Codex | Kimi Code | Antigravity (agy) | OpenCode (candidate) |
| --- | --- | --- | --- | --- | --- |
| Project instructions | `CLAUDE.md` (same contract as `AGENTS.md`) | `AGENTS.md` | Plugin `sessionStart` skill | `GEMINI.md` (`contextFileName`) | `AGENTS.md`, then `CLAUDE.md` as fallback |
| Skills discovery | Plugin `skills/` | `.agents/skills/`, `~/.agents/skills/` | Plugin `skills` path | Plugin `skills/` | `.agents/skills/`, `.claude/skills/`, `.opencode/skills/` |
| Session start / context injection | `SessionStart` hook (`startup`, `clear`, `compact`; `hooks/hooks.json`) | Not established; invoke `using-the-harness` | `sessionStart` skill | Root `hooks.json` | No session-start event; a plugin `session.hook.context` could inject it |
| Slash commands | `/devex-charter:*` (or `/join-the-team:*`) | Not packaged | Not packaged | Not packaged | `.opencode/commands/*.md` (needs conversion) |
| Fresh-context reviewer (subagent) | Subagents ([docs](https://code.claude.com/docs/en/sub-agents)) | Not established | Dispatch mapped via `skillInstructions`; reviewer independence not established | Dispatch mapped ([tool map](../skills/using-the-harness/references/antigravity-tools.md)); reviewer independence not established | `general` subagent (docs) |
| Install | Marketplace `join-the-team-marketplace` | Plugins UI or skills copy | `/plugins install <repo>` | `agy plugin install <repo>` | Skills and `AGENTS.md` discovery; plugin via npm |
| Guide | [claude](install/claude.md) | [codex](install/codex.md) | [kimi](install/kimi.md) | [antigravity](install/antigravity.md) | [opencode](install/opencode.md) |

"Not established" means this repository has no verified evidence, not that the host lacks
the feature. OpenCode cells come from its documentation, checked 9 November 2026
([skills](https://opencode.ai/docs/skills/), [rules](https://docs.opencode.ai/docs/rules/),
[commands](https://opencode.ai/docs/commands/),
[server plugins](https://opencode.ai/docs/build/plugins/server)); none has been verified
by a live run here. Update a cell only with evidence, and date it.

## Harness choice and your own ways of working

We track public harness benchmarks to keep the contract aligned with current practice.
The [Harness Leaderboard](https://huggingface.co/spaces/joelniklaus/harness-leaderboard)
(v0.1.2, read 9 November 2026)
compares coding-agent harnesses with the model, provider and reasoning effort held fixed,
three attempts per task, bootstrap confidence intervals for ties, and cost metered outside
the harness. [Harness Lens](https://huggingface.co/spaces/harness-hub/harness-lens)
(read 9 November 2026)
documents how harnesses differ in prompts, tools, compaction and extensibility, and links
each claim to its source.

Two lessons carry over, and both point the same way:

- **The best harness depends on the model.** No single host wins everywhere, so the
  contract stays host-neutral and the routing unit is a host and model pair.
- **Configuration changes results.** Context window, compaction and output limits move
  outcomes, so every evaluation and routing receipt records the host, harness and version.

We cite the method, not the rankings: the published board covers a few open models and
changes between versions. In the end the most effective setup is hyper-personalised. It
is the one that encodes *your* team's ways of working, the one you repeat until you are
very good at it together. DevEx Charter supplies the shared contract and the evidence
discipline; your team supplies the practice, and measures it on its own work.
