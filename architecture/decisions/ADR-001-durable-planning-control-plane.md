# ADR-001: Use a Dual-Record Planning Control Plane

## Status

Accepted — 2026-07-21; implementation remains governed by DPS-001

## Context

The harness needs durable planning that survives agent context loss and supports humans,
agents, and multiple work-management systems. Repository documents are reviewable,
versioned, portable, and suitable for requirements and decisions, but are poor at
high-frequency assignment and queue state. GitHub issues and milestones are effective for
active work state, but mutable external records are weak homes for enduring intent,
architecture, and offline validation.

Cursor's
[agent-swarm economics research](https://cursor.com/blog/agent-swarm-model-economics)
also indicates that task-tree decomposition, shared decision records, role separation,
neutral integration, and stacked review materially reduce coordination churn. The harness
needs those properties without binding every adopter to GitHub.

## Options considered

### Option A — Repository documents only

Store vision, roadmap, status, specifications, decisions, and tasks entirely as Markdown.

- **Benefits:** portable, offline, versioned, reviewable, simple to distribute.
- **Costs:** assignment and queue state become noisy; concurrent status updates collide;
  task closure and milestone reporting require manual maintenance.
- **Failure mode:** documents drift from actual work and become retrospective theatre.

### Option B — GitHub issues and milestones only

Make GitHub the sole source for product intent, decisions, tasks, and status.

- **Benefits:** one live operational queue; strong assignment, filtering, and automation.
- **Costs:** vendor coupling; weak offline operation; mutable decisions; harder exact-
  candidate review; inaccessible to adopters using other trackers.
- **Failure mode:** issue churn erases decision context and the plugin ceases to be
  platform-neutral.

### Option C — Explicit dual record with deterministic reconciliation

Keep durable intent and decisions in repository documents; keep active assignment and work
state in GitHub or an equivalent tracker. Define which artifact owns each fact, require
cross-references, and validate the stable local half offline.

- **Benefits:** preserves portability and decision history while supporting live delivery
  operations; allows GitHub-specific adapters without contaminating the universal kernel.
- **Costs:** introduces reconciliation work and requires clear conflict rules.
- **Failure mode:** if ownership boundaries are vague, both sides become competing sources
  of truth.

## Decision

Adopt **Option C**. The Product Owner confirmed the dual-record direction on 2026-07-21.
Implementation scope and acceptance criteria remain governed by DPS-001.

The repository owns vision, requirements, ADRs, roadmap outcomes, derived status, release
history, evidence, and learnings. GitHub—or the adopter's equivalent tracker—owns active
milestone, epic, task, assignment, and queue state. Stable IDs and links connect them.
`delivery-orchestrator` owns planning and re-planning coherence; Product Owners and SMEs
own validation and authority; `sitrep` owns derived status reconciliation.

Offline CI validates documents, identifiers, schemas, and local links. Live tracker
reconciliation is an explicit, credentialed operation and cannot silently block offline
plugin use.

An installed `DELIVERY-WORKFLOW.md` sits above the individual skills and maps this model
to project roles, tools, and transitions. Skills implement stages; they do not each define
a competing end-to-end workflow. Minimal vision, roadmap, status, and changelog templates
are bootstrap assets for adopting projects, not external-facing narratives for this
plugin.

## Consequences

### Easier

- Work can resume after context compaction or agent turnover.
- Planner and worker contexts can remain deliberately different.
- Product Owner validation becomes visible and auditable.
- Roadmap, issue hierarchy, evidence, and release history can be reconciled.
- Adopters can map the same semantics to Jira, Linear, Azure Boards, or another tracker.

### Harder

- Every project must define its work-system mapping and reconciliation cadence.
- The orchestrator and sitrep skills must reject ambiguous source-of-truth ownership.
- Teams must distinguish planning changes from shipped changelog entries.
- Live GitHub automation requires separate authority, credentials, and failure handling.

### Foreclosed

- Treating transient chat or a single agent's task list as the delivery plan.
- Letting multiple planners independently decide the same architectural question.
- Equating high task, commit, or token volume with successful delivery.

## Adversarial Gate

**Verdict:** PASS. DPS-001 received Product Owner acceptance on 2026-07-21.

| Failure mode | Mitigation / ownership |
| --- | --- |
| Repository documents and live tracker become competing truths | Define field-level ownership: documents own durable intent and decisions; the tracker owns assignment and active state. Reconciliation reports conflicts instead of choosing silently. |
| Planning ceremony makes small work slower and more expensive | Apply the risk tiers: R0 uses a bounded task note; R1 uses lightweight acceptance and verification; epics, HLDs, and full budgets are reserved for multi-track or R2/R3 work. |
| Product Owner validation becomes a delivery bottleneck | Record an acceptance SLA and delegation boundary in each project profile. Work that changes outcome or acceptance still blocks; silence never becomes approval. |
| Cheaper worker models reduce quality or create more rework | Require a quality floor and evidence-based tier choice. Escalate tasks that exceed retry or uncertainty thresholds; compare total cost per accepted outcome, not token price alone. |
| Stale or unavailable GitHub state breaks portable/offline use | Keep offline validation limited to stable local artifacts and link syntax. Live reconciliation is explicit, credentialed, and reported separately. |
| Teams optimise task, commit, or token counts instead of outcomes | Measure acceptance escape rate, rework, supersession, conflicts, retries, lead time, and cost per accepted outcome; volume metrics never constitute completion. |

### Conditions carried into implementation

- The source-of-truth matrix must appear consistently in the skills, workflow, profile,
  and validator documentation.
- R0/R1 proportionality must be testable, not an informal exception.
- Product Owner revalidation must trigger on material outcome, scope, or acceptance
  changes.
- External issue and milestone creation remains an explicitly authorised action.
- Model tiering may not lower the applicable acceptance or review standard.
