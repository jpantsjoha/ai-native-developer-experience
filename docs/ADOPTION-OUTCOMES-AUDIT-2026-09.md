# Join the Team: adoption and delivery outcomes audit

**Date:** 2026-09-26 · **Owner:** JP · **Parent work:** HFE-001
**Plugin branch baseline:** `71326822157786e0b6c77ee4684a2965ba151a5c`
**Scope:** five owner-operated projects; read-only source/Git/GitHub inspection,
public listing checks and one safe operating-model validation. No adopter changes,
product-suite reruns, authenticated product journeys, cloud operations or paid council calls.

## Judgement and method

Join the Team has demonstrated successful internal adoption and useful contributions
to real delivery. Four repositories explicitly name or embed the shared harness;
Proofly demonstrates compatible adapted practice and operator-attested adoption.
Independent reviews have changed delivered work. This is stronger evidence than
installed skills or well-written policy alone. It does not establish that the package
caused all delivery success, that every control executed, or that the current design
is optimal. These are selected successful projects under one operator, not an
independent team cohort or a controlled comparison.

Primary success means consistent value outcomes, pace, deterministic quality,
independent review and coherent requirements/architecture/acceptance. Commercial and
marketing measures are optional. A public listing is delivery evidence, not revenue
or proof that every customer journey works.

Evidence labels: **observed** = inspected source, Git/API state or public response;
**recorded** = historical test/review/deployment receipt, not rerun; **reported** = JP's
experience. Model names in historical records are labels, not newly verified provider
availability or authenticated reviewer identity.

Adoption scale, distinct from the [capability rubric](EXECUTIVE-SCORECARD.md):
0 confirmed absent; 1 declared; 2 executable adaptation; 3 evidenced delivery use;
4 repeated measured benefit with operating burden and a comparable baseline.
Unknown lineage stays unknown; it does not become absence or a fabricated score.

## Portfolio assessment

| Project / inspected HEAD | Adoption and adaptation | Delivery evidence | Assessment and remaining limit |
| --- | --- | --- | --- |
| Cert Prep / `16cfb07133ef631f256b36354380c5bf3900d59f` | Profile pins Join the Team v0.1.7 assets/manual 2.1.0; active routing, isolated exact-commit pre-push convergence, council and candidate-bound UAT | Remote v0.9.0 release; recorded production revision, 30/30 live UAT and observation; public endpoint returned HTTP 200 | **3/4**. Explicit lineage and real delivery. Signed-in journeys not independently checked; release records acknowledge cold-start target missed |
| FeedEval / `977f6c53a21058dd6be6a5e33fac34232bd8f973` | DEVELOPER_EXPERIENCE explicitly adopts canonical harness; global skill references, adapted router, Make targets, hooks and SHA receipts | Merged v0.4.4 delivery trace; public Chrome listing now shows **0.4.8**, updated 3 September | **3/4**. Marketplace outcome confirmed; current store artifact was not downloaded or digest-matched. Local submission record is stale |
| SentinelTrader / `0140d6105c6e59cee6ea715c5134870154234f8f` | Thin local release/review adapters explicitly compose global skills; diff-bound review and CI receipts, regression and debt gates | Merged login fix, named deployed revisions and recurring SRE receipt; JP reports successful UAT | **3/4**. Useful review intervention and deployment evidenced; inspected older UAT records leave human sign-in/demo smoke incomplete |
| Riter / Ghostwriter / `07c2bc9e8ce4aaa485631563f16f9d7d928da9c3` | Shared manual hash matches 2.1.0 asset; product-owner/journey/golden-thread adaptations; convergence and council targets | Merged feedback/accessibility fix, recorded desktop/phone synthetic journeys; JP reports UAT | **3/4**. Engineering use proven; human/connected UAT issues remain open and referenced receipt paths need reconciliation |
| Proofly Shopify / `4dbfb77a588522343fa929aa32a043184031e4f2` | Local DoD, hooks, failure-injection self-tests, council, candidate/freshness release guard, pinned Graft trial | Public Shopify listing; merged tenant-isolation/credit fixes, recorded staging→production pipelines and image/revision | **3/4 for observed delivery practice; package attribution unverified**. No explicit package lineage found in inspected instructions/skills/planning; global installation and JP's account support association |

Cert Prep, Riter and Proofly checkouts were clean. FeedEval had three modified source/test
files; Sentinel had an untracked reflection. These were left untouched. Findings about
tracked history are bound to the heads above; no dirty code was claimed as released.

## Inspectable delivery traces

### Cert Prep: accepted exam content to production

[Issue #396](https://github.com/jpantsjoha/cert-exam-prep/issues/396), REQ-032/REQ-X1–X6,
defines CCAR-P acceptance. [PR #405](https://github.com/jpantsjoha/cert-exam-prep/pull/405)
records review findings reducing 35→20→5, including incorrect answer keys. Its later
merge comment resolves the stale PR description: authorised fourth review, recorded
Kimi PASS and convergence at `61a0c666`; 137 original publishable items. Merge `60cb78a8`
is not an ancestor of the release: the pack tranche was reapplied at `f0b9e78e` on
the production base, deliberately excluding unrelated #388. Git inspection confirms
the entire `exams/ccar-p` tree at that merge and at v0.9.0 is identical
(`03f33eec70b5259a76c79fcd33818f4ae4b84ac9`); `f0b9e78e` is a release ancestor.
Production receipts connect this separate delivery path to the
[v0.9.0 release](https://github.com/jpantsjoha/cert-exam-prep/releases/tag/v0.9.0).
The retained release evidence records live checks and observation. Current main is
ahead of the deployed release; source HEAD is not the production identity.

### FeedEval: observed capture failure to store release

[Issue #363](https://github.com/jpantsjoha/ChromeExt-FeedEval/issues/363), ADR-011 CTX-4,
connects operator UAT to transcript activity resetting the silence clock. Tests in
`tests/context-model.test.mjs` cover quiet audio with active transcription, wiring and
fire-once behaviour. Review records demanded wiring-test and receipt corrections.
[PR #367](https://github.com/jpantsjoha/ChromeExt-FeedEval/pull/367), merged as
`2024e3e34ed79874c34f7d047d329852723c193b`, records validation and 1,395 tests.
`planning/STORE-SUBMISSION.md` records v0.4.4 and package SHA
`a80765e4376f37d257630e8472753dd0b0c4b67babceb613affd46414543756a`.
The [public listing](https://chromewebstore.google.com/detail/donttrustverify/fpdopmocklkjnfbkjkpojpkbmafjpnka)
now shows v0.4.8. This supersedes the repository's latest-store-version claim, while
leaving current package→source identity unverified. No GitHub release for v0.4.4 was
found; a GitHub release is not necessary evidence of Store publication.

### SentinelTrader: authentication defect to observed deployment

[PR #740](https://github.com/jpantsjoha/sentinelTrader/pull/740) links to earlier #607
and fixes the Google sign-in redirect loop. Recorded red-on-main regression and
independent security/QA review produced a further frame-header correction; final
commit records 250 web tests. GitHub confirms merge `b18db7f7` on 2 September.
`delivery/status-archive/2026-09-04-STATUS-pre-rewrite.md` records the same image,
web `00113-xug`, API `00140-tib`, health/handler 200 and full traffic;
`delivery/audits/2026-09-16-sre-checkup.md` repeats observation. Those records also
leave a human sign-in and demo smoke completion outstanding. Deployment is evidenced;
complete current UAT acceptance was not independently established. No dedicated stable
requirement ID was located for this fix.

### Riter: UAT journey defect to reviewed regression

REQ-019 and FF-01 connect [#380](https://github.com/jpantsjoha/ghostwriter-app/issues/380)
to actual accessibility findings. [PR #381](https://github.com/jpantsjoha/ghostwriter-app/pull/381)
records exact candidate `e308c9a610bc51b19a58bdad364fff3d6c02e919`, K3 PASS, emulator
tests and desktop/phone journey corrections; GitHub confirms merge at the inspected
HEAD. `delivery/FEEDBACK-FUNNEL-2026-09-19.md` and the planning/UAT packets preserve
acceptance and results. Human/connected UAT #376/#377 remain open. The referenced
`.verify/feedback-funnel/` and `.verify/review-e308…md` paths are absent. Independent
review located the exact candidate's review Markdown/raw text and evidence under
`.verify/feedback-funnel-2026-09-19/integration/`; its parent directory's
`delivery-receipt.json` binds PR #381, candidate and merge. Matching archived copies
also remain. Raw evidence is retained locally; the earlier cited paths need
reconciliation, and portable custody beyond this checkout remains unestablished.
The operating-model validator freshly passed with zero warnings despite stale profile
facts: structural validation does not prove semantic truth.

### Proofly: council findings to production fixes

ADR-125 records Graft-assisted navigation and council discovery/corroboration of a
credit race (#680) and tenant isolation defect (#713).
[PR #720](https://github.com/jpantsjoha/proofly-shopify/pull/720) and
[PR #719](https://github.com/jpantsjoha/proofly-shopify/pull/719) are remotely confirmed
merged on 19 August. Their bodies record review-driven corrections, 1,853 tests and
planted regressions proving the gates fail. STATUS's 8 September entry links those
fixes to `prod-v2.2.2`, source/image `6fedd67`, staging 21/21 and production 9/9 steps,
revision `00054-6qk`, and health 200. These are retained claims, not fresh cloud probes.
The [Shopify listing](https://apps.shopify.com/proofly-2) was independently accessible.
ADR-126 subsequently hardens release validation; do not attribute that newer gate
retroactively to the 8 September release.

## What transfers back to the harness

| Priority / existing owner | Evidence-backed improvement | Deterministic acceptance for future implementation |
| --- | --- | --- |
| 1 — ADOPT-DRIFT / DPS-TRACE | Canonical facts projected into adapters. Proofly AGENTS says staging-first while CLAUDE says dev-first; Riter profile denies installed companions/deployment; Sentinel release adapter conflicts with newer tag/CI policy | Fixture with conflicting active environment, gate or release facts must fail; historical facts must remain explicitly dated. Current structural gate does not do this |
| 2 — DPS-REVIEW | Portable exact-candidate receipts and source-verified findings; preserve useful BLOCK→fix→PASS interventions and bounded review rounds | Reject changed candidate/base, missing raw evidence, conditional verdict, failed/unavailable lane and unsupported reviewer identity; retain artifacts beyond worktree removal |
| 3 — DPS-PROMOTE | One release record joins source, artifact digest, environment/store version, journey acceptance, observation and rollback | Refuse identity mismatch and synthetic-as-human UAT claims. Read-only reconciliation must detect FeedEval-style published-version drift and stale PR summaries |
| 4 — DPS-CONTEXT | Keep Graft optional, pinned and development-only; freshness before navigation, then source verification | Prove effective version, changed/deleted-file refresh and failure handling. Do not infer semantic safety, hidden-check discovery or cost savings from a graph |
| 5 — DPS-VALUE | Measure accepted outcomes and effort, including failed work/review loops, at equal quality | One dated cohort with all started tasks, accepted/open/abandoned counts, known author/review/integration effort and evidence coverage; commercial fields only if chosen |

Proofly ADR-125 is especially useful: `npx @nanonets/graft@0.10.1` is isolated from
application dependencies and `make graft-check` calls the pinned tool. It records
zero new hotspots from Graft itself; council reasoning found missing checks and
concurrency defects, and the author corrected overstatements at source. This supports
the adopted division of labour. Graft freshness and vendor savings claims were not
rerun/validated in this audit. No extra skill is needed.

CI is a control outcome, not a required vendor: Cert Prep intentionally retired
Actions under ADR-0076 and currently has no required hosted checks; local convergence
and council govern its process. FeedEval currently requires three hosted checks
with administrators exempt and strict mode off; the sampled historical jobs failed
without runner steps. Riter PR #381 has no status checks, and Sentinel records a local
CI substitution during billing limits. Do not equate red hosted jobs with unreviewed
work, or procedural local receipts with independently enforced remote protection.

## Installation, measurement and limits

Observed Claude registry/cache: global enabled Join the Team **0.2.3**, plus listed
project overrides at 0.2.3. Codex's skill cache is labelled **0.3.0**. Copied manuals
and project adapters have separate revision histories. None proves which package
version executed every past task. Today's unmerged improvements receive no credit
for deliveries that preceded them.

Public checks: browser search service returned the Chrome and Shopify listings;
their reported crawl ages were two weeks and two days respectively. Chrome lists
0.4.8, updated 3 September. Cert Prep was inaccessible through that service, but a
direct unauthenticated HTTP HEAD check returned 200. These checks do not test sign-in,
installs, tenant workflows or availability over time.

The executive interpretation is stronger delivery/adoption confidence, with persistent
coherence and enforcement gaps. Strategic/product relevance has concrete examples;
engineering reviews have demonstrable interventions; SRE/release evidence exists but
is incomplete; efficiency remains unmeasured. Team-scale and independent community
benefit remain unverified. Optional commercial outcomes do not discount core delivery.

How would I break this assessment? Select only successful repositories, reward test
counts, mistake copied skills for invoked skills, treat a public listing as full
acceptance, or claim the harness caused success. Explicit lineage, dated traces,
separate evidence labels and stated sampling/attribution limits constrain those claims.
Next reassessment should include an abandoned task and a non-owner adopter, alongside
one complete acceptance→release→observed outcome trace. No automatic tracking is added.
