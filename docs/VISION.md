# Vision — Shared Delivery Practices for Human–AI Teams

`join-the-team` can be installed for one project or made available across a user’s
projects. Adoption establishes shared practices for planning, tickets, model choice,
testing, review and the route to live, with authority and controls owned by each project.

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

Make the existing delivery tools usable from project, user and plugin installations.
The bootstrap already creates the planning seed; the next improvement is a reliable
adoption journey and a clear account of what users must configure. See
[adoption acceptance](../requirements/ADOPTION-DELIVERY.md) and the [roadmap](ROADMAP.md).
Demonstrate value through a bounded adoption trial before claiming less rework or lower
cost. Broader traceability automation remains proposed, not an installed capability.
