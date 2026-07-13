# Agent Skills Library

A portable, reusable skills library for agent-powered delivery teams.

> **Speed is easy. Safe speed is engineered.** — JP, #HarnessEngineering

These skills encode the discipline that helps agentic systems stay safe and coherent. They
are distilled from the DX-001 harness and firsthand delivery experience. Borrow and adapt
the patterns; they do not make a project production-ready by themselves.

Each skill is a `SKILL.md` in its own directory. Keep the tracked canonical copy under
`.agents/skills/<name>/SKILL.md`. Configure a thin adapter or discovery path when a chosen
assistant expects a different location; do not maintain divergent skill constitutions.

---

## The 13 Skills

| Skill | One-line purpose |
|---|---|
| [`spec-first-delivery`](./spec-first-delivery/SKILL.md) | Force plan / HLD / ADRs before any code is generated |
| [`adversarial-gate`](./adversarial-gate/SKILL.md) | JP's red-team pass: "how would I break this?" — catches brittle assumptions before they ship |
| [`release-readiness`](./release-readiness/SKILL.md) | Go / no-go gate: failure modes, rollback, cost, prod bar, definition of done |
| [`delivery-orchestrator`](./delivery-orchestrator/SKILL.md) | Decompose an epic into atomic parallel tasks; route to the right skill (meta-router) |
| [`the-architect`](./the-architect/SKILL.md) | Architecture decisions, trade-off analysis, ADR authoring |
| [`adk-expert`](./adk-expert/SKILL.md) | Google ADK orchestration patterns; boundaries not tutorials |
| [`gcp-well-architected`](./gcp-well-architected/SKILL.md) | GCP guardrails: IAM least-privilege, data boundaries, cost, residency |
| [`mcp-server-scaffold`](./mcp-server-scaffold/SKILL.md) | Scaffold and govern an MCP server as a bounded tool seam |
| [`domain-validator`](./domain-validator/SKILL.md) | Validate agent output against declared domain rules before trusting it |
| [`pr-reviewer`](./pr-reviewer/SKILL.md) | Review gate: correctness, reuse, simplification — receipts not polish |
| [`cost-guardrail`](./cost-guardrail/SKILL.md) | LLM/token cost awareness: model tiering, budgets, right-sizing |
| [`sitrep`](./sitrep/SKILL.md) | Synthesise a status / standup / situation-report from work state |
| [`operating-model-bootstrap`](./operating-model-bootstrap/SKILL.md) | Install a versioned manual, profile, adapters, checkpoints, and exact-candidate evidence contract for a human–AI squad |

---

## Philosophy

- **Treat “10% model / 90% harness” as a heuristic, not a measured constant.** These skills
  make the surrounding system explicit and testable.
- **Exit criteria over aspirational guidance.** A skill that says "ensure quality" is decoration. A skill that says "done means these three checks pass" is a harness.
- **Receipts, not polish.** Every skill produces a concrete artefact or a pass/fail verdict, not a narrative.
- **Attribute the Adversarial Gate to JP (Jaroslav Pantsjoha)** — the name and “how would I
  break this?” framing are his #HarnessEngineering contribution. The anti-rationalisation
  table format was adopted after reviewing Addy Osmani's MIT-licensed
  [`agent-skills`](https://github.com/addyosmani/agent-skills).

Rinse and repeat.
