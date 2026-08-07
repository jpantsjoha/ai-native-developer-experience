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
| Milestones, epics, tasks, and assignment | `<GitHub or equivalent>` | `<URL or project>` |
| Current derived status | Repository | `docs/STATUS.md` |
| Released behaviour | Repository | `CHANGELOG.md` |
| Checkpoints and exact-candidate evidence | Repository | `docs/operating-model/` |

## Lifecycle

1. **Intake** — capture the problem, actor, desired outcome, and Product Owner.
2. **Accept** — the Product Owner validates scope, priority, acceptance criteria, and
   milestone. Agent-drafted intent remains a draft until this gate passes.
3. **Plan** — `delivery-orchestrator` creates the dependency-aware task tree, ownership,
   context boundaries, success tests, budgets, and documentation impact.
4. **Decide** — human SMEs accept required ADRs and constraints before dependent work is
   dispatched.
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

- Product Owner owns outcome, priority, scope, and acceptance.
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
- Planner / worker / reviewer model tiers: `<mapping and evidence>`
- Epic cost and time ceiling: `<limit>`
- Convergence command: `<command>`
- Live work-system reconciliation: `<command or owned manual process>`
- Status reconciliation trigger: `<trigger>`
- Changelog rule: material delivered behaviour only
- Escalation path: `<human role and channel>`
