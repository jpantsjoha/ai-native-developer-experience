# Delivery status

## Current release

As of 26 November 2026 the latest published release is
[v0.7.1](https://github.com/jpantsjoha/ai-native-developer-experience/releases/tag/v0.7.1)
(released 26 November 2026). The 0.6 line onward keeps the rename backward compatible: `devex-charter` for new
installs, `join-the-team` as a legacy alias. Existing installations do not update
automatically: follow the [migration guide](install/rebrand.md). The tag/release record
owns publication state; a version in a manifest alone is not publication. See the
[source-release decision](../architecture/decisions/ADR-003-source-release.md).

## Merged, not yet released

Nothing: 0.7.1 was released on 26 November 2026 (tag `v0.7.1`). It carries
[pull request 46](https://github.com/jpantsjoha/ai-native-developer-experience/pull/46)
(the three session commands enter through `delivery-orchestrator`, a fail-closed
`make typecheck`, Python 3.9+, ADR skills aligned with the validator) and
[pull request 45](https://github.com/jpantsjoha/ai-native-developer-experience/pull/45)
(companion and tool references re-verified, a context-graph lane, `chrome-devtools-mcp`
1.14.0). Waits on JP: accept or amend
[ADR-007](../architecture/decisions/ADR-007-canonical-adr-format.md) (Proposed).
See the [CHANGELOG](../CHANGELOG.md).

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
