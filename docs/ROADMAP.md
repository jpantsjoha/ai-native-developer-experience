# Delivery roadmap

## Next priority: Harness delivery benchmark v1

JP accepted this sequence on 5 November 2026. Prove material delivery outcomes before
adding coordination features or changing model routing. Start with GCP exam prep;
DevEx Charter branding is outside the treatment. This section owns the next build
order; the earlier delivery table below is historical context.

| Priority | Work package | Exit evidence |
| --- | --- | --- |
| 1 | Freeze baseline and candidate harness instructions, project commit, host/model, tools and resource budgets | Reconstructable arm manifests; treatment separation verified, including globally injected instructions |
| 2 | Select historical GCP exam prep tasks with clear requirements and executable acceptance | Pre-change checkouts, task briefs, independent labels and hidden acceptance/regression checks; completed solutions withheld from agents |
| 3 | Build the smallest end-to-end replay adapter around existing EvalOps | Disposable checkouts; planning, implementation, local validation and independent review; artifacts, failures, retries, timing and resource usage linked to Phoenix |
| 4 | Run a three-task feasibility pilot with repeated runs | Unchanged-harness comparison and deliberately failing control demonstrate noise and failure detection; no superiority claim |
| 5 | Freeze and run a larger paired held-out benchmark | Randomised/counterbalanced order, complete attempt ledger, effect sizes, uncertainty and regression report; exported evidence passes live verification |
| 6 | Adopt supported changes in one project, then consider global promotion | Accepted benchmark disposition, observed project outcomes and rollback; no automatic global rollout |

### Experiment contract

The unit of success is an independently accepted deliverable, not an agent completion
message, approval count or only tests written by the implementing agent. Each case
traces product objective → requirement/task → delivered artifact → acceptance evidence.
The end-to-end boundary is a locally validated, independently reviewed deliverable;
production deployment is not part of the replay. Use scratch checkouts and local gates,
not live issue churn, production changes or GitHub Actions/AI.

Keep model, tools and resource limits matched initially. Compare frozen instruction
bundles; a bundle result does not attribute the effect to each individual skill. Test
model routing and parallel execution separately after the instruction experiment.
Freeze the larger sample size, repetitions, material improvement threshold, uncertainty
method, regression tolerances and total budget before holdout execution; the three-task
pilot cannot establish general superiority. A smaller cost is not a win if quality falls.

Measure requirement acceptance, hidden regressions, user-journey behaviour, critical
defects and harmful changes; elapsed time, review/repair rounds and human intervention
minutes; parent/worker usage including cache/retries; and traceability/status accuracy
and authority compliance. Unknown usage is unknown, not zero. Retain failures, timeouts
and missing runs in planned coverage; do not select only successful repetitions.

Keep answer-bearing patches, later docs and solution history out of task-agent inputs.
Acceptance checks and labels are independently owned. Inspect treatment separation:
if new global instructions contaminate the baseline, or separation cannot be established,
label the run feasibility/sensitivity only, not causal evidence for adoption. Phoenix
verification establishes record integrity, not that the harness is better.

### Scope and dependencies

The existing [EGM protocol](evaluation/egm-review/PLAN.md) isolates review instructions;
its 24-case/144-execution proposal is not an approved sample size for this new whole-task
benchmark. Keep datasets, treatment claims and execution budgets distinct. The
[coordination pilot](planning/SQUADROOM-ADOPTION.md) remains planned and subordinate
to this measurement-first priority; do not build its runtime as a benchmark prerequisite.
Use existing host capabilities and EvalOps before adding infrastructure.

File the execution work item and acceptance criteria before runner implementation,
inspect project contracts and active owners, and validate/review the exact runner and
evaluators before inference. The dedicated session handoff is in [STATUS](STATUS.md).

## Other proposed experiments under workflow-value outcome 3

[Coordination pilot](planning/SQUADROOM-ADOPTION.md): capability/reuse decision →
contract fixtures → durable handoffs and integration controls → paired Phoenix proof →
optional read-only DevDash view. [EGM review measurement](evaluation/egm-review/PLAN.md)
remains independently controlled; do not combine treatments. Implementation children
must be filed and accepted before code. DevEx Charter is the selected name; [#34](https://github.com/jpantsjoha/ai-native-developer-experience/issues/34)
delivered the rebrand, released as v0.5.0 on 6 November 2026. Open: live host migration
checks and upstream listing moves, per the [migration gates](install/rebrand.md).


**Owner:** harness maintainer. Order is by accepted outcome, not skill count.

| Order | Outcome / work item | Exit evidence | State |
| --- | --- | --- | --- |
| 1 | #32 / PR #33: project/user adoption and golden-thread delivery from intent to live | Fresh consumer journey, preserved existing records, local checks and independent review | Delivery tracked by PR #33 and v0.4.0 |
| 2 | Publish v0.4.0 and reconcile installation behaviour | Chosen release version, host install/update checks and rollback | Tag/release owns publication state; live host trials remain |
| 3 | #34 / PR #35: DevEx Charter rebrand, released as v0.5.0 | Aligned manifests, migration guide, local checks and independent review | Released; host migration and listing moves remain |
| 3 | Demonstrate adopted workflow value | One bounded contributor trial: accepted outcome, friction, rework, effort and limits | Proposed; no savings baseline |
| 4 | #24: context loading and incremental review findings | Bounded trial, retained finding history, fixed quality floor | Proposed; prioritise observed friction |
| 5 | #23: decision-record hygiene | Existing-record validation with negative fixtures and owned rollout | Captured; not implemented |

PR #28 (release/review controls) and PR #31 (guarded routing) are merged source changes.
Their merge does not establish package release, installed adoption or efficiency gains.

Use [HARNESS-ADOPTION](HARNESS-ADOPTION.md) for applicable service-transition prerequisites,
conversation provenance and capability ownership. These are extensions of existing
mechanisms, not additional skills or an automatic learning system. Optional commercial
experiments do not block engineering acceptance.

Release/tag/install follows the [source-release decision](../architecture/decisions/ADR-003-source-release.md) and operator authority.
Source merge, package release and observed adopter outcomes are distinct milestones.
