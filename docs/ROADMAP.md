# Delivery roadmap

**Owner:** harness maintainer. Order is by accepted outcome, not skill count.

| Order | Outcome / work item | Exit evidence | State |
| --- | --- | --- | --- |
| 1 | #32 / PR #33: project/user adoption and golden-thread delivery from intent to live | Fresh consumer journey, preserved existing records, local checks and independent review | Delivery tracked by PR #33 and v0.4.0 |
| 2 | Publish v0.4.0 and reconcile installation behaviour | Chosen release version, host install/update checks and rollback | Tag/release owns publication state; live host trials remain |
| 3 | Demonstrate adopted workflow value | One bounded contributor trial: accepted outcome, friction, rework, effort and limits | Proposed; no savings baseline |
| 4 | #24: context loading and incremental review findings | Bounded trial, retained finding history, fixed quality floor | Proposed; prioritise observed friction |
| 5 | #23: decision-record hygiene | Existing-record validation with negative fixtures and owned rollout | Captured; not implemented |

PR #28 (release/review controls) and PR #31 (guarded routing) are merged source changes.
Their merge does not establish package release, installed adoption or efficiency gains.

Use [HARNESS-ADOPTION](HARNESS-ADOPTION.md) for applicable service-transition prerequisites,
conversation provenance and capability ownership. These are extensions of existing
mechanisms, not additional skills or an automatic learning system. Optional commercial
experiments do not block engineering acceptance.

Release/tag/install follows the [source-release decision](../architecture/decisions/ADR-003-source-release.md) and operator authority.
Source merge, package release and observed adopter outcomes are distinct milestones.
