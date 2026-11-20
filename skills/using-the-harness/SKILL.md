---
name: using-the-harness
description: Session-start orientation for this team harness. Load first, before any work. Explains the operating contract, that every delivery ask enters through delivery-orchestrator, and how installed companion plugins supply agent-craft capabilities while this harness supplies the team contract. Trigger at the start of every session.
---

# Using the Harness

This is a **team operating harness**: one shared contract for humans and AI agents
working in the same repository — same rules, same risk tiers, same evidence, same
definition of done. It exists to make a mixed human–AI team coherent, not to make one
agent faster.

A skill supplies a repeatable procedure. It never supplies permission or accountability.

## First actions, every session

1. **Ground in the contract.** If this project has adopted the operating model, read its
   project profile before anything else (`docs/operating-model/PROJECT-OPERATING-PROFILE.md`),
   then the manual it binds. Load the mapped delivery workflow, current STATUS,
   ROADMAP and any applicable checkpoint before planning. Check dates and executable
   commands against current evidence; a stale profile is a finding, not a fact to
   silently preserve. Hooks provide orientation, not proof that these reads happened.
2. **Classify risk before acting.** Map the requested work to R0–R3. Round ambiguity
   upward. Confirm authority at that tier before any consequential, destructive,
   external, or credential-touching action.
3. **Enter through the orchestrator.** Load `delivery-orchestrator` for every delivery
   ask. It reads the records and brings in the roles the work needs.

The shared plugin is provider-neutral. Host adapters implement invocation; the project
profile selects authorised reviewers, subscriptions and budgets. Independent Council
review is a capability, not a fixed roster. See the [review contract](../pr-reviewer/references/independent-council.md).

## Installation and project adoption

A user-level installation makes the skills available across that user’s projects; a
project installation shares a selected baseline with collaborators. Neither creates
project authority. Use the host’s selected skill location, including bundled references
and scripts, without assuming a copied `.agents/skills/` directory.

For a new adoption, route to `operating-model-bootstrap` from the consumer project.
Ground its project-owned vision, workflow and profile: ticket system, owners, model
selection, executable checks, review, release and observation. Existing records and
explicit operator authority take precedence. Load detailed skills when needed; an
unadopted project needs orientation and an adoption path, not the full delivery process.

## Core invariants — not negotiable

- **Classify risk before confirming authority.** Approval is scoped to actual risk.
- **Infer intent; never infer permission.** Useful intent is not a grant of authority.
- **Receipts, not polish.** Produce an artefact or a pass/fail verdict, not a narrative.
- **Review binds to the exact candidate.** Any change after review invalidates it.
- **`seed` is not `active`.** A seed profile supports design and R0/R1 work only.
- **Never invent a project fact.** Unknowns get an owner and a resolving trigger.
- **Insufficient evidence is a stop, not a prompt to improvise.** Tag the roster role
  that owns the decision; silence never converts to permission.

## Skill routing

**Every delivery ask enters through `delivery-orchestrator`**, whoever asks and however
small: a goal, a plan, a ticket, a progress question, a review, a release. It reads the
project's records, then brings in the other skills as roles. Its SKILL.md holds the role
table, the persona map and the quality sequence.

That holds when the operator names a skill or its command: the orchestrator reads the
records, then loads the named skill. It holds for a project that has not adopted the
operating model: the orchestrator sends it to `operating-model-bootstrap`.

**One exception.** A specialist skill may be called directly for a bounded question that
changes nothing: a cost estimate, a platform health check, a performance measurement, a
read-only review. When such a call turns into a change, hand the work to the orchestrator
before continuing. The rule is
[AMH-001 FR-6](../../requirements/ADOPTION-MODES-HITL.md).

## Companion plugins

Agent-craft capabilities may be provided by installed companion plugins instead of these
skills — see `INTEGRATIONS.md` for the evaluated map (simplicity discipline, TDD
methodology, frontend design review, and similar craft lanes).

- Route craft work to an installed companion when the project profile names one as the
  provider. Do not re-implement a capability an installed companion already provides.
- Companions supply capability, never authority. This harness's risk tiers, evidence,
  and review gates still apply to their output.
- No companion installed? The baseline skills above are the fallback. Record the
  equivalent and its owner in the project profile; do not silently skip the capability.

## Harness tool mapping

Skills name actions, not tools. The per-harness translation lives outside the
canonical skill bodies:

- **Antigravity (Gemini)** — read `references/antigravity-tools.md` (in this skill's
  directory) before acting; it maps subagent dispatch, task tracking, and file/search
  actions to Antigravity's native tools.
- **Kimi Code** — the plugin manifest's `skillInstructions` carry the mapping.
- **Claude Code / Codex** — the skills' action vocabulary resolves to the native
  tools of the same names.

## Anti-rationalization table

| Excuse the agent makes | Counter |
|---|---|
| "The skills are just docs — I can skip them" | The skills are the harness. Skipping them is running without the contract. |
| "This task is too small for a skill" | Gates are proportional to risk — R0/R1 is cheap. Skipped small gates are where big failures rehearse. |
| "The companion plugin handles quality" | Companions own craft. Authority, evidence, and completion semantics stay here. |
| "I'll edit the skill body to fit my tools" | Porting adds a thin adapter or tool mapping. Canonical skill bodies never change per harness. |
| "I remember the contract from earlier" | Sessions compact and clear. Re-ground in the tracked profile; memory is not the contract. |
| "The user seems in a hurry" | Speed is easy. Safe speed is engineered. Hurry raises risk tier, it does not lower it. |

## When unsure

Route through `delivery-orchestrator`. Record every unresolved fact with an owner and
the trigger that resolves it. Stop before any R2/R3 mutation or external action that
lacks explicit authority and runnable controls.
