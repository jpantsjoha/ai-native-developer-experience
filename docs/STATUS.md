# Delivery status

## Current release

As of 20 November 2026 the latest published release is
[v0.7.0](https://github.com/jpantsjoha/ai-native-developer-experience/releases/tag/v0.7.0)
(released 20 November 2026). The 0.6 line onward keeps the rename backward compatible: `devex-charter` for new
installs, `join-the-team` as a legacy alias. Existing installations do not update
automatically: follow the [migration guide](install/rebrand.md). The tag/release record
owns publication state; a version in a manifest alone is not publication. See the
[source-release decision](../architecture/decisions/ADR-003-source-release.md).

## Merged, not yet released

- **Baseline hygiene** ([pull request 46](https://github.com/jpantsjoha/ai-native-developer-experience/pull/46),
  merged 26 November 2026): the three session commands enter through
  `delivery-orchestrator` (FR-6), `make typecheck` covers every Python and shell file and
  fails closed, Python 3.9+ runs the gates, and the ADR skills match the validator.
  Waits on JP: accept or amend
  [ADR-007](../architecture/decisions/ADR-007-canonical-adr-format.md) (Proposed).
  See the [CHANGELOG](../CHANGELOG.md).
- **Companion and tool references** ([pull request 45](https://github.com/jpantsjoha/ai-native-developer-experience/pull/45),
  merged 26 November 2026): companions re-verified on 25 November 2026, a context-graph
  lane (Trail-code, Graphify), client-work data-egress notes, and `chrome-devtools-mcp`
  1.14.0. See the [CHANGELOG](../CHANGELOG.md).

0.7.0 was released on 20 November 2026 (tag `v0.7.0`, public pull request 43).

## In progress

- **Adoption modes and the human-in-the-loop queue**: specification
  [AMH-001](../requirements/ADOPTION-MODES-HITL.md) and
  [ADR-006](../architecture/decisions/ADR-006-adoption-modes-and-hitl-queue.md) were
  accepted on 20 November 2026 (development pull request 14). Its routing rule is built,
  as the next entry says. The adoption modes and the queue are not built. It is
  milestone 5 on the [roadmap](ROADMAP.md).
- **The orchestrator as the default entry**: released in 0.7.0
  (development pull requests 19 and 22). Each of the 24 specialist skills names
  `delivery-orchestrator` as its entry and the check that proves its output, or says there
  is none. Measured on Claude Code and Codex. See the
  [routing evaluation](../evals/routing/README.md).

The offline `make planning` gate (part of `make check`) validates the declared delivery
records: required documents, stable IDs, lifecycle states, parents, dependencies,
supersession, local links and Done evidence. See the
[deterministic gate runbook](DETERMINISTIC-GATES.md). Structural PASS does not establish
semantic correctness or release approval.

## Known limits

Live host installation and upgrade coverage for the renamed package, upstream directory
listings and enterprise effectiveness remain unproven. Local fixtures establish package
paths and preservation, not every host UI. [ROADMAP](ROADMAP.md) owns milestone order.
