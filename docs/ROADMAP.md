# Roadmap

**As of:** 2026-09-26 · **Owner:** jpantsjoha · **Plan:** DPS-001 / HFE-001

Ordered outcomes, not duplicated live issue state. This is a local planning record;
unfiled items below are not GitHub issues or accepted release commitments.

| Order | Outcome | Exit gate | State |
| --- | --- | --- | --- |
| Now — HFE-001 | Feed measured adopter experience back into the plugin | Initial four-source audit plus four-project follow-up, usable procedures, review-gate regressions, convergence and independent review | Feature branch; see STATUS |
| Now / Next — DPS-TRACE | Planning records reconcile deterministically | DDG-001 structural gate; next semantic reconciliation and executed-test coverage, then opt-in live freshness/completeness | Structural slice on branch; remaining work unfiled |
| Next — DPS-REVIEW | Review evidence can govern a merge | Candidate/base binding, non-author identity boundary, stale/conditional/error rejection and trusted enforcement tests | Proposed; authority/trust design unresolved |
| Next — DPS-PROMOTE | MVP/UAT/live transitions prove the artifact and outcome | Project-owned maturity exits, immutable digest, upgrade/rollback and observation receipts | Proposed; per-project adoption required |
| Later — DPS-VALUE | Priorities learn from delivery and customer evidence | Opportunity experiments and accepted-outcome economics reconcile to objectives | Proposed; no commercial validation asserted |

## Issue-ready follow-up contracts — not filed

| ID / owner | Scope and DoD | Validation / dependency |
| --- | --- | --- |
| DPS-TRACE / planning maintainer | DDG-001 implements structural IDs/states/parents/dependencies/supersession/local links. Next add semantic current-fact conflicts, requirement→executed-test coverage and opt-in live reconciliation | Structural refusal fixtures run locally. Remaining fixtures must reject stale facts, absent execution and incomplete paginated API reads; no claim of full semantic reconciliation |
| DPS-REVIEW / security and delivery maintainer | Specify trusted receipt producer, author/reviewer distinction, exact candidate, verdict semantics and bypass policy; then enforce through authorised hosted check or declared local mode | Reject replay, changed base/head/tree, malformed/failed lane, wrong identity and open conditions. Local file forgery must not pass as authenticated review |
| DPS-PROMOTE / release owner | Record release ADR, tag rules, build provenance, UAT/live environment contracts, recovery and observation. Reconcile CI retirement/migration | Release rehearsal proves source→artifact→environment identity and rollback. Requires separately approved remote/environment changes |
| DPS-VALUE / product owner | Link customer/commercial hypotheses to experiment, measure, stop threshold, evidence and roadmap decision; measure engineering lead time/rework/known cost | One real completed experiment and one delivery outcome measured with provenance. No invented savings, usage or revenue |
| ADOPT-DRIFT / each adopter owner | Repair audited current-fact and retired-CI delegation drift in individual reviewed branches | Each project's canonical gate and independent review, then regenerate current docs. This feedback branch does not mutate adopters |
| DPS-CONTEXT / context integration maintainer | Reconcile Graft ADR status, effective package resolution, active hook paths and worktree-specific cache identity; harden freshness before claiming coherence | Fixtures cover deletion/rename, old timestamps, failed scans/builds, concurrent readers/writers, missing local package and fallback version. Verify pinned query refresh before adding overlapping hooks; no automatic install |

Existing insight issues [#23](https://github.com/jpantsjoha/ai-native-developer-experience/issues/23)
and [#24](https://github.com/jpantsjoha/ai-native-developer-experience/issues/24)
should be reconciled with this queue before creating duplicates. Neither had a
milestone in the 26 September API snapshot. External tracker updates remain pending.

## Follow-up optimisation slices

The [additional project review](OPTIMISATION-REVIEW-2026-09.md) supplies source evidence
and negative acceptance cases. These refine the contracts above; they are unfiled,
not a parallel issue system. Suggested order, subject to measured value:

1. DPS-REVIEW: review-inclusive WIP and persistent attempt budgets; DPS-CONTEXT and
   DPS-REVIEW: non-provisioning execution-context checks, including dependency identity.
2. DPS-TRACE / ADOPT-DRIFT: canonical policy/gate conflicts and ADR reconciliation,
   then requirement→test→executed-lane coverage with explicit evidence levels.
3. DPS-REVIEW: path-derived specialist requirements and optional per-rule/test-ID debt
   ratchets; baseline updates cannot trade one defect for another.
4. DPS-PROMOTE: persisted completion receipts and profile-specific independent recovery.
   DPS-VALUE: evaluate these changes against matched delivery tasks before scaling.

Portable guidance is included in this branch; these new mechanical controls remain
unimplemented here. No additional always-loaded skill or permanent council lane is
proposed without a measured gap and an experiment/removal rule.

## Deferred cost and ownership

DPS-VALUE uses the [executive rubric](EXECUTIVE-SCORECARD.md) across strategy,
ownership, technology, security, operations, experience and wider value. First collect
accepted-outcome yield, effort per accepted outcome and repeat use with quality/authority
guardrails. No savings target or market validation is assumed.

Trusted merge enforcement is deferred until its identity/authority design is agreed;
this leaves a known procedural boundary, owned by the delivery maintainer. Automated
promotion is deferred until a release owner and target are declared; it blocks claims
of mechanically enforced UAT/live readiness. Evidence is the September audit above.
This ordering is revisable by the Product Owner; a prior roadmap never overrides a
new explicit instruction within the operator's authority.
