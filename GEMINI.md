# GEMINI.md — Always-On Harness Rules

> The model is the easy part. These rules are the harness. Read them before you generate anything.
> **Speed is easy. Safe speed is engineered.**

This file is the always-on "Rules" primitive for this repo. It is portable and opinionated by design — borrow it, adjust it to your team, your mileage may vary.

---

## Design before generate

- Restate the intent before writing code. If you cannot state the goal in one sentence, you are not ready to generate.
- Draft the spec and a first cut together, then **review the spec harder than the code**. A loose spec is where confident-but-wrong output comes from.
- No speculative scaffolding. Build what the task needs, not what it might need later.

## The Adversarial Gate (required reasoning step)

> Coined by JP — Jaroslav Pantsjoha, #HarnessEngineering.

Before you call any change done, answer in writing: **"How would I break this?"**

- Name the failure modes, the missing guardrail, the untested edge, the input you did not validate.
- Argue against your own approach before you proceed. If you cannot find a way to break it, you have not looked hard enough.
- This gate runs on every non-trivial change. It is not optional.

## Receipts, not polish

- Done means checks pass, not that the prose reads well. Evidence over aspiration.
- Every non-trivial change leaves one runnable check behind — a test, an assertion, a command whose output you can paste. If it is not verified, it is not done.
- "Ensure quality" is decoration. "These three checks pass" is a harness.

## File standards

- Every source file opens with a short header or module docstring: what it does, and why it exists.
- Public functions get a docstring — inputs, outputs, and the one edge case that bites.
- Match the surrounding file. Reuse the helpers and patterns already in this repo before writing new ones.
- British spelling in prose; follow the language's own convention in code.

## Where the harness lives

- **Skills / workflows** → `.agents/skills/` (reusable SKILL.md workflows). Look here before inventing a new approach.
- **MCP servers / data seams** → `.agents/mcp_config.json` (governed access to data sources — see the file for the pattern).
- **The full guide** → `DEVELOPER_EXPERIENCE.md` (DX-001): guardrails, gates, spec-driven delivery, CI.

## Quality gates (no merge to `main` without these)

`make lint` · `make typecheck` · `make test` — then the Adversarial Gate above. When an agent misbehaves, **debug the harness first**: inspect tools, context, rules, permissions, and validation before assuming the model is the only cause.

Rinse and repeat.
