# Delivery status

## Current release

The latest release is [v0.5.0](https://github.com/jpantsjoha/ai-native-developer-experience/releases/tag/v0.5.0),
the first under the **DevEx Charter** name (`devex-charter`); v0.4.0 was the last
`join-the-team` release. Existing installations do not update automatically: follow the
[migration guide](install/rebrand.md). The tag/release record owns publication state; a
version in a manifest alone is not publication. See the
[source-release decision](../architecture/decisions/ADR-003-source-release.md).

## Delivered since 0.5.0 (unreleased)

The offline `make planning` gate (part of `make check`) validates the declared delivery
records: required documents, stable IDs, lifecycle states, parents, dependencies,
supersession, local links and Done evidence. See the
[deterministic gate runbook](DETERMINISTIC-GATES.md). Structural PASS does not establish
semantic correctness or release approval.

## Known limits

Live host installation and upgrade coverage for the renamed package, upstream directory
listings and enterprise effectiveness remain unproven. Local fixtures establish package
paths and preservation, not every host UI. [ROADMAP](ROADMAP.md) owns milestone order.
