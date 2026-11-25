---
name: the-architect
description: "A role that delivery-orchestrator brings in. Architecture decisions, trade-off analysis, and ADR authoring. Trigger when a significant technical decision needs to be made, documented, and owned — not when an implementation detail needs a choice. Also trigger on \"should we move from X to Y\" and \"record the decision\"."
---

# The Architect

> **Keep the architecture ladder human-owned.** Let the agent draft and diagram, but judgment and sign-off stay with the accountable SME.

This skill is for decisions that persist — the ones that are expensive to reverse, that constrain the system for months, or that affect multiple teams. Implementation details belong in code review. Architecture decisions belong here.

## When to use

- Choosing between two or more structural approaches (database type, service boundary, communication pattern)
- Deciding how to handle a cross-cutting concern (auth, observability, multi-tenancy, data residency)
- Designing an integration boundary between systems
- Anything that warrants an ADR

## Procedure

1. **State the decision to be made** — one sentence. If you cannot state it in one sentence, it is not one decision.

2. **Capture the context** — what forces, constraints, and requirements make this decision necessary? What is the status quo, and why is it insufficient?

3. **Enumerate the options** — at least two credible options. For each:
   - What are the benefits?
   - What are the costs and trade-offs?
   - What does it require from the surrounding system?
   - What is the failure mode?

4. **Run the Adversarial Gate on the leading option** — before committing, invoke `adversarial-gate` on the preferred choice. A clean gate result is a prerequisite for committing to the decision.

5. **State the decision** — which option is chosen and why. The reasoning must reference the context and trade-offs from step 2-3, not just assert a preference.

6. **Record consequences** — what does this decision make easier? What does it make harder? What does it prevent?

7. **Author the ADR** — match the deterministic delivery-record grammar (`docs/DETERMINISTIC-GATES.md`):
   ```markdown
   # ADR-NNN: <short title>

   ## Status

   Proposed — <YYYY-MM-DD>. Decision owner: <handle>.

   ## Context

   <forces, constraints, why a decision is needed>

   ## Decision

   <the chosen option and reasoning>

   ## Alternatives considered

   <credible options rejected and why>

   ## Consequences

   <what becomes easier, harder, or foreclosed>
   ```
   Store under `architecture/decisions/ADR-NNN-<slug>.md` (or the project's mapped decision
   root in `.delivery.json`). Allowed `## Status` values are `Proposed`, `Accepted`,
   `Rejected`, or `Superseded` (with `**Superseded by:** ADR-MMM` when superseded).
   *Migration note ([ADR-007](../../architecture/decisions/ADR-007-canonical-adr-format.md) —
   reverses the `0.1.6` `ADR/` + `-DRAFT`/`-approved` convention to align with
   `validate_delivery.py` and `docs/DETERMINISTIC-GATES.md`):* `validate_delivery.py` scans
   every `*.md` file under the mapped decision root. Existing adopters using `ADR/` may keep
   that directory by mapping `"decision": "ADR"` in `.delivery.json`, and must update every
   tracked ADR's `## Status` value (`draft` → `Proposed`, `approved` → `Accepted`,
   `superseded` → `Superseded` with `**Superseded by:** ADR-MMM`) before enabling
   `validate_delivery.py`. Legacy YAML frontmatter and `-DRAFT`/`-approved` filename suffixes
   do not fail the validator and may be removed separately (remove stale frontmatter `status:`
   to avoid conflicting human-visible statuses).

8. **Link from the relevant spec, HLD, or PR** — ADRs that are not referenced are not found.

## Cloud vendor routing

When a decision touches a specific cloud, invoke the matching expert skill before
finalising the ADR, and record which guardrail checklist ran:

| Vendor | Skill |
|---|---|
| Google Cloud, AWS, Azure, Alibaba Cloud | `cloud-expert` (read the matching `references/<vendor>.md`) |

Multi-cloud decisions run every relevant checklist; the ADR names them. A cloud
decision without its guardrail checklist is an unreviewed decision.

## Outputs

- `architecture/decisions/ADR-NNN-<slug>.md` (`Proposed` until the accountable human accepts it)
- Trade-off summary (can be included in the ADR or a separate HLD section)
- Updated `architecture/HLD-<feature>.md` if the decision changes the HLD

## Guardrails

- **One ADR per decision.** Bundling multiple decisions into one ADR obscures accountability.
- **The ADR captures reasoning, not just the outcome.** "We chose Postgres" is not an ADR. "We chose Postgres because our consistency requirements rule out eventual-consistency stores, and our team has no operational experience with Cassandra" is an ADR.
- **Architecture is not implementation.** An ADR about which ORM to use is implementation. An ADR about whether the service owns its own database is architecture.
- **Supersede, do not edit.** When a decision changes, create a new ADR that supersedes the old one. History is the point.

## Entry and proof

- **Entry:** `delivery-orchestrator` brings this role in. Enter here directly only for a bounded read-only question.
- **Proof:** None. The output is an ADR with a status; `scripts/validate_delivery.py` checks it is linked. `scripts/` here means the plugin root; a copy of this skill directory alone does not carry it, so name the project's equivalent there.
