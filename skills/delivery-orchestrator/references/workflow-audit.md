# Workflow audit and the golden thread

Use for a requested workflow audit, milestone exit, or drift between delivery records.
This is a procedure, not a claim that all of its checks are automated. Apply the
project's profile and accepted scope; R0/R1 work needs a bounded task, not a new epic.

## Trace outcomes, not activity

The golden thread is a set of resolvable links with evidence at each transition:

```text
vision → objective → requirement → decision → milestone / issue → PR / candidate
       → acceptance test → independent verdict → artifact / tag → environment
       → user outcome / observation → learning or opportunity → next objective
```

An existing ID proves a reference resolves; it does not prove the requirement was
implemented. Derive each claimed outcome from its acceptance test and observation.
Use one stable ID per objective/requirement and map it to an owner and outcome gate.
Tests can serve multiple requirements; declare that relationship instead of forcing
artificial one-to-one mappings. Unknown coverage is a gap, not a zero or a pass.

| Record | Owns | Reconcile when |
| --- | --- | --- |
| VISION | User problem and enduring direction | Product direction changes |
| Objective/spec | Measurable outcome, constraints and accepted scope | Scope or acceptance changes |
| HLD | Components, interfaces, data flows and failure boundaries | Architecture changes |
| ADR / engineering decision log | Why a durable choice was made, owner, status and consequences | Decision changes; supersede accepted records |
| ROADMAP | Ordered outcome horizons and dependencies | Planning changes |
| Issue system | Active task scope, ownership, dependencies, milestone and DoD | Before implementation and at each state transition |
| STATUS | Dated, derived current state, blockers, next action and evidence | Meaningful delivery/review transition |
| README | Current user entrypoint and supported capability | User-facing behaviour or setup changes |
| Runbook | Actual operational commands, recovery and observation | Interface or operations changes |
| CHANGELOG | Material changes; Unreleased candidate entries become release history only when delivered | Merge, then release cut |
| Opportunity log | Customer/commercial hypothesis, evidence and next experiment | New market/user evidence; no automatic roadmap promotion |

Record file paths and case in the profile (for example `docs/STATUS.md` versus
`Status.md`); do not create competing files because a template uses a different name.
Archive superseded snapshots with a pointer and date. Keep status short enough to
use; history belongs in git and immutable receipts, not a permanently growing diary.

## Audit four evidence levels independently

For every consequential control record:

| Level | Evidence needed |
| --- | --- |
| Declared | Current policy and named accountable owner |
| Implemented | Executable body/configuration and a successful focused check |
| Enforced | Required path plus a planted violation that is refused; record bypasses |
| Observed | Receipt from the actual candidate/environment and stated observation period |

Do not score these as a single percentage. A green schema validator can coexist
with a stale profile. A local hook can be bypassed. A successful workflow may not
be a required branch check. A reviewer comment may not authenticate a model or
approve the current candidate. Give every unverified level an owner and trigger.

Start with `git status`, branch, HEAD, relevant policy and actual gate definitions.
Separate committed sources from dirty local changes. Preserve the inspected SHA,
source locations, command exit statuses and UTC timestamps. Redact secrets.
For remote state, use bounded read-only queries; API errors, pagination limits and
missing access are incomplete evidence. Never infer protection from workflow YAML.

The GitHub adapter should inspect issues/milestones, PR base/head, reviews and their
commit IDs, checks, main protection/rulesets, tags, release assets and environments.
Do not require live GitHub for offline validation. Report offline conformance and
live reconciliation separately, with freshness and completeness for each.

## Plan, route, execute, integrate

The planner owns the accepted outcome, interfaces, dependency graph and resolving
questions. Workers own bounded implementation. The reviewer independently tries to
falsify the candidate. One integrator assembles pinned inputs and runs convergence.
Roles can share a model family where policy permits; authors cannot approve their
own output. A second model's agreement is evidence, not proof or authority.

Each delegated lane records task ID, risk, complexity, model requested and resolved,
effort, context inputs, owned paths/resources, expected output, success command,
time/usage/retry ceilings, dependency and integration order. Read-only lanes can
share a checkout; mutating lanes get separate branches/worktrees and resources.
Reconcile progress against that contract, not token use or apparent activity.
Use the council procedure in the pr-reviewer references for complex plan/audit work.

When evidence invalidates a premise, pause affected work, revise the task graph and
revalidate changed acceptance with its owner. Do not keep dispatching descendants
of a decision that is no longer true. Record abandoned effort and the reason.

## Test strategy that proves the claim

For each accepted requirement keep: test/journey, fixture provenance, threshold,
candidate identity, result and remaining gap. Distinguish executed behaviour from
parse-only and source-scan checks. Source scans can check structure; they do not
prove user behaviour. A unit suite does not prove a reachable journey.

- Unit/contract tests cover boundaries, schema refusal and deterministic logic.
- Integration tests cover real seams, migrations, retries and partial failure.
- Packaged artifact journeys cover installation/start, core use and recovery.
- NFR tests record thresholds and environment for performance, accessibility,
  reliability, cost and security; separate gated, merely measured and unmeasured.
- Regression fixes reproduce the failure on the base before passing on the fix.
- Risk-weighted mutation tests demonstrate gates refuse representative defects.
- Teardown proves owned browser/server/process resources are released after failure.

Report passed, failed, skipped with reasons, duration and real exit status together.
Missing optional infrastructure is inconclusive for that lane; required missing
evidence blocks promotion. A skipped requirement cannot become covered.

Use explicit PASS, FAIL, NOT_APPLICABLE and INCOMPLETE states. NOT_APPLICABLE needs
the scope-classifier evidence and reason; it is not a generic success substitute
for skipped execution. Temporary advisory exceptions name owner, scope, expiry or
review trigger, required promotion evidence and release impact.

Diff the canonical convergence command against CI and hooks. If a hosted lane is
retired, replace or explicitly block every check that delegated to it. Record what
still requires a trusted environment and who provides that evidence. Advisory lanes
must be labelled advisory in both receipts and maturity claims.

## Maturity and release promotion

Milestone names are project choices. Define exits before using labels such as MVP,
beta or production. Version `0.x`, issue closure and deployment do not prove an exit.
Track dimensions separately: functionality, usability/accessibility, test evidence,
security/privacy, operations/recovery, distribution and commercial validation.

| Horizon | Minimum outcome evidence to tailor in the profile |
| --- | --- |
| Prototype | Feasibility demonstrated on named fixtures; limitations explicit |
| MVP | Intended user completes core journey; critical requirements tested; failure and recovery honest |
| Beta / UAT | Installable immutable artifact, representative users/environments, feedback ownership, rollback and sustained observation |
| Production | Accepted service/security objectives, operational owner, proven recovery, approved release controls and live observation |
| Production iteration X | Compare candidate to prior baseline, prove regression/upgrade/rollback, evaluate outcome change and new risks |

Each dimension has evidence, threshold, current state, owner and next action. Never
average away a blocking security or recovery gap. A commercial hypothesis may
remain unvalidated even when engineering readiness passes.

Keep three gates distinct: candidate merge readiness, artifact release readiness,
and environment promotion readiness. Record base and candidate (or reviewed tree),
test receipt, reviewer identity/lane and verdict, immutable artifact digest, source
commit/tag, configuration, migration state, environment, approver, health probes,
observation window and rollback target. Any candidate change requires revalidation
and review of the changed candidate; a prior PASS never carries silently.

Build from the approved commit through the project's authorised build path. Promote
the same artifact digest from UAT to live; if platform builds differ, record each
artifact's source/provenance and test the actual promoted artifact. Tags identify
source; they are not approvals, test receipts or deployments. Never move a published
tag to conceal a bad release. Tag rules and environment controls require their own
inspection; main branch protection alone does not protect release tags.

## Value and learning

Measure accepted outcomes per elapsed time and total known cost, including review,
retries, rework and integration. Track first-pass acceptance, escaped defects,
abandoned work, conflicts, lead time and manual operator effort. Unknown usage stays
unknown. No model comparison is meaningful unless tasks and quality floors match.

Log opportunities with user segment, problem, observed source/date, hypothesis,
benefit and cost range, owner, next falsifiable experiment, success/stop threshold
and linked objective. Marketing claims must link to public-safe evidence and name
their limits. Delivery speed or cost savings from one project are hypotheses for
another until measured. Review the opportunity queue when planning; publishing or
contacting customers remains a separately authorised action.

## Audit output and completion

Return prioritised findings with source/command evidence, impact, smallest remedy,
owner and acceptance check. Reconcile docs and issue state within granted authority;
otherwise prepare exact issue drafts and mark them unfiled. The final report names
what is proven, pending, deliberately out of scope and awaiting a delivery decision.
An audit is complete when its evidence and actions are usable; it does not imply
the audited product or every proposed automation is production-ready.
