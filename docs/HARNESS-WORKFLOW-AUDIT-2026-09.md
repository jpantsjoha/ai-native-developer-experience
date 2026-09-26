# Workflow audit — 26 September 2026

## Finding

The projects have a coherent delivery philosophy and substantial executable gates.
The main weakness is transition reconciliation: declared controls, the command that
actually runs, remote enforcement and current maturity can disagree. More skills or
more expensive models alone will not close that gap. Carry candidate identity and
evidence through each transition, then reconcile the records that describe it.

Scope is HFE-001, building on accepted DPS-001. These are source/platform findings,
not certification of the applications' runtime or commercial outcomes. No adopter
was changed, deployed or subjected to a full product test suite in this audit.

## Sources and method

| Repository | Inspected local HEAD | Scope caveat |
| --- | --- | --- |
| mac-control | `711286d71fa3f9725fdef6f2b2a80089057e9f9b` | Clean at read; executable audit and current delivery records inspected |
| ChromeExt-FeedEval | `977f6c53a21058dd6be6a5e33fac34232bd8f973` | Three existing modified source/test files left untouched; no runtime claims from them |
| gcp-exam-prep (`cert-exam-prep` remote) | `16cfb07133ef631f256b36354380c5bf3900d59f` | Clean; operating-profile validator executed |
| ai-native-developer-experience | `164946c3337e630256ff7a1f258e2c18b61aaac2` | Original checkout has untracked duplicate-looking files; excluded from isolated branch |

Two independent read-only audit lanes examined the adopter projects; the parent
examined mac-control and the plugin, and re-read key findings and remote protection.
Commands included `git status --short`, `git rev-parse HEAD`, `gh api
repos/OWNER/REPO/branches/main/protection`, bounded `gh issue list`, `gh run list`
and PR review metadata. These remote observations are dated snapshots, not standing
guarantees; no tokens or personal account data are retained.

## Comparison

| Project | Valuable implemented pattern | Enforcement / observation limit |
| --- | --- | --- |
| mac-control | Requirement → milestone → issue audit; runbook/CLI reconciliation; explicit null/stale signals; multidimensional readiness and exact-tree receipts | Main requires zero approvals and no status checks, with admin enforcement on. `golden-thread.py:44–56` warns and continues when GitHub cannot be read: offline success is not live tracker reconciliation |
| FeedEval | Canonical Make/npm commands; exact-head Copilot checks; reasoned local review; tagged package/browser checks; built-versus-proven maturity | Main requires CI/DX/PR gate, zero approvals, admins not enforced. Hosted gate explicitly excludes reasoned delivery review. Browser/keyed lanes are advisory |
| Exam-prep | Ten-stage traceability; user journey versus API distinction; negative controls; isolated test resources; revision/digest and rollback runbook | Main has no required checks/reviews or admin enforcement. Local hook delegates portal/typecheck to CI after Actions retirement. Profile validation passes despite stale facts |
| Join the Team | Portable 22-skill package; adopted manual/profile templates; orientation hook; approved planning-control-plane design | Baseline `make check` passes 79 tests. Main requires Markdown Lint and Operating Model Contract, but not Agent Plugins Conformance; zero approving reviews. Generic planning reconciliation remains partly specified |

## Prioritised findings and dispositions

| ID | Priority | Evidence and impact | Disposition / acceptance |
| --- | --- | --- | --- |
| AUD-1 | P1 | Plugin `scripts/review-gate.sh` captures `review()` in command substitution; VERDICT does not propagate to the caller under `set -u`. It also discards lane exit status, truncates diffs and uses permissive result branches | Fix in HFE-5 with offline stub regressions; successful PASS must work and every failed/incomplete lane must refuse |
| AUD-2 | P1 | Exam `.githooks/pre-push:183–205` says CI owns PR, portal and type checks; ADR-0076 retires Actions. Main API confirms absent required checks | Proposed follow-up: declare gate execution mode, remove dead delegation, prove all required checks execute on actual candidate; local controls remain bypassable |
| AUD-3 | P1 | FeedEval `.github/workflows/pr-review-gate.yml:292–299` explicitly excludes local reasoned review. PR #429 checks are green; inspected reviews/comments do not contain completed reasoned review | Proposed receipt/enforcement work. Absence in inspected metadata does not prove review never happened |
| AUD-4 | P1 | Exam PR #426 records integration/edit after review and later convergence, with no renewed review in inspected evidence | Require renewed exact-candidate or explicitly scoped delta review; do not infer tests restore a stale review |
| AUD-5 | P1 | FeedEval `planning/STATUS.md:4146` says no tagged package while its header and GitHub v0.4.8 release show one; `planning/ROADMAP.md:7` still names v0.4.7. Exam profile names laptop/LAN and no production while STATUS names public v0.9.0 | Current-fact ledger and semantic reconciliation backlog; structural validators alone do not close this |
| AUD-6 | P1 | FeedEval `release-provenance.yml:42–45` checks event SHA/tag agreement, not independently reviewed SHA, immutability or artifact digest. No rulesets returned in audit | Promotion contract specifies source/review/artifact/environment identities; actual hosted enforcement remains follow-up |
| AUD-7 | P2 | Exam CLAUDE routing chooses agy first in one section and Codex first in another; profile has older tiers. Existing issue #408 tracks routing drift | Portable capability/effort procedure, one project-owned registry, requested/resolved identity and failure semantics |
| AUD-8 | P2 | Plugin lacks current STATUS/ROADMAP despite DPS-001 documenting that need. Open issues #23/#24 have no milestone | This branch adds honest local records and unfiled follow-up contracts. Live milestone/issue mutation is pending authority |
| AUD-9 | P2 | FeedEval commercial strategy and exam funnel/KPIs exist, but current opportunity-to-experiment reconciliation is not demonstrated; exam commercial plan references rejected ADR-0055 | Opportunity register proposal with evidence, experiment, owner and stop/success metric; no revenue or marketing outcome asserted |

Source links for remote findings:
[FeedEval #429](https://github.com/jpantsjoha/ChromeExt-FeedEval/pull/429),
[FeedEval failing governance preflight](https://github.com/jpantsjoha/ChromeExt-FeedEval/actions/runs/34248971133),
[FeedEval v0.4.8](https://github.com/jpantsjoha/ChromeExt-FeedEval/releases/tag/v0.4.8),
[exam #426](https://github.com/jpantsjoha/cert-exam-prep/pull/426),
[exam #408](https://github.com/jpantsjoha/cert-exam-prep/issues/408),
[harness #23](https://github.com/jpantsjoha/ai-native-developer-experience/issues/23),
[harness #24](https://github.com/jpantsjoha/ai-native-developer-experience/issues/24).

## What to preserve and generalise

1. **Golden thread:** mac-control's executable ID/runbook checks, exam's ask-to-live
   chain and FeedEval's milestone journeys. Generalise their contracts, not their
   project-specific regexes. A coverage set check does not prove unique milestone
   ownership or user acceptance; name the exact claim each audit proves.
2. **Planning:** accepted objectives, interfaces and independently verifiable task
   contracts before parallel mutation. Keep the orchestrator's context about decisions
   and convergence; keep worker contexts small and task-specific.
3. **Council:** independent challenge at plan and audit boundaries as well as PRs.
   Resolve actual available models, qualify findings and retain disagreement. Gemini's
   plan critique here contained useful requirements and inaccurate code diagnoses;
   model diversity is not a substitute for re-derivation.
   The final `sol-high` review then identified a missed lifecycle case: async
   pre-commit review became invalid after a normal commit advanced HEAD. A new
   regression reproduced it; advisory workers must review their immutable saved
   snapshot, while later merge decisions independently verify current identity.
4. **Tests:** executable journeys, planted negative controls, packaged-byte tests,
   honest skipped/incomplete outcomes and resource teardown. Distinguish evidence
   from unit, browser, synthetic and live environments.
5. **Maturity:** retain dimensional built/proven distinctions. Separate availability,
   operational readiness, user acceptance and commercial validation. No version or
   averaged percentage can waive a blocking dimension.
6. **Release:** review source, produce provenance, promote known artifacts, observe
   the target and rehearse rollback. Tag creation alone closes none of those gates.

The portable procedure is maintained in
[workflow-audit](../skills/delivery-orchestrator/references/workflow-audit.md),
with model routing and review failure semantics in
[council](../skills/pr-reviewer/references/council.md).

## Reflection on performance and value

Use deterministic checks before expensive reasoning. Use higher effort for unresolved
interfaces, risk logic and competing explanations; use smaller proven-capable workers
for bounded implementation. One independent reviewer is the economical default;
multiple lenses earn their cost on high consequence or unresolved disagreement.

Measure total time and known cost to an accepted outcome, including retries, review
and rework. No cross-project speedup, savings or model ranking was measured here.
The user's Opus 5.5 preference is not claimed as a verified runtime capability.
The local council registry listed `agy` as Gemini 3.8 Flash high and `sol-high` as
GPT-5.6-sol high; registry output is configuration evidence, not successful execution
for every lane. The Gemini plan-review invocation did return a substantive response.

## Completion boundary

This feedback slice produces an audited plan, portable skill improvements, a tested
local helper correction and a reviewable feature branch. It does not complete all
DPS-001 automation, retrofit adopter repos, change remote protection, publish a
plugin version or certify UAT/live readiness. Follow-up contracts live in ROADMAP.
