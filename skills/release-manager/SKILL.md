---
name: release-manager
description: Govern the SemVer release process — versioning discipline, tag-based GitHub releases, changelog hygiene, and the ADR that confirms the release strategy is agreed. Trigger when setting up a release process, before a first public release, or when release practice has become inconsistent. Owned by delivery-orchestrator.
---

# Release Manager

> **A release without a confirmed process is a deployment. A deployment without a rollback plan is a gamble.**

This skill governs the release process itself — not a specific deployment (that is
`release-readiness`) and not the CI infrastructure (that is `github-manager`). It ensures
the team has agreed, documented, and is consistently following a versioning and release
strategy, anchored by an ADR.

## When to use

- Setting up the release process for a new repository
- Before the first public or production release of a project
- When release practice has become inconsistent: manual uploads, skipped tags, changelog
  gaps, or no named release owner
- As part of the bootstrap workflow, when the automation area is being defined
- When `delivery-orchestrator` identifies a release-process gap during R2/R3 classification

## Operating model context

Three release-adjacent skills exist in this harness with distinct responsibilities:

| Skill | Responsibility |
|---|---|
| `github-manager` | CI trigger configuration, runner cost, branch protection, tag-event wiring |
| `release-manager` (this skill) | Process governance: SemVer discipline, changelog, ADR, deviation authority |
| `release-readiness` | Go/no-go gate for a specific deployment: failure modes, rollback, monitoring |

Use all three in sequence for a new project. Use `release-manager` alone when auditing or
repairing an existing process. Always hand off to `release-readiness` before the tag is
pushed.

## Default release strategy

Unless a team ADR explicitly records a different approach, the default is:

- **Versioning**: Semantic Versioning — `MAJOR.MINOR.PATCH`
  - `PATCH` — backwards-compatible bug fixes
  - `MINOR` — backwards-compatible new capability
  - `MAJOR` — breaking changes
- **Tagging**: `v{MAJOR}.{MINOR}.{PATCH}` tags on the default branch trigger release
  builds in CI. No other event produces a release artifact.
- **Artifacts**: produced by CI from the tagged commit — never from a local workstation.
- **Changelog**: `CHANGELOG.md` updated before every release; format follows
  [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- **GitHub release**: created by the CI pipeline, linked to the tag, with the changelog
  entry as its body.
- **Release authority**: the named release owner (recorded in the operating profile)
  approves and pushes version tags. No one else pushes `v*` tags to the default branch.
- **Source of record**: this repository's issues, ADRs, and architecture docs are the
  source of truth unless a team ADR explicitly records otherwise.

## Procedure

### 1. Confirm or create the release ADR

An ADR must exist that records:

- The chosen versioning scheme (default: SemVer)
- The tagging convention and who holds release authority
- How hotfix or patch releases outside the normal cycle are handled
- Any deviations from the default strategy and the reason for them

If no ADR exists, create one using `the-architect`. The ADR is the authority record —
process enforcement without one is informal and will drift.

### 2. Audit current practice against the ADR

Check the repository for evidence of adherence:

- Are version tags following the declared convention?
- Is `CHANGELOG.md` up to date for every tagged release?
- Are release artifacts produced through the ADR-approved build path with retained provenance?
- Are GitHub releases linked to tags and changelog entries?
- Does a single named release owner control version-tag pushes to the default branch?

Flag every gap between declared ADR and observed practice. Gaps are findings, not
acceptable workarounds.

### 3. Wire the release pipeline

Confirm the following are in place (coordinate with `github-manager` for CI config):

The list below describes the default tag-triggered CI path. For an ADR-approved
alternative, substitute its build/tag sequence and equivalent provenance controls.

- A CI workflow triggers on `v*` tags
- The workflow produces and uploads the release artifact
- The workflow creates a GitHub release with the changelog entry as its body
- Tag-specific rules prevent unauthorised creation, movement or deletion of `v*`
  tags; inspect them directly, because main branch protection does not protect tags

### 4. Define the release checklist

Before any tag push, the release owner verifies:

- [ ] `CHANGELOG.md` entry written, reviewed, and committed
- [ ] Version identifier bumped in all manifests and committed
- [ ] Exact candidate convergence and independent review are current with zero conditions
- [ ] `release-readiness` go/no-go, target, authority and rollback are recorded

After authorisation, execute and observe the release using the ADR's sequence
(the entries below show the default CI path):

- [ ] `v{version}` tag pushed to the default branch
- [ ] CI release workflow completed and artifact verified
- [ ] GitHub release created and linked to tag and changelog
- [ ] Promoted artifact digest, environment, health/acceptance and observation recorded
- [ ] Downstream consumers notified if the release contains breaking changes

### 5. Hand off to release-readiness

Invoke `release-readiness` before the tag/promotion action, not after the execution
checklist. Keep merge, artifact release and environment promotion as separate gates.
Use the maturity and promotion contract in
[`workflow-audit.md`](../delivery-orchestrator/references/workflow-audit.md).
Promote the verified artifact and retain its source/tag/digest/environment chain;
rebuilding requires new artifact evidence. Project ADRs may select a different
release sequence, but must state it and prove equivalent provenance and rollback.

## Outputs

- Release ADR (or gap: ADR missing, with named owner and required-before trigger)
- Audit report: declared practice vs. observed practice, with gap list
- Wired release pipeline confirmation
- Release checklist for the team to own going forward

## Guardrails

- **No release process without an ADR.** Conventions without a decision record drift.
- **Follow the approved build and tag sequence.** Tag-triggered CI is the default;
  an ADR may choose a controlled local/hybrid build or tag-as-record sequence.
  Reproducibility depends on pinned inputs, environment and verified artifact
  provenance, not merely where a build runs.
- **The changelog is not optional.** Every release without a changelog entry is invisible
  to users and to future maintainers.
- **Release authority must be named.** Shared ownership of version tags is no ownership.
- **Deviations require an ADR amendment.** "We'll do it differently this time" is drift,
  not a decision.

## Anti-rationalization table

| Excuse | Counter |
|---|---|
| "We all know the release process" | Tribal knowledge drifts. An ADR does not. |
| "The changelog is a nice-to-have" | Every future debugging session starts there. Write it now. |
| "I'll build the release locally, it's faster" | Use the ADR-approved path and prove source, build environment and artifact digest. Neither local execution nor CI alone proves reproducibility. |
| "We don't need an ADR for something this simple" | One page of ADR prevents months of inconsistency. Write it. |
| "The tag was already pushed, I'll do the changelog after" | The changelog belongs before the tag. Reversing this loses the discipline. |
