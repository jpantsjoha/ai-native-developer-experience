# Squadroom-informed coordination pilot

Status: proposed scope, not runtime delivery or adoption approval.
Branch: `codex/squadroom-adoption-plan`.
Base: `e93069b92735ba096abf662f2b9d95a0ebfd36f9`.
Owner: harness maintainer; accountable acceptance owner: JP.

## Outcome and golden thread

Extend the [vision](../VISION.md) and [delivery-planning requirements](../../requirements/DELIVERY-PLANNING-SYSTEM.md)
with evidence that parallel work remains owned, recoverable and traceable to accepted
outcomes. The unit of success is a checked deliverable or resolved discovery question,
not an agent turn, a commit or an approval count.

Planning is authorised. Implementation tickets, host permissions, resource ceilings,
release and adopter changes must be resolved before their execution. No new paid API,
GitHub Actions/AI, daemon, credential store or production path is introduced here.

The [EGM review measurement plan](../evaluation/egm-review/PLAN.md) remains a separate
experiment. Its before/after instructions are fixed; orchestration treatments must not
be introduced into just one EGM arm. No combined improvement claim is permitted without
an explicitly designed later factorial experiment.

## Source and confidence

Reference: [Squadroom at 23ac306b](https://github.com/squadroom/squadroom/tree/23ac306bf922741c9d2fec5765c496c7f568db90).
The source assessment inspected its architecture, threat model, claims/holds logic,
team tooling and stage-write tests. Upstream tests were read, not executed. These are
candidate mechanisms, not evidence of our performance or security.

Borrow concepts from [architecture](https://github.com/squadroom/squadroom/blob/23ac306bf922741c9d2fec5765c496c7f568db90/docs/architecture.md):
durable messaging, one integration owner, worker fencing, scoped work and visible human
decisions. Review [limits](https://github.com/squadroom/squadroom/blob/23ac306bf922741c9d2fec5765c496c7f568db90/docs/threat-model.md)
before any runtime adoption. No code is vendored in this slice. If later reusing MIT
code, preserve attribution/license and review the exact imported dependency surface.

## Architecture boundary

| Component | Owns | Does not own |
| --- | --- | --- |
| Existing harness | Accepted scope, roles, authority, checks and review contract | A second issue system or implicit permissions |
| Proposed local coordination adapter | Attempt/event ledger, dispatch ownership, acknowledged handoffs, guarded integration | Product acceptance, arbitrary shell authority, credential distribution |
| Existing host | Agent launch and actual permission enforcement | Proof that reported completion satisfies requirements |
| GitHub | Work-item identity, code, PRs and release records | Hosted validation or billed AI |
| Phoenix/EvalOps | Versioned experiment data, results and evidence verification | Scheduling authority or work-item status |
| DevDash, later | Read-only projections, freshness, evidence links and decisions requiring attention | A second mutable scheduler or inferred success from missing events |

Use existing bootstrap, delivery-orchestrator, test-strategy, Council and model-routing
contracts before adding tools. The installed skills are not a daemon. A new adapter is
an optional, separately gated runtime; the plugin remains usable without it.

## Proposed first implementation slice

One project, one orchestrator/integrator and at most two editing lanes in isolated
scratch clones/worktrees. One fresh read-only reviewer joins at the gate. Match host
and model in baseline/treatment; keep existing review floors. No speculative model
chooser, persistent autonomous team, automatic push or merge.

The smallest slice is a local command interface and transactional ledger with scripted
workers for deterministic fault tests. Select SQLite as the proposed single-machine
store, with schema versioning and transactions; confirm this in the implementation ADR.
Use an outbox/inbox boundary rather than pretending process dispatch and database commit
are one transaction. Events are append-only application records, not tamper-proof attestations.

### Minimum contract

- Each task identifies project, requirement, issue, acceptance checks, owner, allowed
  paths, base commit, scope version, dependency IDs, model/effort, budget and rollback.
- Each attempt has a new ID; messages have IDs, correlation/causation IDs, scope version,
  recipient and delivery/acknowledgement state. Retries retain earlier failures and costs.
- Events carry schema version, sequence, recorded time, actor/source and available
  observed evidence. Separate model statements from host-observed execution and checked results.
- Immutable artifacts use hashes plus locations. Record parent/worker usage, cache,
  retries and human effort; unknown fields are null with reasons, never zero.
- No raw prompts, credentials or private transcripts in Git commit messages or public
  evidence. Retain necessary private payloads outside Git with access/retention policy;
  default portable fixtures to synthetic data. Digesting private data is not anonymisation.

### Ownership and recovery rules

Claims are advisory for edits in isolated clones, mandatory for admission to integration.
Normalise repository-relative paths, resolve symlink/rename/case aliases conservatively,
reject escapes and overlapping integration claims. Ownership changes increment a fencing
epoch. Ledger write, artifact acceptance and integration all check current task scope,
base identity and epoch; a stale worker's late output is quarantined, never auto-applied.

Lease expiry does not prove a process stopped. Reassignment is refused until host-observed
termination or isolation of the old attempt is recorded. If that cannot be established,
require operator reconciliation. Existing scratch output is preserved for diagnosis.

Messages may be delivered at least once. Persist intent before dispatch, reconcile host
attempt identity after restart and deduplicate acknowledgement/effect admission. A crash
between dispatch and receipt becomes unknown, not success and not automatic re-execution.
Do not claim exactly-once external effects. Publication is outside this slice.

Dependency and hold cycles are rejected with a concrete path. Holds have owners, reasons
and resolving conditions; stale holds escalate without silently releasing permissions.
Scope changes create a new scope version and invalidate affected acknowledgements/review.

An out-of-scope diff pauses integration and preserves the entire artifact; never copy
Squadroom's automatic restoration of edits. Stage file lists cannot contain every runtime
side effect: host sandbox permissions remain required, with enforcement coverage recorded.
Do not claim OS isolation from claims, separate worktrees or fresh conversations.

One decision queue stores stable IDs, question, owner, allowed actions, evidence and expiry.
An answer binds exact scope/artifact and action; it is not permission for all later tasks.
Timeout, agent silence or a loop cap cannot waive a blocker. Progress means a newly
validated acceptance check or resolved discovery hypothesis, not merely a new commit.

## Bounded work packages

These are draft task contracts, not filed issues. File parent/children before code; keep
one integration owner. Each child records dependency, risk, tests and acceptance evidence.

| ID | Deliverable and owner role | Dependency | Deterministic acceptance |
| --- | --- | --- | --- |
| S0 | Orchestrator: current-host capability/reuse inventory and architecture decision | This plan accepted | Every required control mapped to native capability, adapter or explicit unsupported state; no duplicate scheduler |
| S1 | Architect + test strategy: versioned task/event schema and fixture ground truth | S0 | Reject absent requirement/owner/check IDs, stale schema and invalid state transitions; independent expected outcomes |
| S2 | Runtime implementer: ledger, inbox/outbox, leases and reconciliation | S1 | Crash tests around every persistence/dispatch boundary; no accepted stale result, duplicate effect or lost acknowledged message |
| S3 | Runtime implementer: claims, scope checks, hold cycles and decision lifecycle | S1; integrate with S2 | Negative path/symlink/case/rename tests, overlapping integration claims, expired approval and cycle detection |
| S4 | EvalOps implementer: immutable run ledger and Phoenix export adapter | S1; complete S2/S3 for paired runs | All planned slots reconcile to exact outputs/errors/exclusions; export/verify and paired analysis agree |
| S5 | Integration owner + independent Council: scratch end-to-end pilot | S2–S4 | Full local gates, exact candidate review, deterministic fault suite and valid paired report; no safety regression |
| S6 | DevDash owner: optional read-only view contract and consumer test | S5 supports value | Replay shows fresh/stale/unknown/failed separately, correct links, no write authority or silent success |

Parallelise S2 and S3 only after S1 freezes interfaces and separates file ownership;
S4 can build against fixtures in its own lane. Convergence is one serial integration step.
S0–S5 are proposed harness work. S6 needs separate DevDash backlog/owner coordination;
this branch does not modify that repository. Rebranding is independent of all six.

## Test and measurement protocol

First test control correctness without LLMs using scripted workers and synthetic cases.
Fault scenarios: duplicate/out-of-order delivery, lost acknowledgement, crash before/after
persist/dispatch/receipt, stale lease output, unresolved running process, conflicting
scope, path aliases, dependency cycle, expired decision, truncated evidence, unavailable
Phoenix and missing usage. Include clean parallel work and legitimate no-code discovery
so restrictive controls cannot win merely by refusing everything.

Proposed pilot: 12 calibration and 24 held-out task scenarios, family-separated with
independently checked expected outcomes. Three matched repetitions per scenario and arm
produce 144 planned attempts (72 pairs). Freeze hashes, faults/seeds, timing, resource
limits and decision thresholds before running. Treat calibration cases as tuning only.

Baseline: current native host coordination and existing checks; treatment: same workflow
plus the scoped coordination adapter. Same agents, model/effort, accepted task, resources,
source snapshot and review policy; counterbalanced random order. Both arms receive identical
instrumentation and fault injection. A fake-worker result proves control behaviour only;
real-agent effectiveness requires a separately labelled matched pilot after deterministic
success. Preflight must establish treatment separation and host capability; otherwise
report feasibility, not causal improvement. Do not pool synthetic and live results.

Primary outcome: proportion of scenarios reaching the correct accepted or correctly
blocked outcome within the frozen budget. A legitimate refusal is correct only where
independent ground truth expects it. Always report successful delivery and correct
blocking separately. Counter-metrics: clean-task completion, unnecessary blocking,
conflicting integrations, duplicate accepted effects, recovery time, owner interventions,
wall-clock, parent/worker tokens/cache/retries and measured human minutes.

Proposed adoption rule, to be accepted before execution: zero unsafe acceptance or lost
acknowledged handoff; no decrease in clean-task completion; positive lower 95% bound on
paired primary-outcome improvement; median paired elapsed-time overhead at most 20%.
Bootstrap by scenario family, averaging repetitions within scenario first. Resource/effort
missingness blocks efficiency claims. Small samples cannot qualify rare-event safety.
A failed hard invariant is a stop even if average performance rises. Inconclusive means
no expansion; revise on calibration, then use a fresh held-out set for another attempt.

Require all 144 planned slots and 72 pairs for adoption. Timeouts/model errors are
observed failures; unattempted/infrastructure-invalid/contaminated slots remain distinct
and make the adoption test incomplete. Do not silently replace them. Diagnostic retries
have separate IDs and cannot substitute for primary failures. Retain every attempt.
The planned ledger is authoritative: EvalOps may verify an export with exclusions, so
reconcile all slots and exclusions before computing quality or adoption. Integrity PASS
is not quality PASS. Pin experiment manifest, code/model/config/corpus/rubric hashes and
export verified Phoenix records using the existing single service.

Default execution ceiling proposal: one project, four agent slots including reviewer,
one active local-model generation at a time, 30 minutes per live task, four hours per
batch, no paid API spend. Freeze concrete budgets after S0 capacity sampling and before
S5; reaching a ceiling preserves incomplete outcomes rather than resetting the budget.
No experiment or local model load is authorised merely by this plan. Resource guards,
provider policy, existing approval boundaries and exact-candidate review still apply.

## Rollout, rollback and evidence

S0 chooses between native-only controls and a minimal adapter; do not build if native
capabilities already meet acceptance. Start shadow recording, then guarded integration
in scratch projects, then a separately accepted one-project trial. Shadow recording
must never be described as enforcement. Stop on duplicate effects, lost messages,
authority escalation, scope breach, incomplete evidence or unacceptable overhead.

Rollback disables dispatch/integration through the adapter, terminates or reconciles
owned attempts and returns to native workflow. Keep ledger/receipts and scratch artifacts;
no deletion, automatic source reset, credential migration or release rollback is implied.
Schema upgrades need fixture-tested migration and backup/restore before activation.

Retention proposal: synthetic reproducible fixtures/results permanent; private payloads
expire after 30 days unless the project retention policy requires otherwise. Preserve
sanitised manifests and decisions, with redaction and deletion verification before any
sharing. No additional service or storage backend is selected.

Completion of this planning slice: frozen source reference, scoped contracts, measurements,
risks, independent fresh-context plan verdict, local documentation validation and a branch.
Implementation completion later requires local `make check`, independent exact-candidate
Council review and the specified integration/user-path evidence. No merge, tag, install,
publication, model qualification or improved performance follows from this plan.

## Decisions and adversarial challenge

| Decision | Owner and resolving gate | Default until resolved |
| --- | --- | --- |
| Native capabilities versus adapter and transactional schema | Architect, S0/S1 review | No runtime dispatch implementation |
| Host permission enforcement and termination evidence | Integration owner, S0 capability probe | Unsupported routes refused |
| Corpus labels, thresholds and live-run budgets | JP + independent test reviewer, before S5 | No adoption claim or live pilot |
| DevDash read-only contract | DevDash owner, after S5 | No consumer edits |
| Plugin name and compatibility migration | JP, separate naming decision | Retain `join-the-team` identifiers |

How would this fail? A stale worker might still mutate files after its lease expires;
fencing only protects effects routed through the adapter, so termination/isolation is
mandatory before reassignment. A queue could duplicate commands after a crash; reconcile
unknown dispatch rather than replay blindly. A blocked-everything harness could score
well on adversarial cases; require clean completion and independent expected dispositions.
A dashboard could disguise missing evidence; render unknown/stale explicitly. A rebrand
could break installed skills; keep that migration separate and test both names first.
