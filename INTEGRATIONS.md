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
