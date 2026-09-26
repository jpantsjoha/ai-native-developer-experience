# Roadmap

**As of:** 2026-09-26 · **Owner:** jpantsjoha · **Plan:** DPS-001 / HFE-001

Ordered outcomes, not duplicated live issue state. This is a local planning record;
unfiled items below are not GitHub issues or accepted release commitments.

| Order | Outcome | Exit gate | State |
| --- | --- | --- | --- |
| Now — HFE-001 | Feed measured adopter experience back into the plugin | Four-source audit, usable procedures, review-gate regressions, convergence and independent review | Feature branch; see STATUS |
| Next — DPS-TRACE | Planning records reconcile deterministically | Offline invalid-ID/state/link fixtures fail; live reconciliation reports freshness, completeness and API failures separately | Approved DPS-001 direction; detailed slice unfiled |
| Next — DPS-REVIEW | Review evidence can govern a merge | Candidate/base binding, non-author identity boundary, stale/conditional/error rejection and trusted enforcement tests | Proposed; authority/trust design unresolved |
| Next — DPS-PROMOTE | MVP/UAT/live transitions prove the artifact and outcome | Project-owned maturity exits, immutable digest, upgrade/rollback and observation receipts | Proposed; per-project adoption required |
| Later — DPS-VALUE | Priorities learn from delivery and customer evidence | Opportunity experiments and accepted-outcome economics reconcile to objectives | Proposed; no commercial validation asserted |

## Issue-ready follow-up contracts — not filed

| ID / owner | Scope and DoD | Validation / dependency |
| --- | --- | --- |
| DPS-TRACE / planning maintainer | Implement remaining DPS-001 FR-8: IDs, lifecycle states, links, rejected/superseded ADR references and current-fact conflicts. Keep unknowns explicit | Fixture suite fails missing documents, broken links, stale state and incomplete paginated API reads. Depends on agreed schema; bounded optional live adapter |
| DPS-REVIEW / security and delivery maintainer | Specify trusted receipt producer, author/reviewer distinction, exact candidate, verdict semantics and bypass policy; then enforce through authorised hosted check or declared local mode | Reject replay, changed base/head/tree, malformed/failed lane, wrong identity and open conditions. Local file forgery must not pass as authenticated review |
| DPS-PROMOTE / release owner | Record release ADR, tag rules, build provenance, UAT/live environment contracts, recovery and observation. Reconcile CI retirement/migration | Release rehearsal proves source→artifact→environment identity and rollback. Requires separately approved remote/environment changes |
| DPS-VALUE / product owner | Link customer/commercial hypotheses to experiment, measure, stop threshold, evidence and roadmap decision; measure engineering lead time/rework/known cost | One real completed experiment and one delivery outcome measured with provenance. No invented savings, usage or revenue |
| ADOPT-DRIFT / each adopter owner | Repair audited current-fact and retired-CI delegation drift in individual reviewed branches | Each project's canonical gate and independent review, then regenerate current docs. This feedback branch does not mutate adopters |
| DPS-CONTEXT / context integration maintainer | Reconcile Graft ADR status, effective package resolution, active hook paths and worktree-specific cache identity; harden freshness before claiming coherence | Fixtures cover deletion/rename, old timestamps, failed scans/builds, concurrent readers/writers, missing local package and fallback version. Verify pinned query refresh before adding overlapping hooks; no automatic install |

Existing insight issues [#23](https://github.com/jpantsjoha/ai-native-developer-experience/issues/23)
and [#24](https://github.com/jpantsjoha/ai-native-developer-experience/issues/24)
should be reconciled with this queue before creating duplicates. Neither had a
milestone in the 26 September API snapshot. External tracker updates remain pending.

## Deferred cost and ownership

Trusted merge enforcement is deferred until its identity/authority design is agreed;
this leaves a known procedural boundary, owned by the delivery maintainer. Automated
promotion is deferred until a release owner and target are declared; it blocks claims
of mechanically enforced UAT/live readiness. Evidence is the September audit above.
This ordering is revisable by the Product Owner; a prior roadmap never overrides a
new explicit instruction within the operator's authority.
