# AutoHarness research and guarded learning proposal

**Date:** 2026-09-26 · **Owner:** JP · **Parent:** HFE-001
**Join the Team baseline:** `331a984c688daf89b38d252b1ee83ed3553d2421`
**External source:** [tigerless-labs/autoharness](https://github.com/tigerless-labs/autoharness),
commit `ca39a72e4353ebef11b7de13c1fc7fa5f4df421b`, manifest 0.5.3, MIT.
**Scope:** primary-source research, independent source inspection and isolated
synthetic probes. No installation, live hooks, session-log collection or model calls.

## Assessment

AutoHarness implements a useful automatic skill-maintenance loop. Join the Team
provides a broader delivery contract: intent, ownership, architecture, deterministic
tests, independent review, release and observed acceptance. They address overlapping
problems at different levels. Our learning process is less automatic and its actual
use is less instrumented; AutoHarness's usage-driven selection does not establish
that accepted outcomes improve. Neither has demonstrated comparative optimum value.

Recommendation: borrow observable learning and proposal provenance, then evaluate
changes through the existing delivery gates. Do not enable automatic edits to our
global skills. No new skills are proposed; useful lessons can amend existing scripts,
tests, references, runbooks or routing. The following is a design recommendation,
not an implemented learning service or permission to install one.

## Verify the screenshot's claims

| Claim | What the sources support |
| --- | --- |
| Learns from real sessions | Hooks capture transcript windows; a reflector stages proposals and a deterministic promoter writes accepted changes. Reflection is triggered by tool activity, not only at session start |
| No daemon | Lifecycle evaluation happens at SessionStart; reflection and consolidation launch detached child processes. Daemon-free does not mean no model calls or background cost |
| Survives by use | Retention uses Skill invocation counts divided by layer request counts since creation, with probation and capacity rules. Counts begin at PreToolUse, before successful completion; this measures use, not verified adherence or usefulness |
| Only touches its own skills | Modification paths check ownership, but an isolated same-name create overwrote a human-owned fixture at the inspected commit. The blanket claim is not upheld by that path |
| 42%→78% CORE-Bench | HAL reports Opus 4.5 at 42.22% with CORE-Agent and 77.78% with Claude Code. This is a scaffold comparison, not an AutoHarness before/after result |
| 4.4k stars / v0.5.3 | GitHub API snapshot reported 4,712 stars; manifest is 0.5.3. Stars are adoption interest, not effectiveness. The latest GitHub Release endpoint returned 404; the manifest badge is not proof of a published GitHub Release |

The [HAL leaderboard](https://hal.cs.princeton.edu/corebench_hard) identifies the
Claude Code submission by Nicholas Carlini and separately reports 95.5% after manual
validation. Do not mix that grading correction with the scaffold comparison. The
older [HAL paper](https://arxiv.org/html/2510.11977v1) linked by AutoHarness supports
model/scaffold interaction generally, but its original CORE-Bench table predates
this exact Opus 4.5 pair. It also found equal or lower accuracy with higher reasoning
effort in 21 of 36 tested combinations. That supports measuring task/model/effort
fit; it does not select today's best model or prescribe low effort universally.

## Mechanisms worth learning from

The source separates model proposals from a deterministic writer. The writer checks
format, paths, ownership on modification, required reason/evidence, and heuristic
safety rules. Individual file replacement is atomic. Records distinguish proposal,
landing, rejection, use, view, patch and retirement. Session start makes the learned
library discoverable and reports prior rejected changes. Consolidation tries to
reuse an existing rule rather than accumulate duplicates. Archives and snapshots
provide recovery mechanisms. These are implemented mechanisms, not proof of semantic
correctness or a complete transaction across concurrent sessions.

Source anchors:
[staging](https://github.com/tigerless-labs/autoharness/blob/ca39a72e4353ebef11b7de13c1fc7fa5f4df421b/src/autoharness/stage_skill/server.py),
[promoter](https://github.com/tigerless-labs/autoharness/blob/ca39a72e4353ebef11b7de13c1fc7fa5f4df421b/src/autoharness/hook/promoter.py),
[metrics](https://github.com/tigerless-labs/autoharness/blob/ca39a72e4353ebef11b7de13c1fc7fa5f4df421b/src/autoharness/lib/metrics.py),
[lifecycle](https://github.com/tigerless-labs/autoharness/blob/ca39a72e4353ebef11b7de13c1fc7fa5f4df421b/src/autoharness/lib/lifecycle.py).

## What we verified and what remains uncertain

| Finding | Evidence | Consequence for adoption |
| --- | --- | --- |
| Human-skill collision | Fresh temporary-root probe: human update refused; same-name create accepted, content replaced, ownership changed to agent. Promoter lines 51–54, 129–158; validator lines 211–212 | Refuse adoption until create collision/ownership protection is proven through the public proposal path, including races and symlinks |
| Merge provenance lost in transport | Fresh `server.stage` probe accepts delete with `absorbed_into`, but staged intent omits it. Schema declares field; `_intent` lines 139–154 drops it | End-to-end tests must preserve the field and prove the receiving absorption check executes; component tests alone miss this |
| Capacity is not a total context bound | Fresh pure-function probe: 200 probation members at mature capacity 50 cause no archives. Source also excludes viewed zero-use survivors; index reads live managed skills | Use explicit total context/token and proposal budgets. [Issue #167](https://github.com/tigerless-labs/autoharness/issues/167) independently reports the probation/documentation mismatch |
| Usage is an incomplete objective | Lifecycle denominator spans all layer requests; global counts span projects. Invocation recorded before result; no task-success input in the inspected metrics | Separate eligible exposure, invocation, successful execution and accepted outcome. Never discard rare rollback/security controls for low use |
| Admission is not independent acceptance | Source regex scanner explicitly describes heuristic limits; evidence need only be nonempty, not authenticated against a trace. Passing proposals land without a separate semantic review | Keep our exact-candidate tests and independent review; readable or frequently invoked instructions can still be wrong |
| Runtime boundaries need integration proof | Child commands include permission-prompt bypass, relying on tool restrictions/hooks; spawn has no explicit subprocess timeout or per-run budget. Linked worktrees resolve to main-root skill storage; global writes affect other projects | Any future trial needs isolated storage, bounded execution and tested enforcement. These source observations are not a reproduced exploit or proof of unlimited provider spend |

The normal staging API does not expose edits to AutoHarness's Python validator.
The concern is promotion of learned instructions and the proven collision path,
not a claim that it routinely rewrites its own admission code. Regex redaction and
path heuristics are useful controls but do not certify all session content safe to
retain or transmit. No private session was read for this research.

Pinned runtime sources:
[spawn](https://github.com/tigerless-labs/autoharness/blob/ca39a72e4353ebef11b7de13c1fc7fa5f4df421b/src/autoharness/hook/spawn.py),
[routing/storage](https://github.com/tigerless-labs/autoharness/blob/ca39a72e4353ebef11b7de13c1fc7fa5f4df421b/src/autoharness/lib/layer.py),
[safety scanner](https://github.com/tigerless-labs/autoharness/blob/ca39a72e4353ebef11b7de13c1fc7fa5f4df421b/src/autoharness/lib/skills_guard.py).

The exact inspected source has a successful
[hosted CI run](https://github.com/tigerless-labs/autoharness/actions/runs/36142489286).
Its workflow runs lint and non-live tests on Python 3.11/3.12; it tolerates empty
pytest collection. Live host E2E is a skipped placeholder, and public source excludes
the referenced experiment directory. We did not rerun the upstream suite or verify
private experiments. Green component CI coexists with the reproduced boundary gaps.

Probe script and result are retained locally in the adjacent audit-evidence directory:
`probe_autoharness.py` and `autoharness-probe-results.json`. The script imports the
pinned source, uses explicit disposable roots for both layers and makes no network
or model calls. These probes test narrow seams, not the complete Claude host loop.

## Comparison with Join the Team

This compares inspected mechanisms and declared scope, not a head-to-head benchmark.

| Dimension | AutoHarness | Join the Team | Useful next step |
| --- | --- | --- | --- |
| Learning capture | Automatic episode reflection and consolidation | Operator/session-driven audits and reviewed repository changes | Capture proposed lessons from existing delivery receipts; keep promotion separate |
| Discoverability | Session index and usage/view counters | Shared router and project adapters; no equivalent portfolio invocation telemetry proven | Detect unavailable, never-exposed and failed controls separately from unused controls |
| Quality criterion | Structural admission plus usage-driven retention | Candidate-bound tests, independent review and acceptance contract; enforcement still uneven | Require outcome evidence for learning promotion, retain planted negative tests |
| Golden thread | Per-skill reason/evidence ledger | Vision→requirement→decision→issue→test→release→observation | Link every proposed optimisation to the original failure and requirement |
| Recovery | Archives and pre-curation snapshots | Git history, reviewed changes and release/rollback procedures | Demonstrate rollback of one learning change; keep evaluator outside the learner's write scope |
| Scope/portability | Claude plugin, project/global learned skill trees | Portable contract with runtime adapters | Trial project-local; require separate evidence before wider adoption |
| Proven benefit | Implementation/CI evidence; no comparative outcome study found in inspected public material | Five-project delivery adoption evidence; causal savings still unmeasured | Compare accepted outcomes and all effort at a fixed quality floor |

Our most material gap is observable learning: we have a learning procedure but lack
a routinely measured closed loop showing which harness change helped which outcome.
Our existing controls are also incomplete: structural validation does not resolve
semantic drift, local review files do not authenticate identity, and all adopter
enforcement paths are not proven. AutoHarness does not remove those gaps.

## Proposed bounded learning loop — no new skills

```text
existing delivery receipt → evidenced lesson → deduplicated change proposal
    → fixed-baseline regression/refusal tests → independent candidate review
    → authorised project-local trial → observed outcome → retain or revert
```

Use the existing DPS-VALUE, DPS-TRACE and DPS-REVIEW contracts rather than a new
service or parallel backlog. A proposal records source candidate/failure, requirement,
target file, expected effect, competing explanation, tests, owner, budget and removal
trigger. Prefer correcting an existing script or reference. Model output can propose;
it cannot redefine authority, acceptance, reviewer independence or test thresholds.

Suggested first experiment: one recurring failure class in one project, using already
retained receipts, initially without activation. Select the eligible task cohort and
baseline before seeing outcomes. Include failed/abandoned work. Keep tests, model
version/effort and relevant environment comparable, or explicitly record differences.
Measure acceptance yield, recurring defects, author/review/integration effort and
known model cost; invocation is a diagnostic. Small samples support an exploratory
decision, not a percentage-improvement claim.

Promotion needs a current candidate, the existing convergence gate, independent PASS,
unchanged protected quality floor, preserved evidence and demonstrated rollback. Test
changes needed for legitimate new requirements are a separately reviewed scope, never
an in-experiment shortcut to improve the score. Unavailable evidence leaves the change
unpromoted. Exceeded budget or a quality regression stops the trial; no automatic
global rollout, deletion of safety procedures or weakening of CI is proposed.

Minimum future refusal fixtures: duplicate create/human ownership; stale candidate;
lost proposal fields; failed or merely attempted tool invocation; concurrent updates;
protected path mutation; fabricated/missing evidence; renamed/archive recovery;
unbounded probation/index growth; and a popular proposal that fails outcome tests.
These are acceptance requirements for future implementation, not checks added here.

How would I break this proposal? Optimise usage instead of outcomes; learn a temporary
workaround as global policy; remove an infrequently used recovery control; or change
the evaluator to make an optimisation pass. Fixed scope, explicit eligible cohorts,
protected controls, independent review and observable rollback address those failure
modes. Their enforcement must be demonstrated before any automatic activation.
