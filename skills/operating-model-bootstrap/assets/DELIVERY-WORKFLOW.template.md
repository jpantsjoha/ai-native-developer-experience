# <Project Name> Delivery Workflow

This file defines how accepted intent moves through planning, implementation, review,
delivery, observation, and learning. The operating manual supplies the universal state
machine; this project workflow maps that contract to the team's roles and work system.

## Work-system mapping

| Delivery record | System of record | Project location |
| --- | --- | --- |
| Vision and outcomes | Repository | `<path>` |
| Requirements and Product Owner acceptance | Repository | `<path>` |
| Architecture decisions | Repository | `<path>` |
| Roadmap order and gates | Repository | `docs/ROADMAP.md` |
| Milestones, epics, tasks, and assignment | GitHub Issues (unless explicitly mapped otherwise) | `<URL or project>` |
| Current derived status | Repository | `docs/STATUS.md` |
| Released behaviour | Repository | `CHANGELOG.md` |
| Checkpoints and exact-candidate evidence | Repository | `docs/operating-model/` |

## Lifecycle

1. **Intake** — capture the problem, actor, desired outcome, Product Owner and source/date.
   Conversation-derived intent is proposed evidence, not permission; link it to the
   existing issue/spec and retain accepted/superseded decisions.
2. **Accept** — the Product Owner validates scope, priority, acceptance criteria, and
   milestone. Agent-drafted intent remains a draft until this gate passes.
3. **Plan** — `delivery-orchestrator` creates the dependency-aware task tree, ownership,
   context boundaries, success tests, budgets, and documentation impact. Include applicable
   operational receiving-owner, support, recovery and handover prerequisites before
   the releases they enable.
4. **Decide** — human SMEs accept required ADRs and constraints before dependent work is
   dispatched.
   Select available model/effort against the project’s declared policy and task risk;
   use deterministic tools first and count review/retry costs. Installation does not
   activate a model-routing pilot or authorise a subscription change.
5. **Execute** — bounded human or agent workers implement independently verifiable tasks
   in isolated mutable lanes.
6. **Integrate** — one named integration owner assembles pinned outputs and runs the
   convergence gate.
7. **Review** — independent reviewers apply declared, decorrelated lenses to the exact
   candidate; conditions block until resolved.
8. **Deliver and observe** — an authorised operator releases, watches the declared
   signals, and rolls back when thresholds are crossed.
9. **Reconcile and learn** — update roadmap gates, derived status, release changelog,
   evidence, risks, and reusable delivery learnings.

## Role boundaries

- Product Owner owns vision outcomes, user journeys, requirements, priority and acceptance.
- CXO oversight challenges strategic fit, affordability, risk and operational ownership.
- Test strategy owns acceptance-to-check coverage; it does not accept product scope.
- Delivery orchestrator owns plan coherence and re-planning; it does not approve product
  intent.
- Planners own assigned planning subtrees and cross-cutting decisions; they do not
  implement delegated leaf tasks.
- Workers own one bounded task and its evidence; they do not change sibling scope.
- One integration owner assembles; independent reviewers refute; the operator authorises
  external effects.

## Re-planning trigger

Pause affected descendants when evidence changes an outcome, acceptance criterion,
interface, dependency, risk, budget, or ownership boundary. Record the new evidence,
supersede stale tasks or decisions, obtain the required human validation, and only then
resume dispatch.

## Project controls

- Product Owner acceptance evidence: `<field, issue check, or signed record>`
- Maximum active lanes: `<number>`
- Planner / worker / reviewer capabilities and host mapping: `<risk/effort fit and evidence>`
- Review attempt/time ceiling and escalation owner: `<limit and owner>`
- Selected skill maintainers and review triggers: `<existing profile routing record>`
- Epic cost and time ceiling: `<limit>`
- Model selection policy and permitted subscriptions: `<project policy or existing baseline>`
- Deployment target, promotion authority and rollback trigger: `<profile or release decision>`
- Post-release observation and receiving owner: `<signal, window and owner>`
- Convergence command: `<command>`
- Live work-system reconciliation: `<command or owned manual process>`
- Status reconciliation trigger: `<trigger>`
- Changelog rule: material delivered behaviour only
- Escalation path: `<human role and channel>`

## Golden thread: evolving intent to accepted capability

Use the locations in the work-system mapping, including existing casing and paths;
do not create competing Status.md/STATUS.md or Roadmap.md/ROADMAP.md records.

1. Product Owner captures incoming intent with source/date, stable requirement ID,
   actor, outcome, business journey, scope and observable acceptance criteria.
   Keep proposed, accepted, changed and superseded requirements distinguishable.
   Do not publish private source conversations in public issues or the package.
2. Map accepted requirements to vision outcomes and roadmap milestones. CXO oversight
   checks strategic fit, cost/risk and operating ownership on material changes;
   a simulated executive role cannot approve on behalf of an accountable human.
3. Delivery orchestrator first checks current STATUS, open issues/PRs and worktrees.
   Reuse existing work, coordinate with its owner, then create or amend GitHub Issues
   by default (an explicitly configured tracker may replace it). Use milestones and
   linked epic/story/task issues only to the depth the work needs.
4. Each actionable ticket records requirement IDs and source links, parent/milestone,
   owner, dependencies, scope/exclusions, T-shirt size (XS/S/M/L/XL with uncertainty),
   checkable Definition of Done, test commands or owned manual checks, and authority.
   Split L/XL work before dispatch where independent acceptance is possible. Sizing is
   relative effort/uncertainty, not a promised duration or a model-selection rule.
5. Test strategy maps each acceptance criterion to the real user path, appropriate
   unit/integration/journey checks, failure cases and environment. Match tests to risk;
   passing component tests alone cannot prove a user-facing end-to-end capability.
6. Version changed workflows and ADRs alongside the requirement revision. Preserve
   supersession links; an ADR changes a decision, not silently the accepted outcome.
   Orchestrator updates affected descendants, tests and milestones with Product Owner
   acceptance and CXO input where material. Unaffected authorised work may continue.
7. Independent PR review uses a fresh read-only subagent, including an adversarial
   lens against requirements, failure/recovery and test adequacy. Bind verdict and
   executed checks to the exact candidate; self-review is preparation, not approval.
8. On completion, reconcile each ticket's delivered behaviour with its original and
   current accepted requirement. Partial coverage stays open or becomes an explicit
   linked remainder; an issue closure or a mentioned ID is not semantic acceptance.
9. Record merged changes under Unreleased. On authorised release, link the version,
   GitHub tag/release and included PRs/requirements in CHANGELOG. Distinguish merged,
   released, installed/deployed and observed use; none implies the next. STATUS owns
   in-flight work and blockers, ROADMAP owns remaining outcomes and sequence.
10. After verified merge, fetch and fast-forward a clean main checkout where safe.
    Confirm PR merged state and that this lane's changes are integrated (squash/rebase
    may change commit IDs). Remove only this lane's clean, no-longer-needed worktree
    and local/remote branch; preserve uncommitted or unintegrated work and other owners'
    lanes. Prune stale worktree metadata only after checking the worktree inventory.

Reconcile these records at intake, scope change, handoff, merge and release. Update
agent entrypoints only when the shared contract itself changes; operational progress
belongs in the records they reference. Never self-amend authority to pass a gate.
The orchestrator reports broken links and semantic gaps; this workflow is an agent
procedure, not an automatic tracker synchroniser or proof of requirement coverage.
