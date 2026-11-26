# Delivery status

## Current release

As of 26 November 2026 the latest published release is
[v0.7.1](https://github.com/jpantsjoha/ai-native-developer-experience/releases/tag/v0.7.1)
(released 26 November 2026; tag on the [release pull request 49](https://github.com/jpantsjoha/ai-native-developer-experience/pull/49)
merge commit, tree identical to the reviewed candidate). The 0.6 line onward keeps the rename backward compatible: `devex-charter` for new
installs, `join-the-team` as a legacy alias. Existing installations do not update
automatically: follow the [migration guide](install/rebrand.md). The tag/release record
owns publication state; a version in a manifest alone is not publication. See the
[source-release decision](../architecture/decisions/ADR-003-source-release.md).

## Merged, not yet released

- **0.8.0** is the release candidate in this public pull request: the manifests read
  0.8.0 and the CHANGELOG carries its section. Publication is recorded here only after the
  `v0.8.0` tag and GitHub release are verified. It carries `design-steward` (27 skills),
  the literal ratchet, the hook templates and the adoption gaps (development pull requests
  29, 31 and 37), and the operator-queue tooling (development pull request 35). Release
  approved by JP on 26 November 2026. See the [CHANGELOG](../CHANGELOG.md).

0.7.1 was released on 26 November 2026 (tag `v0.7.1`). It carries
[pull request 46](https://github.com/jpantsjoha/ai-native-developer-experience/pull/46)
(the three session commands enter through `delivery-orchestrator`, a fail-closed
`make typecheck`, Python 3.9+, ADR skills aligned with the validator) and
[pull request 45](https://github.com/jpantsjoha/ai-native-developer-experience/pull/45)
(companion and tool references re-verified, a context-graph lane, `chrome-devtools-mcp`
1.14.0). Waits on JP: accept or amend
[ADR-007](../architecture/decisions/ADR-007-canonical-adr-format.md) (Proposed).
See the [CHANGELOG](../CHANGELOG.md).

## In progress

- **Design harness (24 November 2026):** `design-steward`, the literal ratchet and three hook
  templates (development pull requests 29 and 31), in the 0.8.0 candidate. The
  adoption gaps found adopting it into DevDash (issue 32) merged on 26 November 2026 (development pull
  request 37): adopt-only bootstrap, settings and pre-commit writers, path-owner hooks, a
  resolved Bash-write detector, and a raise check that fails closed on an unresolvable base
  ref. Open: issue 38 (keep `.claude/settings.json` formatting on registration; cosmetic).
  Not blocked.

- **Adoption modes and the human-in-the-loop queue**: specification
  [AMH-001](../requirements/ADOPTION-MODES-HITL.md) and
  [ADR-006](../architecture/decisions/ADR-006-adoption-modes-and-hitl-queue.md) were
  accepted on 20 November 2026 (development pull request 14). Its routing rule is built,
  as the next entry says. The queue validator and idempotent migration command
  (`scripts/hitl_queue.py`, run in `make check`) and this repository's own adoption are built
  (development pull request 35, issue 11, 26 November 2026); DevDash adopted the same
  contract and will read the queue. Bootstrap creation of the queue (#5) and team mode (#6, #7) are not
  built. It is milestone 5 on the [roadmap](ROADMAP.md).
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
