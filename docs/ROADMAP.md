# Delivery roadmap

**Owner:** harness maintainer. Order is by accepted outcome, not skill count.

| Order | Outcome / work item | Exit evidence | State |
| --- | --- | --- | --- |
| 1 | #32: project, user and plugin adoption from intent to live | Fresh consumer journey, preserved existing records, local checks and independent review | Current source work; not released |
| 2 | Release and installation reconciliation | Chosen release version, host install/update checks and rollback | Next; published version remains v0.3.0 |
| 3 | Demonstrate adopted workflow value | One bounded contributor trial: accepted outcome, friction, rework, effort and limits | Proposed; no savings baseline |
| 4 | #24: context loading and incremental review findings | Bounded trial, retained finding history, fixed quality floor | Proposed; prioritise observed friction |
| 5 | #23: decision-record hygiene | Existing-record validation with negative fixtures and owned rollout | Captured; not implemented |

PR #28 (release/review controls) and PR #31 (guarded routing) are merged source changes.
Their merge does not establish package release, installed adoption or efficiency gains.

Use [HARNESS-ADOPTION](HARNESS-ADOPTION.md) for applicable service-transition prerequisites,
conversation provenance and capability ownership. These are extensions of existing
mechanisms, not additional skills or an automatic learning system. Optional commercial
experiments do not block engineering acceptance.

Release/tag/install of the plugin follows its release strategy and operator authority.
Source merge, package release and observed adopter outcomes are distinct milestones.
