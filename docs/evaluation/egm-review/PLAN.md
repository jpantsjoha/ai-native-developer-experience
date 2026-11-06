# EGM review upgrade: before/after measurement plan

Date: 4 November 2026. Owner: harness maintainer; decision owner: JP.
State: proposed preregistration, no experiment run or measured improvement claimed.
Branch: `codex/egm-review-measurement`. Base: `6245074681cf3990160b8ef95185925522bff416`.

## Objective and scope

Determine whether design comprehension, design/delivery reconciliation and qualified
independence claims improve review correctness enough to justify their whole-process
cost. This branch retains the exact historical before/after instructions for testing;
it does not install another global guide or change adopter repositories.

Trace: reliable AI-native delivery → this measurement requirement → cases and expected
findings → paired experiments → verified Phoenix evidence → adopt/revise/revert decision.
Existing roadmap outcome 4 owns demonstrated workflow value. File a bounded work item
before implementing the runner; this planning branch is not a filed execution ticket.

## Controls and hypotheses

Use baseline.md (saved before 3 November additions) versus candidate.md (reviewed
addition), verified with guide-hashes.json. This is a controlled replay, not a claim
that historical real-world outcomes were measured before deployment. The guide was
already globally adopted; calendar before/after alone would confound model, task and
host changes. Missing historical time/tokens remain unknown.

Primary comparison: baseline versus all three additions. Later diagnostic arms may
add comprehension only, drift only and independence qualification only, each pinned
separately before use. A combined win does not prove which addition caused it.

Hold model/version, effort, tools, source packet, task budget and dataset version
constant within each pair. Test Codex and Claude as separate host strata; do not pool
or claim an untested host. Start with the authorised subscribed Codex route. Local
Ollama reviewers are a later separate model-selection experiment, not substitutes for
required Council approval. No hosted API spend or GitHub Actions/AI is authorised.

## Golden cases and staged review

Author 12 calibration cases and 24 held-out cases, separated by source/bug family,
not random variants of the same source. Holdout: eight design-comprehension cases,
eight drift cases, eight independence-evidence cases. Within each group include
four seeded failures and four clean/legitimate-unknown controls. Reserve historical
incidents as candidates only after independent confirmation of the expected finding.
Synthetic cases keep proprietary project material out of portable artifacts.

Each case binds requirement IDs, exact source/design hashes, expected findings,
severity, allowed unknowns and forbidden assertions. Ground truth requires an
independent reviewer plus JP adjudication of ambiguous cases before freezing. The
same model must not write and grade its own cases. No fabricated human labels.

The 144-run primary experiment measures natural full-workflow bundle effects. The
baseline receives its historical policy and the candidate its added staging policy;
each has the same source materials available, but the candidate controls staged timing.
Score final review outcomes under the same labelled rubric. A common-stage explanation
diagnostic is deferred, excluded from the primary estimand and requires its own frozen
budget, run count and denominators before execution.

For the candidate comprehension stage, capture the design-only first response before disclosing accepted
requirements, source, REVIEW.md and test results. Do not compare this first response directly with a baseline response that already
saw source or requirements. The deferred diagnostic would stage the same materials
for both arms. Count all added stages in the primary experiment cost.

For drift, include implementation defects, stale documentation, approved deviations,
unresolved decisions, superseded prototypes and harmless renames. For independence,
include observable fresh-context evidence and unknown host injection. Reward calibrated
claims, not assertions of impossible isolation. Do not give answer keys to task agents.

## Metrics and denominators

| Change | Primary measure | Regression guard |
| --- | --- | --- |
| Explain design back | Correct required propositions / all labelled propositions; missing information correctly marked unknown | Invented requirements; missed critical acceptance conditions |
| Design versus delivery | Confirmed-defect recall and adjudicated finding precision; four-class confusion matrix | False blockers on clean cases; harmful fixes; approved deviations called defects |
| Independence claims | Unsupported isolation claims / all applicable cases; completeness of available provenance | Blanket unknown despite available evidence; fabricated launch/read receipts |
| Whole process | Wall-clock, parent + worker tokens/cache/retries, review rounds, repair effort and human minutes | Quality loss hidden by lower token usage; unavailable usage treated as zero |

Case success requires every critical expected finding, no harmful false positive,
correct disposition and no unsupported independence claim. Record metric denominators
and case-level outputs. Timeouts/errors/missing verdicts count as failures; unattempted
cases remain in planned coverage. Report completed-only scores only alongside the
planned denominator. Unknown cost/usage is null with a reason, never zero. Local zero
provider fees do not mean zero machine or human cost.

Run three fresh repetitions per held-out case per arm: 144 planned task executions
for the initial two-arm experiment, subject to a frozen resource/time budget. Randomise
and counterbalance arm order with a recorded seed. Repetitions are not independent
cases: bootstrap paired differences by case/family, retaining all repetitions within
each cluster. Report 95% intervals, effect sizes and discordant cases, not just means.
This is a pilot; 24 cases cannot establish rare-event safety or universal improvement.

## Proposed decision rule, frozen before execution

Adoption requires all 144 planned slots to have valid observed outcomes and all 72
case/repetition pairs to be complete. Model errors/timeouts count as observed failed
outcomes. Unattempted, infrastructure failure and contaminated slots have distinct
statuses and do not meet complete valid coverage. Any such slot, early stop or empty
run makes this pilot inconclusive for adoption; retain all records and report coverage.
No replacement/retry may overwrite a primary slot. Diagnostic retries are separate;
rerunning for adoption requires a newly frozen complete paired experiment, retaining
the first attempt. Never select the best repetition.

Primary estimand: mean within-case candidate-minus-baseline case-success difference,
first averaging three repetitions per case, then equally weighting all 24 cases.
No-regression dimensions are proposition correctness (higher better), defect recall
and precision (higher better), and unsupported isolation claim rate (lower better).
A zero precision denominator is undefined, not perfect; undefined dimensions prevent
adoption. Compute elapsed-time overhead on all 72 paired valid task executions.

No newly introduced critical miss, harmful fix or blocker waiver is acceptable.
Provisional adoption evidence requires a positive lower 95% confidence bound on the
paired overall case-success difference, no negative point estimate in any primary
quality dimension, and no more than 20% increase in median whole-process elapsed time.
Token and human-effort changes must be reported; missing effort data prevents an
end-to-end efficiency claim. These thresholds are proposed policy, not empirical facts;
JP owns acceptance before execution. Small or uncertain differences mean inconclusive,
not success. Revise on calibration only; a revised policy needs untouched holdout cases.
Stop on resource guards, budget exhaustion or repeated blocker findings; retain failures.
A review cap never turns an unresolved blocker into an accepted trade-off.

## Phoenix and evidence contract

Reuse the single local EvalOps/Phoenix service. Initialise this repository, pin the
synthetic corpus and commit it before pushing a new dataset version. Use one immutable
holdout dataset version for both arms. Experiment names include protocol version,
arm, host/model and repetition. Record guide/corpus/rubric/prompt/checker hashes, exact
candidate commit, model identity/parameters, host/version, seed, permitted tools,
observed input provenance and unobservable context explicitly.

Store per-case outputs and deterministic scores, independently adjudicated findings,
error/retry dispositions and parent/worker resource measurements. Export each experiment
and run `evalops verify` against live Phoenix, then compare paired case IDs. A replay
of captured output must be labelled replay; it is not new model inference. Integrity
PASS and quality PASS are separate fields and separate claims. The planned-slot ledger
is authoritative for adoption: EvalOps export can exclude examples with missing
repetitions, and verify allows explicit exclusions. Reconcile all 144 slot IDs, case IDs,
repetitions, errors and exclusion reasons with Phoenix exports before computing the
paired decision; an export aggregate must not replace this denominator check.

Required artifacts: frozen protocol/manifest, case family split, independent labels,
raw run ledger, Phoenix dataset/version/experiment links, exported verified records,
paired report with intervals, and JP's adopt/revise/revert disposition. Dashboard shows
coverage, correctness, harmful false positives and cost/latency side by side. No single
health score or approval count stands in for these measurements.

## Delivery sequence and completion

1. Planning branch: pin both guides, protocol and ownership; independent plan review.
2. File execution work item; freeze cases, independent labels, thresholds and budgets.
3. Implement the smallest adapter around existing EvalOps; local tests must inject
   errors, missing verdicts, duplicate case IDs, leakage, changed digests and harmful
   false positives. Fresh exact-candidate Council review before benchmark execution.
4. Run sequentially within resource guards, export/verify, paired analysis and decision.
5. Observe the scoped adopted workflow over 20 eligible changes or 30 days (whichever
   comes first), reporting coverage, reverts, escaped defects and human effort. This
   observational follow-up supports monitoring, not the controlled causal estimate.

Done for this branch's planning slice means pinned artifacts, explicit limitations,
local documentation checks and substantive independent plan review. It does not mean
runner delivery, Phoenix experiment creation, measured gains or plugin release.

## Adversarial check

A verbose reviewer could flag everything, game unknowns, or leak labels across cases.
Clean controls, precision, harmful-fix checks, provenance completeness and family splits
counter these. Sequential experiment order can confound results with load; counterbalance
and record resources. Summaries and approval counts can hide failures; retain raw attempts
and planned denominators. Before inference, inspect available host launch/configuration evidence for each arm.
If global candidate instructions reach the baseline, or evidence cannot establish
separation of the treatment instructions, stop the causal experiment. Any bounded
execution then needs a separately labelled feasibility/sensitivity protocol and cannot
support adoption. Log this as contamination or unobservable separation, not a clean
baseline. Other unobservable host context remains explicitly unknown. Isolate supplied
policy packets without asserting full host isolation.
