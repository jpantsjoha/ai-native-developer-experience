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
repairing an existing process. Check authority before any tag or build trigger. Hand off to `release-readiness`
before promotion; when a tag starts deployment, its workflow must hold promotion
until the artifact checks and authorised go/no-go decision are complete.

## Default release strategy

First resolve the project's approved release ADR and operating profile. The default
below is a recommendation until adopted. An approved alternative governs the audit,
checklist and pipeline too; it is not an exception to evidence or authority requirements.
If the ADR and profile disagree, stop the affected release action and reconcile them.

Declare `tag-ci` or `approved-alternative`, build trigger/executor, promotion trigger,
release owner and decision reference in the profile. Read
[the release contract](../operating-model-bootstrap/references/release-contract.md)
for the fields and offline structural check. The default, unless the ADR differs, is:

- **Versioning**: Semantic Versioning — `MAJOR.MINOR.PATCH`
  - `PATCH` — backwards-compatible bug fixes
  - `MINOR` — backwards-compatible new capability
  - `MAJOR` — breaking changes
- **Tagging**: `v{MAJOR}.{MINOR}.{PATCH}` tags on the default branch trigger release
  builds in CI. Promotion is separately gated; the tag alone grants no authority.
- **Artifacts**: produced by CI from the tagged commit in `tag-ci` mode. An approved
  alternative must identify its controlled executor and retained provenance; a local
  build does not qualify merely because it completed.
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
- Do trigger, executor and artifact provenance match the approved mode?
- Are GitHub releases linked to tags and changelog entries?
- Does a single named release owner control version-tag pushes to the default branch?

Flag every gap between declared ADR and observed practice. Gaps are findings, not
acceptable workarounds.

### 3. Wire the release pipeline

Confirm the following are in place (coordinate with `github-manager` for CI config):

- Trigger and executor match the profile (`v*` → CI for the default mode).
- Build evidence binds the exact source to the immutable artifact digest.
- Publication and promotion use the declared destination and approval boundary.
- Tag rules or equivalent repository rules restrict version-tag creation; branch
  protection alone does not protect tags.
- The adopted release command runs the structural preflight and retains its result.
  Missing required lanes remain blocking, including during hosted-CI outages; any
  substitute must already be authorised and retain equivalent required evidence.

### 4. Define the release checklist

The release owner applies the declared mode, not an unconditional CI checklist:

- [ ] Approved ADR, profile and effective trigger/executor agree; owner is named.
- [ ] Changelog and manifest versions agree with the chosen version convention.
- [ ] Exact source candidate has passed required checks and independent review.
- [ ] Build/tag action is authorised; controlled build produces an immutable artifact.
- [ ] Build, validation and review receipts bind that candidate and artifact.
- [ ] Run the release structural check with the expected candidate, then inspect the
  receipts for authenticity, adequacy and any unresolved review conditions.
- [ ] Rollback is tested; observation plan and stop criteria are ready.

### 5. Hand off to release-readiness

Before promotion, obtain the authorised go/no-go decision for the actual artifact and
target environment. If a tag triggers the pipeline, hold its deployment/publication
stage until this gate completes. A structurally valid record is not release approval.
After authorised delivery, verify the destination digest, observe the agreed signals,
and reconcile the release record, changelog and status. Notify downstream consumers
of breaking changes through the approved channel.

## Outputs

- Release ADR (or gap: ADR missing, with named owner and required-before trigger)
- Audit report: declared practice vs. observed practice, with gap list
- Wired release pipeline confirmation
- Release checklist for the team to own going forward

## Guardrails

- **No release process without an ADR.** Conventions without a decision record drift.
- **The declared mode governs all steps.** Preserve reproducible source-to-artifact
  identity and required evidence in either mode; never treat an unavailable runner as
  permission to substitute or skip a gate.
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
| "I'll build the release locally, it's faster" | Use only the approved executor and retain provenance; speed does not approve an alternative. |
| "We don't need an ADR for something this simple" | One page of ADR prevents months of inconsistency. Write it. |
| "The tag was already pushed, I'll do the changelog after" | The changelog belongs before the tag. Reversing this loses the discipline. |
