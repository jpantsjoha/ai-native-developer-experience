---
status: approved
id: ADR-0001
date: 2026-07-23
approved: 2026-07-23
deciders: [jpantsjoha]
---

# ADR-0001: ADR lifecycle convention

## Status

**approved** — this file is `-approved`; `status:` is `approved`. A decision's state is
visible from both a directory listing and the file body. Drafts carry the `-DRAFT` postfix
and `status: draft`; superseded decisions carry `status: superseded`.

## Context

The plugin's value proposition is coherence, yet two ADR conventions had coexisted:

- `the-architect` declared `architecture/decisions/ADR-NNN-<title>.md` with an inline
  `Status: Proposed | Accepted | Superseded` field.
- `operating-model-bootstrap` referenced `architecture/decisions/ADR-0000-baseline-structure.md`.
- Maintainer intent (2026-07-23): a decision's lifecycle should be visible **both** in the
  filename (`-DRAFT` / `-approved`) **and** in an in-file `status:` field, in an `ADR/`
  folder.

A plugin that preaches one coherent contract cannot ship two ADR conventions.

## Decision

One ADR convention across the plugin and this repo:

- **Folder:** `ADR/`.
- **Filename:** `ADR-<NNNN>-<slug>-DRAFT.md` while under review; renamed to
  `ADR-<NNNN>-<slug>-approved.md` on approval.
- **In-file:** frontmatter `status: draft | approved | superseded` — redundant by design
  with the filename postfix, so state is unmistakable from `ls` and from opening the file.
- **Lifecycle location:** drafts are cultivated privately; on approval they publish to the
  public `ADR/` via PR (branch protection requires the PR).

## Consequences

Applied in the same change that approved this ADR:

- `the-architect` ADR output and format reconciled to this convention.
- `operating-model-bootstrap` baseline-ADR reference reconciled to `ADR/`.
- A deterministic test (`tests/test_adr_convention.py`) asserts the filename postfix and
  the in-file `status:` agree, wired into `make check`. Without it the redundancy could
  desync and lie.

## Adversarial gate — how would I break this?

- **Redundant state desync.** The `-DRAFT` postfix and `status:` field can drift.
  Mitigation: the CI-enforced agreement test above.
- **Two conventions during transition.** Mitigation: approve and reconcile in one PR; do
  not half-apply.
