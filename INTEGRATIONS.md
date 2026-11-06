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

Versions below were verified on 2026-07-19 against public listings; re-verify before
pinning into a project profile.

| Craft lane | Companion plugin | Provider capability | Tested version | Licence |
|---|---|---|---|---|
| Agent methodology (TDD, debugging, plan execution) | [superpowers](https://github.com/obra/superpowers) | `agent-methodology` | 6.1.1 | MIT |
| Simplicity discipline / anti-over-engineering | [ponytail](https://github.com/DietrichGebert/ponytail) | `simplicity-review` | see repo | see repo |
| Frontend design quality | [impeccable](https://github.com/pbakaus/impeccable) | `design-review` | 3.9.1 | Apache-2.0 |
| UI generation (tokens, components) | [ui-ux-pro-max](https://www.claudepluginhub.com/) | `ui-generation` | 2.6.2 | see repo |
| Token/compression economy | [caveman](https://www.claudepluginhub.com/) | complements `cost-guardrail` | 1.9.0 | see repo |

Listing a plugin is an interoperability note, not an endorsement or a warranty. Each
project profile names its own providers and fallbacks.

## Graft — adopted context provider

**Recommendation, 2026-09-26:** use [Graft](https://github.com/trailhq/Graft) as an
optional code-context provider where structural navigation reduces repeated source
exploration. It complements the harness; it does not replace requirements, tests,
decision records or independent review. Small/documentation-only tasks may gain
little from indexing. Keep direct source search/reading as the fallback.

FeedEval's accepted ADR-035 pins `@nanonets/graft` **0.10.1** with a lockfile and
committed Claude hook/helper/skill wiring; MCP registration remains per developer.
Exam-prep reuses the root dependency and hook pattern. Its ADR-0065 is still marked
**proposed**, despite installed wiring: adoption evidence and decision ratification
must be reported separately. Both installed package versions and local graph files
were inspected on 26 September; fresh successful queries were not demonstrated here.

The adopted boundary is local structural indexing; `--deep` stays off under those
project decisions. Resolve the package from the repository root, record the effective
provider/version, and review hook/configuration changes before installation or
upgrade. Do not generalise a historical package security review to newer versions.
Do not copy upstream skill bodies into this plugin. The installed Graft guidance
may help with navigation, but cannot override this harness's source verification
or authority rules.

Read [Context-Graph Freshness](docs/CONTEXT-GRAPH-FRESHNESS.md) for wiring and its
limits, and the [audit addendum](docs/HARNESS-WORKFLOW-AUDIT-2026-09.md#graft-adoption-addendum)
for provenance and remaining work. No Graft dependency, MCP registration or hook
is automatically installed by this recommendation.

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
