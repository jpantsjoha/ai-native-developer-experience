# Deterministic delivery-record gates

**Spec ID:** DDG-001
**Status:** In review
**Owner:** jpantsjoha
**Depends on:** DPS-001, ADR-001

The operator requested executable lints and deterministic controls for quality,
coherence and completeness on 2026-09-26, explicitly without adding skills. This is
a bounded implementation of DPS-001 FR-8, on the existing enhancement branch.
Risk is R2: new local validation can block a candidate but grants no new authority.
Existing architecture: [planning HLD](../architecture/HLD-DELIVERY-PLANNING-SYSTEM.md)
and [ADR-001](../architecture/decisions/ADR-001-durable-planning-control-plane.md).

## Design

One standard-library Python validator reads a project-owned JSON policy containing
canonical document paths and record roots. Existing Markdown records own their IDs,
status and relationships; the policy does not duplicate work state. Specs/epics/tasks
use bold metadata fields. ADRs retain their existing title ID and Status section.
New records under configured roots are discovered automatically. Missing required
roots, unreadable documents and malformed policy fail closed.

Validate required nonempty files, unique stable IDs, closed lifecycle vocabularies,
task→epic parent references, dependencies and cycles, supersession targets, and local
Markdown file links. Done work requires local evidence links; that checks presence,
not truth, execution, reviewer identity or production readiness. Prose contradiction,
remote issue state, URL availability and heading fragments are explicitly out of scope.
Code fences/comments/single-line inline code cannot spoof record metadata or satisfy
links. Multiline/unmatched inline backticks fail explicitly; a bounded grammar must
not guess block precedence and hide visible fields.

`make planning` runs the validator. Existing `make test` invokes it so local
`make check` and the existing CI job share the gate. Expand `make typecheck` to all Python
scripts/tests in the existing source roots and syntax-check executable shell sources;
do not execute their hooks or provider commands during syntax checking. No new skill,
dependency, provider call, installed cache change or remote configuration change.

## Acceptance

- DDG-1: repository records pass; missing/empty required file or record root refuses.
- DDG-2: malformed/duplicate policy keys, invalid types and escaping paths refuse.
- DDG-3: missing/duplicate IDs, metadata hidden in examples, ambiguous metadata and
  invalid lifecycle state refuse; valid current ADR format remains supported.
- DDG-4: missing/wrong-kind parent, missing dependency, dependency cycle and invalid
  supersession refuse; no epic is imposed on a standalone spec.
- DDG-5: broken inline/reference local links refuse; external URLs remain offline;
  Done without existing nonempty local evidence refuses. Evidence existence does not
  become approval or an execution attestation.
- DDG-6: gate is reached by `make check` and existing CI's `make test`; planted invalid
  repository metadata produces a nonzero result, with structured findings available.
- DDG-7: all existing gates remain green, a fresh independent reviewer checks the exact
  candidate, and status/roadmap/changelog describe delivered checks and remaining gaps.

## Plan, limits and rollback

First write negative CLI fixtures, then implement the parser and relationship checks;
add project policy and minimal metadata corrections, wire the existing Make targets,
run focused fixtures and convergence, independently review, and commit locally.
One mutating integrator; one bounded fresh reviewer, at most two corrective rounds
before replanning. No paid model/API calls are needed. Revert this local commit to
remove the new gate; no adopter state or environment is changed.

How would I break this? Hide metadata in a fence/comment; replace an invalid state with
an empty inventory; redirect a link through a symlink; mark a task Done with a broken
receipt; or confuse structural PASS with semantic correctness. Negative fixtures,
required roots/documents, containment checks and explicitly limited output address
these cases. Self-authored receipts remain unauthenticated; trusted review/promotion
controls and full semantic reconciliation remain separate roadmap work.

## Replanning after adversarial review

Two corrective rounds exposed the cost of guessing Markdown block boundaries when
masking multiline inline-code spans. The final design removes that heuristic and
refuses unsupported spans explicitly. Existing fenced examples remain supported.
This narrows parser claims and preserves fail-closed behaviour; it adds no skill,
dependency or authority. Fresh review must assess this reduced design and its fixtures.
