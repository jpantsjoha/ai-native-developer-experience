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

## The 19 Skills

| Skill | One-line purpose |
|---|---|
| [`using-the-harness`](./using-the-harness/SKILL.md) | Session-start orientation: the contract, the routing table, and how companion plugins supply craft capabilities |
| [`spec-first-delivery`](./spec-first-delivery/SKILL.md) | Force plan / HLD / ADRs before any code is generated |
| [`adversarial-gate`](./adversarial-gate/SKILL.md) | JP's red-team pass: "how would I break this?" — catches brittle assumptions before they ship |
| [`release-readiness`](./release-readiness/SKILL.md) | Go / no-go gate: failure modes, rollback, cost, prod bar, definition of done |
| [`delivery-orchestrator`](./delivery-orchestrator/SKILL.md) | Decompose an epic into atomic parallel tasks; route to the right skill (meta-router) |
| [`the-architect`](./the-architect/SKILL.md) | Architecture decisions, trade-off analysis, ADR authoring — routes cloud decisions to the matching vendor expert |
| [`gcp-expert`](./gcp-expert/SKILL.md) | Google Cloud guardrails: IAM least-privilege, data boundaries, cost, residency, official-source validation |
| [`aws-expert`](./aws-expert/SKILL.md) | AWS guardrails: IAM, data boundaries, cost, residency, official-source validation |
| [`azure-expert`](./azure-expert/SKILL.md) | Azure guardrails: Entra ID, policy-first governance, cost, residency, official-source validation |
| [`alibaba-expert`](./alibaba-expert/SKILL.md) | Alibaba Cloud guardrails: RAM, residency (mainland/international split), cost, official-source validation |
| [`adk-expert`](./adk-expert/SKILL.md) | Google ADK orchestration patterns; boundaries not tutorials |
| [`mcp-server-scaffold`](./mcp-server-scaffold/SKILL.md) | Scaffold and govern an MCP server as a bounded tool seam |
| [`domain-validator`](./domain-validator/SKILL.md) | Validate agent output against declared domain rules before trusting it |
| [`pr-reviewer`](./pr-reviewer/SKILL.md) | Review gate: correctness, reuse, simplification — receipts not polish |
| [`cost-guardrail`](./cost-guardrail/SKILL.md) | LLM/token cost awareness: model tiering, budgets, right-sizing |
| [`github-manager`](./github-manager/SKILL.md) | Cost-effective, consistent GitHub operations: CI triggers, Actions billing, issues, labels, branch protection, releases |
| [`sitrep`](./sitrep/SKILL.md) | Synthesise a status / standup / situation-report from work state |
| [`operating-model-bootstrap`](./operating-model-bootstrap/SKILL.md) | Install a versioned manual, profile, adapters, checkpoints, and exact-candidate evidence contract for a human–AI squad |
| [`plugin-submission`](./plugin-submission/SKILL.md) | Govern directory and marketplace listings: current policy, artifact eligibility, final confirmation, and receipts |

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
