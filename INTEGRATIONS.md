# Companion Plugins — Integration Map

This harness owns the **team contract**: authority, risk tiers, evidence, review, and
completion semantics for mixed human–AI teams. It deliberately does **not** compete in
agent-craft lanes that other plugins already own. Composition over duplication: route
craft work to an installed companion, keep the contract canonical here.

Two rules make this safe:

- **Reference, never vendor.** Companion plugins are named by repository and pinned
  version below. Their skill bodies are never copied into this repository — vendored
  copies drift, and drift is what this harness exists to catch.
- **Capability, never authority.** A companion plugin supplies a procedure. It does not
  grant permission, does not lower a risk tier, and its output still passes this
  harness's review and evidence gates.

**Standalone guarantee:** every skill in this repository works with zero companions
installed. Companions are recorded in the project profile as optional providers with a
named fallback; absence never silently drops a capability.

## Evaluated companions

Versions below were re-verified on **2026-11-25** against primary sources: each
repository's latest GitHub release, its `.claude-plugin/plugin.json`, its licence as
GitHub detects it, and (for packages) the npm or PyPI registry. They are the current
upstream releases, **not versions re-tested with this harness**. Re-verify before
pinning into a project profile. The previous check was 2026-07-19.

| Craft lane | Companion plugin | Provider capability | Upstream version (2026-11-25) | Licence |
|---|---|---|---|---|
| Agent methodology (TDD, debugging, plan execution) | [superpowers](https://github.com/obra/superpowers) | `agent-methodology` | 7.0.2 | MIT |
| Simplicity discipline / anti-over-engineering | [ponytail](https://github.com/DietrichGebert/ponytail) | `simplicity-review` | 5.3.3 | MIT |
| Frontend design quality | [impeccable](https://github.com/pbakaus/impeccable) | `design-review` | 4.11.0 | Apache-2.0 |
| UI generation (tokens, components) | [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | `ui-generation` | 2.15.0 | MIT |
| Token/compression economy | [caveman](https://github.com/JuliusBrussee/caveman) | complements `cost-guardrail` | 4.2.0 | Apache-2.0 |

Three of these crossed a major version since July: superpowers 6.1.1 → 7.0.2, impeccable
3.9.1 → 4.11.0 and caveman 1.9.0 → 4.2.0. ui-ux-pro-max moved 2.6.2 → 2.15.0. Treat a
pinned profile on the July versions as unverified until its owner re-tests.

### Sources and data leaving the machine

Read this before recommending a companion for client work. "None documented" means the
README says nothing either way; it is not a guarantee.

| Companion | Version source (checked 2026-11-25) | Network and telemetry behaviour (from the upstream README) |
|---|---|---|
| superpowers | [v7.0.2 release](https://github.com/obra/superpowers/releases/tag/v7.0.2), published 2026-11-03; `plugin.json` 7.0.2 | The optional brainstorming visual companion loads a logo from the maintainer's site, sending the plugin version. Off with `SUPERPOWERS_DISABLE_TELEMETRY`, `DISABLE_TELEMETRY` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`. |
| ponytail | [v5.3.3 release](https://github.com/DietrichGebert/ponytail/releases/tag/v5.3.3), published 2026-10-29; `plugin.json` 5.3.3 | None documented. |
| impeccable | [skill-v4.11.0 release](https://github.com/pbakaus/impeccable/releases/tag/skill-v4.11.0), published 2026-11-24; `plugin.json` 4.11.0 | A new design fetches visual directions from impeccable.style, even with telemetry off. Anonymous telemetry is on by default; off with `DO_NOT_TRACK=1`, `npx impeccable telemetry off`, or `"telemetry": false` in `.impeccable/config.json`. |
| ui-ux-pro-max | [v2.15.0 release](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/releases/tag/v2.15.0), published 2026-08-13; `plugin.json` 2.15.0 | README states the search scripts make no network calls. |
| caveman | [v4.2.0 release](https://github.com/JuliusBrussee/caveman/releases/tag/v4.2.0), published 2026-11-22; `plugin.json` 4.2.0 | Now a skill plus a local proxy. The CLI sends usage stats by default (commands, token counts, install ID, OS, IP); off with `caveman telemetry off` or `DO_NOT_TRACK=1`. The skill-only install (`npx skills add JuliusBrussee/caveman`) has no proxy. |

## Context graph

A code graph answers "where is X, who calls Y" from a prebuilt index instead of
re-grepping. Keep it fresh with [the context-graph freshness pattern](docs/CONTEXT-GRAPH-FRESHNESS.md),
and read its guardrails before running either tool's `init` or `install`. Both tools are
indexers the project runs, not a provider of any harness capability, and neither is
needed by any skill here.

| Companion | Version source (checked 2026-11-25) | Licence | Data leaving the machine and files it writes |
|---|---|---|---|
| [Trail-code](https://github.com/trailhq/Trail-Code), formerly graft | npm [`@trailhq/trail-code`](https://www.npmjs.com/package/@trailhq/trail-code) 0.30.5, published 2026-11-17 (the repository has no GitHub releases). The old package `@nanonets/graft` still runs the same code and is at 0.30.1. | MIT | The code map is built locally with tree-sitter; `trail build --deep` sends code to the model provider you configure. Anonymous telemetry is **on by default**; off with `DO_NOT_TRACK=1` or `trail telemetry disable`. `trail init` reads your own messages from the repo's past Claude Code transcripts (via your Claude Code, so they go to Anthropic) and, when `gh` is signed in, the review comments on the repo's last 50 merged PRs. It also adds hooks and a statusline to Claude Code, and with `--agents` it removes its wiring from unlisted agents' user-level files unless `--no-global` is passed. `trail init --dry-run` previews the wiring. |
| [Graphify](https://github.com/Graphify-Labs/graphify) | PyPI [`graphifyy`](https://pypi.org/project/graphifyy/) 0.9.120, published 2026-11-25 (matching [GitHub release v0.9.120](https://github.com/Graphify-Labs/graphify/releases/tag/v0.9.120)). It releases almost daily, so pin the exact version. | Apache-2.0 | Code is parsed locally with tree-sitter. Docs, PDFs and images go to an LLM: the assistant's model through the `/graphify` skill, or, for headless `graphify extract`, a backend auto-detected from whichever API key is in the environment. Set `GRAPHIFY_BACKEND=none` (code only, no LLM) or `GRAPHIFY_BACKEND=ollama` (local). `graphify install` writes a skill registration into `~/.claude/CLAUDE.md`; `graphify install --project` writes under the repository instead. |

Listing a plugin or tool is an interoperability note, not an endorsement or a warranty.
Each project profile names its own providers and fallbacks.

## Adjacent plugins — different job, do not cite as companions

These operate near the team-governance space. Study them; do not list them as
providers, and do not re-implement their mechanics.

- **[ecc](https://www.claudepluginhub.com/)** — a large bundle (500+ skills, 100+
  agents) for orchestrating agent teams end to end. Breadth play. This harness's
  answer is depth: risk-tiered authority, evidence bound to the exact candidate, and
  drift-checked adapters — properties a large bundle cannot carry.
- **[claude-apd](https://www.claudepluginhub.com/)** — mechanical pipeline enforcement
  (spec → build → review → verify → commit) with hook-intercepted tool calls, Claude
  Code and Codex only. That is enforcement mechanics for agent commits. This harness
  defines the contract such a pipeline serves — across harnesses, humans included.

## Wiring a companion into a project

1. Install the companion through its own harness-native mechanism.
2. Record it in the project profile's **Companion capabilities** section: provider,
   version, and the fallback used when it is absent.
3. Keep this repository's canonical skills unchanged. If a companion needs a harness
   adaptation, add a thin adapter — never edit a canonical skill body per harness.
