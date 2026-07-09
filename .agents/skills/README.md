# Agent Skills Library

A portable, reusable skills library for agent-powered delivery teams.

> **Speed is easy. Safe speed is engineered.** — JP, #HarnessEngineering

These skills encode the discipline that keeps agentic systems safe, coherent, and production-worthy. They are distilled from the DX-001 harness spec and real delivery experience. Borrow the patterns — your mileage may vary. The harness is the other 90%.

Each skill is a `SKILL.md` in its own directory. Drop any skill into `.agents/skills/<name>/SKILL.md` (or `~/.claude/skills/`) and invoke it by name.

---

## The 12 Skills

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

---

## Philosophy

- **The model is roughly 10% of a working agent; the harness is the other ~90%.** These skills are harness.
- **Exit criteria over aspirational guidance.** A skill that says "ensure quality" is decoration. A skill that says "done means these three checks pass" is a harness.
- **Receipts, not polish.** Every skill produces a concrete artefact or a pass/fail verdict, not a narrative.
- **Attribute the Adversarial Gate to JP (Jaroslav Pantsjoha)** — the "how would I break this?" framing and its anti-rationalization table are his coinage under #HarnessEngineering.

Rinse and repeat.
