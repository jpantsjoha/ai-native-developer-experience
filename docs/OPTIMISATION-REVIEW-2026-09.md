# Join the Team optimisation review

**Date:** 2026-09-26 · **Scope:** HFE-001 follow-up · **Baseline:** `68ad5a9`

Join the Team has a strong operating contract, but “most optimal” is not evidenced.
The next return should come from making existing controls executable, reducing review
queues and proving that checks exercise the intended candidate. Adding more skills
or routinely convening more models would not establish better value.

This extends the [original audit](HARNESS-WORKFLOW-AUDIT-2026-09.md). Four additional
unique projects were selected using recent commits and instruction/status-file updates
under `~/local`; this is a bounded sample, not an exhaustive folder audit. The two
trading-project audits ran as independent read-only lanes. No trading records, private
manuscripts, credentials or live product services were used. Findings are engineering
workflow evidence, not assessments of those products' financial or commercial merit.

## Source provenance and confidence

Paths below are relative to each named checkout under `~/local`. Line numbers are
navigation aids; the full SHA and dirty caveat identify the inspected source.

| Source | HEAD | Working-tree caveat / execution |
| --- | --- | --- |
| PersonalTrader | `bd6064a562ba38e6590964b3803464ede44d90e6` | Pre-existing modified planning documents, including `Planning/README.md`; its WIP finding describes working-tree policy. Other product files were dirty and untouched. No tests executed |
| sentineltrader | `0140d6105c6e59cee6ea715c5134870154234f8f` | Only an untracked reflection was reported; left unread. Gate and fixture source inspected, not executed |
| browser-harness | `afbcc381b963040c19627d788e40c7e7663171ee` | Clean. Source and fixture inspection; no browser/daemon started or live health probe run |
| ghostwriter-app (Riter) | `07c2bc9e8ce4aaa485631563f16f9d7d928da9c3` | Clean. `bash scripts/council-review.SELFTEST.sh` passed **56/56**, exit 0, using a stub council and disposable repository; no provider calls |

Source plus fixture inspection is evidence of an implemented mechanism, not a current
successful check or effective enforcement. Only the bounded Riter self-test above was
executed in an adopter. It proves those refusal/loop fixtures, not model availability,
remote protection or production readiness. Join the Team validation is retained in
the adjacent audit-evidence directory and does not substitute for adopter validation.

## Priorities and smallest useful changes

Effort/value below are planning judgements, not measured savings. Extend the existing
[roadmap contracts](ROADMAP.md), avoiding a second backlog or another universal skill.

| Order / existing owner | Improvement and evidence | Smallest adoption and acceptance |
| --- | --- | --- |
| **1 · DPS-REVIEW / delivery maintainer** — small guidance, medium automation | Bound review loops and keep review/integration inside WIP. Riter `scripts/council-review.sh:123` counts attempts across commits, changes lane and halts; its self-test passed. PersonalTrader `Planning/README.md:50` keeps review slots occupied and distinguishes Ready but queued | Persist attempts by stable work-item/lineage, with configurable ceiling, replan trigger and audited reset. Do not reset on SHA change or free capacity when authoring ends. Fixtures: changed SHA still hits ceiling; full WIP leaves ready work queued; reset preserves history. Source branch-name-only ledgers and file-name similarity are useful signals, not sufficient identity or proof of the same defect |
| **2 · DPS-REVIEW + DPS-CONTEXT / integration maintainers** — medium effort, high expected value | Verify actual execution context before expensive dispatch. Riter `CLAUDE.md:480` describes tests resolving workspace dependencies from the parent checkout; `Makefile:781` now supplies locked `npm ci`. Browser-harness `src/browser_harness/admin.py:1459` supplies versioned strict doctor JSON for an existing daemon; fixtures are in `tests/unit/test_admin.py:170` | A non-provisioning preflight reports checkout/tree, resolved imports/tool versions, requested versus effective model, exact resource identity and required missing capabilities. Fixtures: parent-checkout import refuses, missing explicitly selected interpreter refuses, absent daemon does not spawn a replacement. Repair/install remains a separate authorised action. Do not copy Riter's older instruction to discard lockfile changes |
| **3 · DPS-TRACE / planning maintainer** — medium effort, high expected value | Reconcile current policy and executable acceptance links. Sentinel `delivery/scripts/verify_proof_spine.py` maps invariant→test→gate; `verify_adrs.py` checks decision metadata; `ci_local.sh:451,568` wires them. Riter's profile still names `make check` while its Makefile distinguishes stronger pre-merge/review gates | Start with adapter/profile/gate conflicts and ADR links/status/supersession, then stable requirement→test IDs. Separately report mapping validity and actual execution. Fixtures: renamed/deleted test, disabled/comment-only lane, unresolved adapter precedence and newly stale ADR fail the relevant claim. A source match must not become execution proof |
| **4 · DPS-REVIEW / security and delivery maintainer** — medium effort | Dispatch specialists from changed surfaces and ratchet existing debt. Sentinel `delivery/scripts/required_reviews.py:136,258,287,317` classifies paths, binds scoped digests, handles renames and prioritises blocking verdicts. `quality_ratchet.py:22` compares lint/type rules and failing test IDs | Project-owned capability registry plus a reviews-owed report; retain assembled-candidate review. Optional brownfield debt baseline is reviewed and environment-bound. Fixtures: rename out of protected path still triggers; changing classifier triggers review; missing digest/BLOCK refuses; equal-total defect substitution and crashed tool refuse. A self-authored trailer does not authenticate a reviewer |
| **5 · DPS-PROMOTE / release owner** — small guidance, project-specific implementation | Verify persisted outcomes, not hook invocation. PersonalTrader `.claude/hooks/funnel_flag.sh:17` clears a pending flag on skill invocation, without verifying a saved result. Its recovery epic correctly keeps independent off-machine/key recovery pending despite local recovery tests | Completion hooks need work-item/session-bound persistence receipts. Failure to write or wrong-session receipt stays pending. Recovery profiles distinguish local round-trip, independent environment, recovered identity/key, RPO/RTO and logical reconciliation. A local same-key restore cannot close an independent recovery criterion |
| **6 · DPS-VALUE / product and harness maintainer** — small experiment, medium evaluation work | Admit harness complexity only for a measured gap. PersonalTrader `Planning/milestones/M4-triggered-experiments.md:19` requires baseline, cost ceiling, simpler alternative and kill rule; currently policy, not a proven controller | Trial one change against comparable tasks at the same quality floor. Track accepted-outcome lead time, review queue, retries/rework, escaped defects, known cost and operator effort. Add offline failure scenarios before broad adoption; record runtime/version for opt-in agent evaluations. Remove or park controls with no evidenced incremental value |

## Further distinctions worth preserving

- **Shared resources need ownership beyond worktrees.** Browser-harness `SKILL.md:63`
  serialises operations on a daemon's mutable current tab. Parallel code lanes do not
  make simultaneous tab switches safe. Give the resource one lane/lease; reclaim only
  owned resources. Its recorder (`src/browser_harness/recorder.py:304`) preserves
  `frame_error` instead of silently implying a complete recording. Missing required
  proof stays incomplete even when the main action succeeded.
- **Mode and environment belong in receipts.** Sentinel's `ci_local.sh:39,71,119`
  distinguishes fast/full, refuses dirty HEAD and resolves explicit interpreter choice.
  Improve the pattern with pre/post immutable candidate identity and unique run IDs;
  porcelain cleanliness alone misses a clean checkout switch. Required skipped lanes
  cannot satisfy full release acceptance.
- **Do not inherit weaknesses with the pattern.** Sentinel's proof-spine uses text
  matching and can accept full-mode wiring in a fast run. Its ratchet updater
  (`quality_ratchet.py:662`) checks aggregate increases, leaving equal-total replacement
  possible. Baseline updates must preserve per-rule/set constraints too. Local gates
  and override variables remain procedural controls unless a trusted required path
  enforces them.
- **Canonical policy is still drifting.** Sentinel `AGENTS.md:3` delegates precedence
  to GEMINI while newer rules appear in CLAUDE. Riter's profile was last verified
  16 August and its command table lags the newer merge ladder. Preserve explicit user
  authority and report affected conflicts; do not resolve them by taking whichever
  Markdown file has the newest timestamp. Adopter remediation belongs in ADOPT-DRIFT.
- **Graft remains advised as an optional, evidenced context accelerator.** FeedEval's
  root-pinned adoption and Sentinel's personal/global-resolved loaders (`.gitignore:150`)
  are different installation models. A portable preflight must disclose effective
  package, hook and cache identity. No fresh query or incremental benefit was measured
  here; the [freshness limitations](CONTEXT-GRAPH-FRESHNESS.md) still apply. Avoid
  overlapping refresh hooks and verify important claims against source.
- **Keep domain and workflow choices local.** Do not copy trading thresholds, fixed
  WIP numbers, brand vocabulary, model aliases, branch layout or PersonalTrader's
  preference for local planning over GitHub Issues. The plugin should identify the
  chosen task system's owner, not force two competing sources of truth.

## Measuring whether this improves delivery

Use the next representative delivery tasks as a baseline, recording complexity/risk,
acceptance, environment and total work through integration. Compare a bounded change
on matched tasks; include failures and abandoned attempts. Small samples support a
local decision, not a universal model ranking or a marketing savings claim.

Begin with review queue/attempt accounting and execution-context checks. Then implement
the existing reconciliation and trusted review contracts. Add new council lanes only
when a specified expertise gap, disagreement or consequence warrants them; resolve
the operator's requested model at runtime and record the actual lane and effort.
No evidence here establishes that a permanently larger council is better.

Exercise the plugin itself against reproducible scenarios: stale candidate, unavailable
reviewer, incorrect worktree dependency, misleading PASS text, hook write failure,
partial evidence, shared-resource collision and retired CI delegation. Deterministic
fixtures validate mechanics; separately evaluated runtime tasks validate whether an
agent follows the procedure. Neither schema conformance nor prose review proves both.

## This branch's change and adversarial check

This follow-up adds the comparison and concise guidance to existing workflow/council
references and the bootstrap template. It does not implement the proposed doctor,
WIP validator, specialist classifier, ratchet or semantic reconciliation engine.
Roadmap contracts remain unfiled. No adopter, installed cache, remote policy, tag or
release is changed.

How would I break this? Treat source-inspected fixtures as executed; mistake new prose
for enforcement; import a local project exception as universal authority; or add so
much ceremony that accepted delivery slows down. The evidence table, negative acceptance
cases, project-owned settings and measured admission rule address those failure modes.
The remaining implementation and outcome evidence stays explicit in the roadmap.
