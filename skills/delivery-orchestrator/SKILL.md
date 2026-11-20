---
name: delivery-orchestrator
description: "Default entry point for every delivery ask, from any person: pursue or finish a goal, plan scope, create or change a ticket, ask where we are, what is blocked, what waits on me, are we on track, how do we prove it is done, is it ready to ship, or record a decision. Reads the project's records first, then brings in the role skills (product-owner, the-architect, test-strategy, pr-reviewer, release-readiness, sitrep and the rest) and keeps issues, STATUS, ROADMAP and CHANGELOG straight. Load this before any other skill; skip it only for a bounded read-only question. Also decomposes multi-track epics into parallel tasks."
---

# Delivery Orchestrator

> **The default entry point.** A person states a goal; the orchestrator reads the records,
> brings in the roles the goal needs, and keeps the records straight. The other skills are
> roles it brings in, not tools to pick from a list.

The orchestrator has four jobs: ground the ask in the project's records, decompose work into
the smallest independently executable units, bring in the role that owns each unit, and
**keep the delivery records honest**, because a plan nobody can trust is worse than no plan
and takes longer to discover.

## When to use

Every delivery ask enters here, whoever makes it and however small:

- pursuing or finishing a goal, milestone or epic
- planning scope, or creating or changing a ticket
- "where are we", "what is blocked", "what waits on me", "are we on track"
- "how do we prove this works", "what is the definition of done", "what evidence do we have"
- "is it ready to ship", "review this before merge", "record this decision"
- work that needs several roles, or parallel agents
- records that have drifted: a status file that stops before today's work, a roadmap asking
  for a decision already made, a tracker claiming `gated` with nothing that walks it

**Direct calls.** A specialist skill may be called without the orchestrator only for a
bounded question that changes nothing: a cost estimate, a platform health check, a
performance measurement, a read-only review. When such a call turns into a change, the
skill hands the work here before continuing
([AMH-001 FR-6](../../requirements/ADOPTION-MODES-HITL.md)). A skill the operator names
(`get-it-done`, `wrap-it-up`, `sitrep`) still enters here: read the records, then load it.

## Bring the role in

After the reads, name the role that owns the ask and **load that role's skill before doing
its work**. This file routes; it does not hold the role's procedure. Answering a progress
question without `sitrep`, a proof question without `test-strategy`, or a design question
without `the-architect` is doing the role's work from memory. One ask may need one role or
several; say which and in what order.

## Read first

Before answering or dispatching, read what the project already says. Each record answers one
question; do not answer it from memory.

| Read | Why |
|---|---|
| `VISION` or the README | What the product is for and who it serves; the test of whether an ask belongs |
| `ROADMAP.md` | What comes next and in what order; where the ask fits |
| `STATUS.md` | What is in flight, who owns it and what waits on whom |
| `CHANGELOG.md` | What has merged or released, so finished work is not redone |
| The issue tracker | The scope and Definition of Done of each piece of work |
| The human queue (`HITL/OPERATOR/`, where the project has adopted it) | Decisions and actions waiting on this person |
| The project profile and `DELIVERY-WORKFLOW.md` | Authority, risk tiers and the checks this project runs |

## Who asks, and which roles answer

The same entry serves a solo owner and a team. In a team, a named lead is accountable for
each domain; a solo owner holds every row.

| Person | Words they use | Roles the orchestrator brings in |
|---|---|---|
| Solo owner | "get this done", "plan it", "create a ticket", "what next" | All, in the order the work needs |
| Product owner | priority, requirement, user journey, adoption, "aligned with the vision" | `product-owner`, `spec-first-delivery`, `cxo-oversight` |
| Delivery director | progress, blocked, "on track", "waits on me", golden thread | `sitrep`, `release-manager`, `wrap-it-up` |
| Technical lead | decision, trade-off, design, review, "break this into tasks" | `the-architect`, `adversarial-gate`, `pr-reviewer`, `cloud-expert`, `adk-expert` |
| QA lead | quality, proof, definition of done, evidence, "try to break it" | The quality sequence below |
| Data or SRE specialist | live, errors, cost, performance, "ready to release" | `cloud-checkup`, `release-readiness`, `cost-guardrail`, `frontend-performance-audit`, `system-performance-guardrail` |

## The quality sequence

Quality has no separate entry role: the orchestrator sequences four roles, and a quality ask
starts at the first one that has not been done.

1. `test-strategy` maps each acceptance criterion to a runnable check, before code.
2. `domain-validator` checks agent output against the project's declared rules.
3. `adversarial-gate` argues against the work before it is called done.
4. `pr-reviewer` gives an independent verdict bound to the exact commit.

Each role names the deterministic check that proves its output, or says there is none
(see the "Entry and proof" section of each skill). A judgement is never reported as a
deterministic result.

## The delivery records — the baseline

**One fact, one owner.** Four artefacts carry delivery state, and each answers exactly one
question. Full doctrine, including the issue template and the audit: `docs/DELIVERY-RECORDS.md`.

| Record | The one question it answers | Written when |
|---|---|---|
| **GitHub issues** | *What exactly is this work, and how will we know it is done?* | Before the first line of code |
| **`STATUS.md`** | *What is happening now, and what waits on whom?* | The records task, after each merge batch: one entry per working session, amended by later batches in that session |
| **`ROADMAP.md`** | *What are we building toward, in what order?* | The records task, after each merge batch, when the batch changed what comes next or its order |
| **`CHANGELOG.md`** | *What merged or released, with checks and version links?* | The records task, after each merge batch that merged user-visible work |

The five rules that keep them from drifting:

1. **`ROADMAP` owns build order.** Where another document disagrees about what is next, the
   roadmap wins.
2. **`CHANGELOG` records the proven, not the intended.** A changelog of intentions reads as
   evidence, which makes it worse than none.
3. **An issue not filed is not started.** The tracker is current *before* the code, because the
   failure this prevents is work that accretes from a small fix and is reconciled afterwards,
   if at all.
4. **`gated` means a test proves a user can reach it; `shipped` means a person used it.** These
   two are the ones routinely overclaimed. Code existing is `built`, and deployment is not
   shipping.
5. **One records task per merge batch, solo or parallel.** Builders never edit `ROADMAP`, `STATUS` or `CHANGELOG`; they note the record change their work implies in the PR body. After each batch of merges, the orchestrator (in a solo session, whoever leads it) updates all three together in one records commit or PR. Every entry links its issue or PR, so the files can be cross-checked and never disagree.

## Golden-thread ownership

For intake, dispatch, scope changes and completion, follow the golden-thread section
of the adopting project's `DELIVERY-WORKFLOW.md`, located by its profile. Without an
adopted workflow, start with `operating-model-bootstrap` in the consumer project.
Use the [workflow template](../operating-model-bootstrap/assets/DELIVERY-WORKFLOW.template.md)
as a checklist while mapping existing records; unresolved placeholders are project
questions, not executable paths or permission to invent defaults.
Product Owner maintains accepted intent and priorities; CXO provides material oversight;
test strategy corroborates coverage. The orchestrator actions and reconciles the tickets,
dependencies, status and delivery links. Check in-flight owners before selecting roadmap work.

## Procedure

### Part 1 — Decomposition

0. **Read the records** in "Read first" and state where the ask fits. A small ask ends here, with one role's skill loaded.
1. **Read the spec or brief** — confirm a feature spec or HLD exists. If not, invoke `spec-first-delivery` first.
2. **Identify tracks** — group work into independent tracks (e.g. backend API, frontend, infrastructure, testing). Tracks can run in parallel. Dependencies between tracks must be explicit.
3. **Break each track into atomic tasks** — an atomic task is one that:
   - Can be assigned to a single agent
   - Has a clear input and a clear output
   - Does not require coordination with another concurrent task to complete
   - Can be validated independently
4. **Sequence dependencies** — where task B requires output from task A, mark the dependency. Everything else is parallel.
5. **Assign context boundaries** — each agent gets only the context it needs. Avoid stuffing all specs into every agent's context.

### Part 2 — Skill routing

1. **Map each task to a skill** using the routing table below. If no skill matches exactly, use the closest and note the gap.
2. **Validate integration after parallel work** — run the full regression suite (`make check` or the project's equivalent convergence command) after all parallel tracks complete. Parallel work that skips integration validation is not done.

## Skill routing table

| Task type | Route to skill |
|---|---|
| New feature / epic planning | `spec-first-delivery` |
| Vision, requirements, user journeys and product acceptance | `product-owner` |
| Material strategic, cost/risk or operating ownership decision | `cxo-oversight` |
| Acceptance coverage and executable user-path checks | `test-strategy` |
| Architecture decision or trade-off | `the-architect` |
| High-stakes design review | `adversarial-gate` |
| Pre-deployment go/no-go | `release-readiness` |
| Release process governance, SemVer, ADR, changelog | `release-manager` |
| Enterprise policy, compliance, or governance alignment | `governance-guardrail` |
| GitHub repo operations: CI triggers, billing, issues, labels, branch protection | `github-manager` |
| Google ADK agent patterns | `adk-expert` |
| Cloud infrastructure guardrails (GCP, AWS, Azure, Alibaba Cloud) | `cloud-expert` |
| MCP server design or governance | `mcp-server-scaffold` |
| Agent output validation | `domain-validator` |
| PR or code review | `pr-reviewer` |
| LLM cost or model selection | `cost-guardrail` |
| Status or standup synthesis | `sitrep` |
| Plugin-directory, marketplace, or curated-list submission | `plugin-submission` |
| New repo or operating model install / repair | `operating-model-bootstrap` |
| Delivery controls: source of truth, issue/PR conventions, DoD, escalation | `delivery-orchestrator` (own it here) |
| An agreed goal to pursue autonomously to a merged outcome | `get-it-done` |
| Close out a frozen in-flight set to merged, deferred or operator-blocked | `wrap-it-up` |
| Developer-machine contention, orphaned automation browsers, cloud-sync stalls | `system-performance-guardrail` |
| Read-only SRE checkup of a GCP project: probes, status table, one `OVERALL:` line | `cloud-checkup` |
| Frontend performance measurement: Core Web Vitals, traces, Lighthouse, heap growth | `frontend-performance-audit` |
| Entry for any delivery ask | `delivery-orchestrator` (you are here) |

## Adoption and review recovery

Use [the adoption guide](../../docs/HARNESS-ADOPTION.md) to reconcile conversational
requirements, skill maintenance ownership, early operational dependencies and measured
improvement. Preserve one integration owner and include review/integration in WIP.

Before consequential review declare the work-item attempt/time ceiling. On repeated
findings or exhaustion, follow [Council loop recovery](../pr-reviewer/references/independent-council.md);
changing candidate or reviewer never erases unresolved findings or spent attempts.

## Outputs

For workflow audits, maturity exits or reconciliation across records, read
[`references/workflow-audit.md`](references/workflow-audit.md). It defines the
vision-to-observation thread, evidence levels, test strategy, promotion and value
feedback. Distinguish declared, implemented, enforced and observed controls.
Track lane identity/effort, mutation boundary, budget, expected output and acceptance
command; check actual lane health before reporting progress. A registry entry is
not proof that a model or reviewer ran.

- Task breakdown: tracks, atomic tasks, dependencies
- Skill routing: task → skill mapping
- Parallel execution plan with integration validation step, naming the integration
  owner, merge order and where each H1–H4 handoff is recorded
- The no-progress limit for each R2/R3 work item
- A brief orchestration summary for the human lead

## Guardrails

- **Atomic means independently validatable.** If you cannot describe how to verify a task in isolation, it is not atomic — split it further or merge it with its dependency.
- **Parallel agents must not share mutable state without a coordination strategy.** If two tracks write to the same file or schema, they are not independent. Use worktrees or serialise them.
- **Integration validation is not optional.** Parallel work that skips the post-merge regression check is not complete.
- **Handoffs are records.** Work changes hands only through the manual's H1–H4 records:
  candidate SHA, checks with exit codes, open conditions, receiver acknowledgement.
- **Activity is not progress.** Count attempts against a newly validated check; a new
  commit or reviewer run does not reset the no-progress limit.
- **Clean up what you merged.** A merged lane left behind is not COMPLETE. Use the
  read-only [lane hygiene report](../../scripts/lane_hygiene.py) as the evidence.
- **Keep agent context lean.** Each agent gets its task spec and relevant ADRs, not the entire repo.

## Model choice at the delegation boundary

Use the adopting project's model-routing policy before dispatch. Record requested
model/effort, allowed paths, Definition of Done and independent checks. Prefer
deterministic tools where sufficient; do not equate a smaller task with a qualified
cheaper model. Track failed attempts, escalation and parent integration costs. Preserve
existing risk floors and stop rules. The [routing guide](../cost-guardrail/references/model-routing.md)
shows a reversible approach; it does not automatically enable routing in consumers.
