# Join the Team: executive rubric and initial assessment

**Rubric:** 1.0 · **Date:** 2026-09-26
**Assessor:** Codex, a contributor to this candidate; independent challenge required
**Assessed candidate:** `e37958053b9df329dada133d594eed6448ebc07c`
**Scope:** local enhancement branch; installed/released 0.3.0 is not re-scored here

Current judgement: a useful internal delivery harness with credible local engineering
controls, incomplete end-to-end enforcement and unmeasured net value. Evidence does
not establish an optimum, commercial validation or consistent effectiveness across
every supported runtime. Scores are provisional ordinal judgements against explicit
criteria, not objective measurements of quality.

## Purpose

The [vision](VISION.md) is to help human–AI teams turn intent into accepted outcomes
without losing ownership, evidence or continuity. The value hypothesis is less avoidable
rework, coordination and operator effort at an equal or better quality floor.
The operator confirmed the primary purpose: consistent, proven delivery of value,
with proportionate effort and coherent engineering. Commercial, marketing, reputation
and community outcomes are optional project objectives, not core maturity conditions.

Every additional control should name the recurring failure it prevents, its operating
cost and the simpler existing alternative it was compared with. No new skills are
proposed by this assessment.

## Three separate assessments

- **Capability maturity, 0–4:** progress against the anchors below, within a named scope.
- **Demonstrated impact:** outcome change, baseline, period, sample and trade-offs.
  Use **U — unmeasured** where those are missing.
- **Operator experience, 1–5:** JP's own usefulness, confidence and friction ratings,
  each with an example. Continued use is not a numerical satisfaction score.

| Level | Anchor | Evidence needed |
| --- | --- | --- |
| 0 — Absent | Required capability confirmed missing | Inspected scope and specific missing control; unavailable evidence is not 0 |
| 1 — Defined | Intent/policy/hypothesis explicit | Written outcome, owner and procedure; no implementation claim |
| 2 — Usable | Artifacts/mechanisms can be used | Inspectable assets/implementation and adoption example; validation gaps may remain |
| 3 — Verified locally | Scoped capability passes reproducible checks | Candidate-bound execution, meaningful refusal cases where applicable, independent challenge |
| 4 — Proven in operation | Benefit/reliability persist in representative use | Repeated outcomes, sustained observation, comparable baseline and measured operating burden |
| U — Unknown | Evidence cannot support a level | Missing source/coverage named with a next check |

A rule cannot score 3 because it sounds complete. A tested parser cannot make an entire
security programme level 3. Test count describes a suite, not a maturity percentage.
Low evidence maturity need not mean poor experience or a low-value idea.
Record candidate, exercised runtimes, period, criteria, sources, limits, assessor and
next action. Keep declared, implemented, enforced and observed distinct; record bypasses
and never infer remote enforcement from YAML. Explain the anchor and gap to the next level.

## Initial executive scorecard

Evidence codes resolve below. These assess capability maturity; realised ROI, revenue,
brand uplift and independent community benefit have not been quantified.

| Lens | Criteria | Maturity / 4 | Evidence and limitation | Next evidence |
| --- | --- | --- | --- | --- |
| **CEO: strategic relevance** | Problem, intended users, why this approach, objectives and stop criteria | **2** | E1/E5: coherent vision and operator-led improvements in owned projects; no comparative value baseline | Priority objective traced to accepted outcome, compared with a simpler alternative |
| **CPO: product ownership** | Owner, accepted scope, journey, acceptance, prioritisation and change control | **2** | E2: accepted DPS-001 and usable workflow/spec assets; transitions not universally enforced | Actual work showing accepted requirements, controlled changes and user acceptance |
| **CTO: architecture/portability** | Boundaries, reuse, decisions, adapters and compatibility | **3, scoped** | E3: local packaging/contract checks and review; not every runtime's install/upgrade behaviour | Fresh-install, upgrade and removal journeys per supported runtime/version |
| **Engineering: quality controls** | Gates execute, defects refuse, evidence binds the candidate | **3, scoped** | E3/E4: 141 local tests, including 40 delivery-gate tests, red regressions and exact-content review; bounded structural grammar | Gate effectiveness and escaped defects across ordinary delivery |
| **Golden thread: coherence** | Vision→requirements→decisions→work→tests→review→release→observation agree | **2** | E2/E4/E5: record ownership/structural checks exist; semantic/live reconciliation and executed-test coverage incomplete | Complete trace through actual release/observation with current state reconciled |
| **Security/governance** | Authority, least privilege, data boundaries, independent review and auditability | **2** | E3/E5/E6: local refusal tests and authority/privacy guidance; receipts do not authenticate reviewers | Exercise trust boundaries and candidate/identity replay refusal in the authorised enforcement path |
| **SRE/release: operability** | Installation, diagnostics, compatibility, rollback, support and observation | **2** | E5/E6: packaged assets/runbooks; no release/recovery rehearsal for this candidate | Representative plugin install/upgrade/rollback drill; assess adopter SRE separately |
| **COO: delivery operations** | Ownership, WIP, handoffs, queues, bounded retries and maintainability | **2** | E2/E5: workflow and exercised review/integration; WIP/loop limits substantially procedural | Several deliveries with queue/override/handoff records and support burden |
| **COO/CFO: efficiency** | Effort/cost per accepted outcome, rework and opportunity cost | **1** | E5: measurement policy exists; total human effort/model spend not captured. Parser review cycles show rework, not net savings | Matched tasks with author/review/retry/integration effort and known spend, including abandoned work |
| **Developer experience** | First value, resumption, clear errors, cognitive burden and sustainable use | **2** | E5 and JP's reported use: adoption exists; no numeric sentiment or fresh-user onboarding study | Separate JP ratings and an observed new-user task, including interventions/confusion |
| **CMO: positioning/value capture** | Audience, truthful promise, proof, distribution and value pathway | **2 assets / 1 validation** | E1/E6: positioning/packaging/submission assets; no measured funnel, brand attribution or willingness to pay | Audience tests a proposition and produces a predeclared qualified response or repeat use |
| **Open-source/community** | Reuse rights, adoption, contribution/support and independent benefit | **2** | E6: licence/install material/public contribution path; owned-project reuse is not community traction | Non-owner adopter completes a useful task and repeats use without disproportionate support |

Local engineering assurance is strongest. Strategic/operating structure is usable;
full lifecycle coherence/enforcement is incomplete. Economic, commercial and community
impact remain **U**. No lens earns 4. Continued measured internal use is reasonable;
this is not release approval or public-beta readiness. Installed 0.3.0 cannot inherit
an unreleased branch's scores.

Do not average yet: lenses overlap and several outcomes are unknown.
If a portfolio decision later requires weights, agree them before scoring, show evidence
coverage and retain the dimensions. Authority, security, required acceptance and recovery
failures cannot be averaged away.

## Portfolio evidence addendum — 26 September 2026

The initial table above remains a snapshot of the local plugin candidate. It
underweights the delivery evidence available from adopters. The subsequent
[five-project adoption audit](ADOPTION-OUTCOMES-AUDIT-2026-09.md) establishes explicit
lineage and delivery use in Cert Prep, FeedEval, SentinelTrader and Riter. Proofly
adds useful delivery and Graft evidence; its package lineage remains operator-attested.
Public marketplace listings and candidate-linked corrections strengthen the case for
practical usefulness. They do not retroactively validate this unreleased branch.

Use the audit's separate adoption scale, where 3 means evidenced delivery use; it is
not interchangeable with this rubric's capability level 3. The portfolio supports
successful internal adoption and useful quality interventions. Full semantic coherence,
authenticated review, current UAT acceptance and comparative efficiency remain uneven
or unmeasured. No aggregate percentage or claim of optimality follows.

Installation correction: the inspected Claude registry and cached manifest identify
user-scoped **0.2.3**, globally enabled, with project overrides also at 0.2.3. The
Codex skill cache is labelled **0.3.0**. Earlier references to installed 0.3.0 apply
to that Codex surface, not every Claude session. Copied manuals and project adapters
have their own revisions; exact runtime invocation was not retrospectively proven.

## CTO's four Cs

| Quality | Question | Current reading |
| --- | --- | --- |
| Clear | Can a newcomer identify contract, owner and next action? | Entry points exist; fresh-user comprehension/time-to-value untested |
| Coherent | Does each change serve an objective through observed outcome? | Structural links exist; outcome reconciliation incomplete |
| Consistent | Do adapters, scripts, docs and runtime follow the same rules? | Local packaging drift checked; cross-runtime/adopter drift remains |
| Complete | Are applicable acceptance, security, operational and user outcomes evidenced? | Gaps recorded; structural PASS alone cannot establish completeness |

These questions apply across lenses, rather than adding four numbers to an average.

## Measurement pilot

Use existing issue/evidence records, without a new skill, tracker or automatic telemetry.
A practical pilot is the next ten bounded items across at least two owned projects.
This is a learning sample, not statistical proof. Record complexity, risk, scope changes
and runtime; compare equivalent quality floors. Observational comparison is not causality.

| Metric | Definition/source | Decision and caveat |
| --- | --- | --- |
| **Accepted-outcome yield** | Items meeting predeclared milestone acceptance / all items started in a dated cohort. Separately report accepted, failed/abandoned and still-open counts. Source: work items/acceptance receipts | Does effort reach outcomes? Freeze denominator/acceptance; do not exclude failures or split items to raise the ratio. Milestone acceptance need not equal live-user impact |
| **Effort per accepted outcome** | All recorded author/review/retry/integration minutes for the cohort / accepted outcomes; include abandoned work. Known cash spend reported separately with coverage | Is benefit worth the burden versus simpler execution? With zero accepted outcomes the ratio is undefined. Unknown time/cost stays unknown; lead time/review rounds diagnose movement |
| **Repeat voluntary use** | People/projects using the core workflow on two eligible occasions / those observed with two opportunities. Report counts, period and internal/external cohorts separately. Source: opt-in adoption notes | Is usefulness durable? Installs/stars/owned-project counts are insufficient. Include support burden; no unsolicited tracking |

Guardrails: acceptance escapes/reopened work by severity; material authority,
data-boundary or recovery failures. An unresolved severe failure blocks the relevant
delivery claim regardless of efficiency. Collect a baseline before setting savings targets.
For branding, test a public-safe case study with an attributable qualified response.
For revenue, test an offer/willingness to pay before forecasting. For community value,
seek independent repeat use. These are experiment proposals, not market findings;
publication/outreach still requires the operator's instruction.

## Operator experience and reassessment

JP can rate each 1 (poor) to 5 (excellent), with an example:

| Question | JP's rating | Example |
| --- | --- | --- |
| Does it help me complete the intended work? | Not supplied | Pending |
| Do I trust its checks and understand remaining uncertainty? | Not supplied | Pending |
| Is effort/friction proportionate to value? | Not supplied | Pending |

Keep experience beside evidence maturity. High satisfaction/low evidence suggests
measuring value; strong tests/low satisfaction suggests simplifying workflow.
Reassess at a milestone/release or material failure, with a light monthly review only
during active development. This is a proposed cadence, not a scheduled automation.
Preserve dated snapshots, rubric version and assessed commit. Raise scores only when
new evidence meets the next anchor, not when prose improves.

## Evidence and actions

- **E1:** [Vision](VISION.md), [README](../README.md): purpose/audience/proposition.
- **E2:** [DPS-001](../requirements/DELIVERY-PLANNING-SYSTEM.md), [workflow](WORKFLOW.md),
  [ADR](../architecture/decisions/ADR-001-durable-planning-control-plane.md): ownership,
  acceptance, architecture and record boundaries.
- **E3:** [Makefile](../Makefile), [tests](../tests/), [packaging validator](../scripts/validate_plugin.py)
  and retained local `delivery-gates-handoff.json`: 141 tests/review at the assessed
  candidate. Receipt is in the adjacent audit-evidence directory, not authenticated
  public attestation. Reading it does not imply a new test run.
- **E4:** [Gate runbook](DETERMINISTIC-GATES.md), [validator](../scripts/validate_delivery.py):
  structural scope, grammar and refusal cases.
- **E5:** [Status](STATUS.md), [roadmap](ROADMAP.md), [audit](HARNESS-WORKFLOW-AUDIT-2026-09.md),
  [optimisation review](OPTIMISATION-REVIEW-2026-09.md): provenance, gaps and proposals.
  Cross-project inspection does not prove incremental benefit.
- **E6:** [Privacy](PRIVACY.md), [licence](../LICENSE), [submission](PLUGIN-SUBMISSION.md),
  [release guidance](../skills/release-readiness/SKILL.md): assets/procedures, not market
  traction or comprehensive security assurance.

DPS-VALUE owns the measurement pilot; DPS-TRACE owns outcome reconciliation; DPS-REVIEW
owns trusted review evidence; DPS-PROMOTE owns release/recovery drills. Prioritise real
outcome measurement and consequential enforcement gaps. No additional skills.

How would I break this assessment? Reward documents I wrote, infer ROI from green tests,
count owned projects as independent demand, or apply unreleased changes to installed
software. Candidate binding, explicit anchors/unknowns, separate experience/impact and
independent challenge address these risks. This is a disclosed judgement, not certification.
