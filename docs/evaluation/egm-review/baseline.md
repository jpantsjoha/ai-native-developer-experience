# Review workflow — Claude Code and Codex

JP's user-level adoption, 2 November 2026. Applies to engineering review in both
hosts. Read with `cross-model-council/SKILL.md`, which owns reviewer invocation and
subscription policy. Project requirements, risk floors and release boundaries still
apply. This is guidance loaded by the agent, not an enforced hook or branch rule.

## Intake and evidence

The delivery orchestrator binds product objective → requirement → work item → scoped
change → acceptance checks → delivery evidence. Record scope changes before expanding
implementation. A spike has a question, time limit and evidence-based disposition;
an abandoned experiment can be a valid outcome. Stop work that no longer serves the
objective rather than polishing it because it was cheap to generate.

Use small coherent changes with one integration owner. Identify affected journeys,
dependencies, risk and rollback before implementation. Risk follows behavior and
blast radius, not author, diff length or model confidence. Auth, billing, tenant/data
boundaries, credentials, installers/updaters, review controls and release paths need
focused scrutiny even when the diff is short. Retain required human decisions;
model approval never fills a required human approval slot.

Run proportionate deterministic checks before independent review: the project's
required lint/typecheck/tests/build and relevant behavioral, UI or user-journey
checks. Keep command, environment, exit status and raw output bound to the candidate.
State what those checks miss. For documentation-only work, validate applicable links,
schemas and behavioral decisions rather than running unrelated product suites.

## Review contract and project memory

Read the project's existing review policy. If it has `REVIEW.md`, explicitly include
it in the reviewer packet; do not assume either host discovers that filename. If
review knowledge repeatedly has to be rediscovered, propose or maintain one short
project-owned `REVIEW.md` through its normal delivery process. It should contain:

- Concrete local failure modes, sensitive paths and linked source/test evidence.
- Requirement and domain invariants that routine tooling cannot establish.
- Generated/vendor exclusions, retaining responsibility for changed interfaces.
- Finding format: failure scenario, affected location, evidence and severity.
- Nonblocking style preferences; linters own mechanical style. No speculative nits.

Prefer a regression test or lint rule for an executable invariant. Record a design
choice in an ADR and a recurring operational failure in a runbook. `REVIEW.md` links
to those records; it is not another incident ledger. Prune obsolete guidance after
checking its evidence and owner. Keep global AGENTS/CLAUDE files as short routing
pointers, not a growing list of project bugs.

## Independent review and convergence

Use one fresh read-only reviewer by default under the Council skill. Supply the exact
base/head or file hashes, accepted intent, relevant source/dependency context,
`REVIEW.md` if present and raw checks. A summary or Graft map helps navigation but
does not replace exact code needed to validate a finding. Add a separate security or
domain reviewer only when a concrete risk requires expertise not covered by the
first review. Parallelise independent bounded lenses, not serial approval rounds.

Track findings by stable identity: introduced/regressed versus pre-existing,
blocking versus nonblocking, affected invariant, source evidence and disposition.
Verify a proposed bug against source or a reproducer before changing code. Fix every
affected instance of an established bug class within scope; unrelated pre-existing
work gets a linked follow-up. Resolve a finding by a checked fix or an evidenced
false-positive/intentional-behavior disposition. Do not erase unresolved blockers,
count votes as proof, or downgrade a blocker merely to converge.

Declare a work-item review time/attempt budget before dispatch. Default to at most
three substantive review rounds unless a stricter project limit applies; a repeated
blocking defect triggers diagnosis earlier. At the ceiling, stop the review/fix
cycle, retain evidence and re-scope with the owner. No automatic merge or budget
reset. Candidate, branch, model and reviewer changes preserve the attempt ledger;
tool failures consume the declared elapsed-time budget and remain recorded.

The first review covers the complete change and relevant surrounding system. Each
changed candidate needs fresh review of its delta, affected dependencies and prior
finding resolutions. Link that verdict to the unchanged reviewed base and new head.
Widen to a full review when integration, scope, base or assumptions change. After
integration, verify the final assembled candidate and applicable checks; a delta
receipt is not approval for an unexamined merge or changed base. Stop when required
checks pass and a substantive independent PASS has no unresolved blockers. Avoid
repeated full reviews of an unchanged candidate seeking a different answer.

## Delivery and outcome ownership

The handoff records intent/work item, exact candidate, checks and limitations,
independent verdict and finding dispositions, risk, rollback method and accountable
owner. Keep issue/STATUS/ROADMAP/CHANGELOG ownership; link receipts instead of copying
them into every record. Before an authorised merge, check the current target base
and combined result locally. Existing branch protection remains binding. Use only
already-approved deployment paths, staging acceptance and production authority.

The integration owner retains follow-through for regressions, detection and rollback.
Flags and staged rollout are useful where already supported; adding them is separate
scoped work. No unattended merges, broad security scanner, nightly review schedule,
new cloud service or GitHub Actions/AI is enabled by this guide.

## Learn and measure

Turn confirmed review misses, incidents and reverts into project eval candidates:
pin the pre-fix source/diff, independently confirm the bug and expected finding,
retain the fix/reproducer and severity, and group related bug families. Add confirmed
clean changes and harmful-fix negative controls so a noisy reviewer cannot win by
flagging everything. Accepted comments are evidence to inspect, not ground truth by
themselves. Keep tuning and holdout cases separate, with source-family leakage checks.

When evaluating a reviewer/model/prompt/tool/rubric change, use the same pinned dataset
version and the existing EvalOps/Phoenix workflow. Score confirmed-bug recall by
severity, adjudicated finding precision, harmful false positives on clean cases and
whether applicable review instructions were followed. Count errors/missing verdicts
under the preregistered error policy; disclose small samples and uncertainty.

Track review rounds, human review/wait/repair effort separately, elapsed time, parent
and worker usage including cache/retries, and observed reverts/incidents per defined
change cohort and follow-up window. Approval/comment counts are proxies, not minutes
or evidence of correctness. Missing historical usage stays unknown. Maintain current
model floors until paired quality and whole-process evidence supports a scoped
change. Claims need exported, verified EvalOps evidence; this guide creates no
experiment or performance improvement by itself.

Source: [Anthropic engineering account](https://claude.dev/blog/solving-code-review-at-anthropic/),
15 October 2026, checked 2 November. Principles adapted to JP's local gates and
Council policy; its internal results are not a controlled benchmark for our projects.
