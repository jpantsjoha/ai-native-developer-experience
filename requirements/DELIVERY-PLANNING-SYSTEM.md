# Feature Spec — Delivery Planning Control Plane

**Spec ID:** DPS-001

**Status:** Approved for implementation — Product Owner accepted 2026-07-21

**Product Owner:** Jaroslav Pantsjoha (`@jpantsjoha`)

**Planning owner:** `delivery-orchestrator` capability

**Target milestone:** Pending GitHub milestone creation

**Related vision:** [`docs/VISION.md`](../docs/VISION.md)
**Proposed architecture decision:**
[`ADR-001`](../architecture/decisions/ADR-001-durable-planning-control-plane.md)

## Problem

The harness already documents a strong sequence—specification, planning, atomic tasks,
implementation, evidence, review, release, and status reconciliation—but several parts
remain conventions rather than an operational planning system:

- the Product Owner is named as accountable for requirements, but no skill requires a
  durable validation record before dispatch;
- `delivery-orchestrator` decomposes work but does not own roadmap, milestone, epic,
  task, status, or plan-revision reconciliation;
- planner and worker responsibilities are not explicitly separated, so high-value
  planning context can be polluted by implementation detail;
- the project has no `docs/ROADMAP.md`, no `docs/STATUS.md`, no GitHub issues, and no
  GitHub milestones despite claiming that traceability model;
- agent cost controls inventory calls, but do not budget the planner/worker/reviewer
  topology or measure churn caused by weak planning;
- no deterministic gate checks the cross-references between planning artifacts.

This creates a risk that the plugin teaches good principles while its users—and this
repository—still run delivery from transient chat context.

## Research basis

Cursor's 20 July 2026 article,
[“Agent swarms and the new model economics”](https://cursor.com/blog/agent-swarm-model-economics),
reports that improved task-tree decomposition, planner/worker separation, shared design
records, neutral integration, stacked review, and durable agent-authored context produced
similar or better outcomes with materially lower churn and cost in its SQLite experiment.

The article is evidence for a design hypothesis, not a universal benchmark. This feature
therefore adopts the control patterns while requiring each project to measure its own
quality, cost, rework, and coordination outcomes.

## Users and actors

- **Product Owner (human):** owns outcome, priority, scope, acceptance criteria, and
  acceptance sign-off.
- **Delivery orchestrator (planning capability):** owns decomposition, dependencies,
  plan coherence, context boundaries, cost/concurrency envelope, and reconciliation.
- **Human SME:** validates domain facts, architecture, data, security, or operational
  constraints within an explicit scope.
- **Planner agent:** refines an accepted branch of the task tree; does not implement the
  delegated work or decide questions owned by another planner.
- **Worker agent or human contributor:** executes one bounded task with a falsifiable
  success test and returns evidence.
- **Integration owner:** assembles pinned outputs, resolves contract-level conflicts, and
  runs convergence checks.
- **Independent reviewer:** applies one or more decorrelated review lenses to the exact
  candidate.

## Functional requirements

### FR-1 — Product Owner acceptance contract

Before implementation dispatch, every epic must record:

- problem and desired outcome;
- target users or actors;
- in-scope and out-of-scope behaviour;
- measurable acceptance criteria;
- priority and milestone;
- constraints, risk tier, and cost/time ceiling;
- named Product Owner validation with date and status.

Agent-drafted requirements remain `Draft` until the Product Owner explicitly marks them
`Accepted`. A material scope or acceptance change returns the epic to `Needs PO review`.

### FR-2 — Durable task tree owned by delivery-orchestrator

The orchestrator must lower an accepted epic into independently verifiable tasks. Each
task records:

- parent epic and milestone;
- owner and execution type (`human`, `agent`, or `paired`);
- dependencies and interfaces;
- owned files and mutable resources;
- success test and evidence expected;
- model/tool tier when an agent is used;
- token, cost, time, and retry ceiling;
- documentation and changelog impact.

No implementation task is dispatched while a required specification or ADR dependency
is unresolved.

### FR-3 — Planner, worker, reviewer, and integrator separation

- Planners own decomposition and cross-cutting decisions, not leaf implementation.
- Workers receive only the accepted task contract and relevant decisions.
- Two planners may not own the same design question or mutable subtree.
- Integration is performed by one named owner in a clean worktree.
- Review is independent of the worker and bound to the exact candidate.
- An exception requires a documented reason, risk owner, and compensating review.

### FR-4 — GitHub delivery hierarchy

For projects that use GitHub as the work system of record:

- **Milestone:** outcome/release horizon;
- **Epic issue:** accepted outcome, labelled `type:epic`, assigned to one milestone;
- **Task issue:** independently verifiable unit, labelled `type:task`, containing
  `Parent epic: #<number>` and assigned to the same milestone;
- **Pull request:** closes or references task issues and links the relevant spec/ADR;
- **Repository docs:** link the milestone and epic rather than duplicating mutable task
  state.

Projects using another tracker must record an equivalent mapping in their operating
profile. The plugin must not make GitHub mandatory for non-GitHub teams.

### FR-5 — Document roles and reconciliation

- `docs/VISION.md` owns enduring product direction.
- `docs/ROADMAP.md` owns ordered outcomes, milestones, dependencies, and planning status.
- `docs/STATUS.md` is a dated, derived snapshot of done, blocked, next, risks, and plan
  changes.
- Feature specs own requirements and Product Owner acceptance.
- ADRs own durable architectural decisions.
- GitHub issues own active work state and assignment.
- `CHANGELOG.md` records shipped material changes, not backlog activity.

The orchestrator reconciles roadmap and issue hierarchy after planning or re-planning.
`sitrep` reconciles status after meaningful state changes. Release completion reconciles
status, roadmap, changelog, evidence, and remaining risk.

### FR-6 — Plan revision and learning loop

When a human SME or worker reports new evidence, a failed assumption, or scope pressure:

1. pause affected descendants of the task tree;
2. record the evidence and impacted requirement or decision;
3. re-plan dependencies, budgets, and ownership;
4. obtain renewed Product Owner or SME validation where authority is affected;
5. supersede stale tasks and evidence rather than silently rewriting history;
6. record a reusable delivery learning when it would shorten future work.

### FR-7 — Planning economics

Every multi-agent plan must declare:

- maximum active planner, worker, reviewer, and integrator lanes;
- model tier by role and evidence for the choice;
- per-task and epic-level token/cost/time ceilings;
- retry and escalation limits;
- review budget;
- metrics that distinguish output from churn: duplicate work, superseded tasks, merge
  conflicts, rework, abandoned changes, acceptance escape rate, and cost per accepted
  outcome.

### FR-8 — Deterministic traceability validation

The repository must provide an offline validation command that checks required planning
documents, stable identifiers, lifecycle status values, and local cross-references. A
separate opt-in GitHub reconciliation mode may verify live milestone and issue state when
credentials and network access are available. Offline CI must not depend on mutable
external state.

### FR-9 — Installed workflow definition and minimum templates

The bootstrap must install a project-specific `DELIVERY-WORKFLOW.md` that maps the
universal operating-manual state machine to the adopter's roles, work system, commands,
budgets, and reconciliation triggers. It is the lifecycle contract above the individual
skills:

- the workflow owns stage order, transition guards, role separation, source-of-truth
  boundaries, and re-planning triggers;
- each skill owns the procedure and evidence for its stage;
- the operating profile owns verified project facts and authority;
- checkpoints own resumable task state for consequential work.

The bootstrap must also offer vanilla, minimal `VISION.md`, `ROADMAP.md`, `STATUS.md`,
and `CHANGELOG.md` templates. It must never overwrite an adopter's existing versions.
The templates are operational placeholders, not polished public narratives or
plugin-release content. `VISION.md` seeds outcome framing and Product Owner focus;
`ROADMAP.md` and `STATUS.md` start without claimed work or progress.

The plugin repository's own root `CHANGELOG.md` remains the plugin release history and is
not the same artifact as a target project's installed changelog template.

### FR-10 — Hook and enforcement strategy

Hooks should improve discovery and fail fast without becoming a hidden workflow engine:

- session start and post-compaction orientation should tell the agent to load the project
  profile, delivery workflow, current status, roadmap, and applicable checkpoint;
- hooks may report missing or stale planning artifacts and point to the right skill;
- hooks must not auto-approve requirements, rewrite roadmap/status/changelog, create
  external issues, or mutate lifecycle state;
- deterministic validators and CI enforce schemas and traceability;
- skills and named humans make decisions and perform authorised transitions.

Because hook support differs across harnesses, the canonical workflow must remain usable
without hooks. Surface adapters may add equivalent orientation behaviour without changing
the contract.

## Acceptance criteria

1. `delivery-orchestrator`, `spec-first-delivery`, `sitrep`, `cost-guardrail`,
   `using-the-harness`, and the operating-profile template describe one consistent
   lifecycle and source-of-truth model.
2. Issue templates exist for epics and tasks, with required Product Owner, parent,
   milestone, acceptance, ownership, evidence, budget, and documentation fields.
3. The bootstrap assets include minimal vision, workflow, roadmap, status, and changelog
   templates and the initializer installs them only when the target path is absent.
4. `docs/WORKFLOW.md` and the installed workflow template show Product Owner acceptance,
   planner/worker separation, integration, review, re-planning, and document/GitHub
   reconciliation.
5. The planning validator fails fixtures with a missing required document, invalid
   lifecycle state, missing epic/task parent reference, or broken local cross-reference.
6. `make check` runs the new validator and all existing gates successfully.
7. `CHANGELOG.md` records the planning-control-plane change under `Unreleased` until a
   release is cut.
8. The repository's own Product Owner acceptance and implementation tracking are recorded
   in design artifacts or explicitly pending; installed placeholders are not presented as
   polished external project status.
9. Article-derived claims in public documentation link to Cursor's primary article and
   distinguish Cursor's experiment from this project's own evidence.

## Out of scope

- Building a general-purpose project-management application.
- Treating per-skill prose or hooks as a substitute for the shared workflow contract.
- Automatically creating, editing, or closing external GitHub objects without explicit
  operator authority.
- Mandating a single model vendor or fixed planner/worker model pairing.
- Treating commit count, issue count, or token volume as delivery success.
- Claiming Cursor's experimental results will reproduce in every project.

## Constraints and risks

- The canonical skills must remain vendor- and harness-neutral.
- GitHub-specific mechanics belong in an adapter or documented work-system mapping, not
  in the universal authority kernel.
- Planning overhead must be proportional to risk; R0 work should not require an epic.
- Mutable live issue state cannot be a mandatory offline CI dependency.
- Constitutional skill changes are R3 for this project and require Product Owner approval
  of this spec before implementation.

## Product Owner validation

**Decision:** Accepted on 2026-07-21

**Validator:** Jaroslav Pantsjoha (`@jpantsjoha`)

**Recorded changes:** adopt Option C; add an installed workflow definition; package
vanilla/minimum vision, roadmap, status, and changelog placeholders; keep hooks
lightweight and non-mutating; keep the plugin release changelog distinct from installed
project records.

Implementation may proceed in reviewed slices. Approval authorises the direction and
requirements; it does not declare the acceptance criteria complete. The first slice adds
the bootstrap planning seed in FR-9. Cross-skill lifecycle changes, issue templates, and
deterministic tracker reconciliation remain subsequent delivery work.
