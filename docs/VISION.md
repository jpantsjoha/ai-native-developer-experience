# Vision — Governed Delivery for Human–AI Teams

`join-the-team` should make a mixed human–AI delivery team behave like one coherent
delivery system. Human Product Owners and subject-matter experts retain authority over
intent, priority, acceptance, architecture, risk, and external effects. AI planners and
workers increase throughput inside those boundaries without fragmenting decisions,
duplicating work, or spending unbounded time and tokens.

The unit of delivery is not a prompt or an agent session. It is an accepted outcome
contract that can be decomposed into owned, independently verifiable work and traced
through implementation, review, release, observation, and learning.

The harness succeeds when it makes these behaviours routine:

- the Product Owner validates requirements before implementation is dispatched;
- the delivery orchestrator owns the plan and decomposes accepted outcomes into a
  dependency-aware task tree;
- planner context stays focused on intent, interfaces, decisions, and convergence while
  worker context stays bounded to one independently verifiable task;
- GitHub milestones, epics, tasks, pull requests, and repository documents point to one
  another without competing as sources of truth;
- roadmap, status, changelog, ADRs, and evidence are reconciled at defined lifecycle
  transitions;
- planning quality is measured partly by avoided rework, conflict, duplication, context
  churn, and agent spend—not by task or commit volume alone;
- teams capture delivery surprises so later human and agent trajectories become shorter.

## Product principles

1. **Intent is scarce.** High-quality requirements and acceptance decisions are
   non-delegable Product Owner work, even when an agent drafts them.
2. **Planning is execution leverage.** Ambiguity removed by a capable planner reduces
   worker churn, context use, and total cost.
3. **One decision, one owner, one record.** Parallel planners may refine independent
   branches of a task tree; they may not decide the same cross-cutting question twice.
4. **State is durable and derived.** GitHub tracks work state; repository documents track
   intent, decisions, operating truth, and release history.
5. **Review is cheaper than rework.** Independent, decorrelated review lenses are part of
   the plan and budget, not an optional final flourish.
6. **Learning closes the loop.** Scope changes, surprises, and failed assumptions update
   the durable plan before more work is dispatched.

## Current focus

The first implementation milestone is the delivery-planning control plane described in
[`requirements/DELIVERY-PLANNING-SYSTEM.md`](../requirements/DELIVERY-PLANNING-SYSTEM.md).
It will add a shared installed workflow, minimal planning placeholders, coordinated skill
contracts, and deterministic traceability checks without turning the harness into a
heavyweight project-management product.
