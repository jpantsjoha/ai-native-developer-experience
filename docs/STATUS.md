# Delivery status

## Dedicated-session handoff — 5 November 2026

**Next work:** Harness delivery benchmark v1, accepted by JP; scope and priority order
are in [ROADMAP](ROADMAP.md#next-priority-harness-delivery-benchmark-v1). Start with GCP
exam prep. Implementation and experiments have not started; no measured improvement
or global promotion is claimed.

**Update, 6 November 2026:** the rebrand and planning commits merged to `main` in
[PR #35](https://github.com/jpantsjoha/ai-native-developer-experience/pull/35)
(`401b735`), closing #34, and were released as
[v0.5.0](https://github.com/jpantsjoha/ai-native-developer-experience/releases/tag/v0.5.0).
Main's two Actions-only required checks were removed on JP's instruction (Actions are
retired); local `make check` plus a fresh independent review gate merges. Next owner:
create the benchmark branch from `main`.
Avoid the old iCloud-backed release-mode checkout, which previously stalled Git.

### Verified prerequisites and limits

- Local Arize Phoenix 20.19.0 was checked on 5 November with `evalops status --json`:
  health, database readiness, authentication and single-process checks passed. UI:
  <http://127.0.0.1:6006>. Recheck at session start; this is a dated health receipt,
  not proof of experiment quality or future availability.
- Existing EvalOps supports dataset pin/push, task experiments, paired comparisons,
  export and live verification. Load the global `evalops` skill for the supported flow.
- The EGM plan and pinned review guides exist under `docs/evaluation/egm-review/`;
  coordination scope exists under `docs/planning/`. Neither proves improved delivery.
- This branch has no delivered whole-task replay runner, frozen historical task corpus,
  independently labelled golden set or verified end-to-end comparative report.
- Rebrand source passed 129 local tests, lint, packaging/conformance checks and fresh
  Astra review; the upstream documentation delta passed fresh Sol review and lint.
  Private receipts: `/Users/jp/local/harness-research/devex-charter-rebrand/`. These
  establish source validation, not live host migration or harness effectiveness.

### First actions for the new session

1. Read this handoff, ROADMAP and applicable repository/project contracts. Inspect live
   worktrees/issues/PRs and establish one owner; file the benchmark execution issue
   with requirements, scope, acceptance criteria and explicit budget before code.
2. Recheck Phoenix/EvalOps and inspect available host launch/configuration controls.
   Establish whether old/new instruction packets can be separated from global policy.
   If not, document the limitation before starting a causal experiment.
3. Inspect GCP exam prep history and propose three bounded tasks with reconstructable
   pre-change states, clear deliverables and independent acceptance checks. Withhold
   completed solutions from task agents; do not mutate the active project checkout.
4. Freeze the feasibility manifest and build the smallest runner/evaluator adapter;
   locally test failure accounting, missing/duplicate runs and evidence linkage, then
   obtain fresh read-only Council review before running the pilot.
5. Export/verify the pilot and report feasibility and observed variation. Only then
   freeze the larger held-out comparison and its material-improvement decision rule.

No benchmark is running in the background. This session records the handoff only.

## Coordination adoption planning

The local `codex/squadroom-adoption-plan` branch prepares a
[Squadroom-informed scope](planning/SQUADROOM-ADOPTION.md) and preserves the separate
[EGM paired review protocol](evaluation/egm-review/PLAN.md). Both are plans; no runtime,
new experiment, measured benefit or installation is delivered. The
[naming decision](planning/PLUGIN-NAMING.md) now selects DevEx Charter.

## DevEx Charter source rebrand

[#34](https://github.com/jpantsjoha/ai-native-developer-experience/issues/34) owns
the source rename: manifests, commands, README, changelog and migration guidance.
Merged in PR #35 and released as v0.5.0 on 6 November 2026. Live host migration and
upstream listing updates remain separate gates; installed plugins are unchanged.


**Earlier release context (16 October 2026). Owner:** harness maintainer.

## Delivery record

[#32](https://github.com/jpantsjoha/ai-native-developer-experience/issues/32) and
[PR #33](https://github.com/jpantsjoha/ai-native-developer-experience/pull/33) own the
adoption/golden-thread delivery and exact-candidate checks. Coordinate with that lane
while the PR is open; its live merged state is authoritative.
[Acceptance](../requirements/ADOPTION-DELIVERY.md) covers portable installation,
lean context, product/CXO/test roles, requirement reconciliation and safe cleanup.

The latest release is [v0.5.0](https://github.com/jpantsjoha/ai-native-developer-experience/releases/tag/v0.5.0) (DevEx Charter); v0.4.0 was the last `join-the-team` release.
The tag/release record owns publication state; a version in a manifest alone is not
publication. See the [source-release decision](../architecture/decisions/ADR-003-source-release.md).
Merged source, a published tag, updated installations and observed use remain distinct.

## Remaining work

Run the measurement-first sequence above before claiming delivery improvement. Live host installation/update coverage and enterprise effectiveness remain
unproven; local fixtures establish package paths and preservation, not every host UI.
The broader DPS planning validator remains open. [ROADMAP](ROADMAP.md) owns order.
