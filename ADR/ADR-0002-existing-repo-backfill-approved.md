---
status: approved
id: ADR-0002
date: 2026-07-23
approved: 2026-07-23
deciders: [jpantsjoha]
implements: H-013
---

# ADR-0002: Existing-repo requirement backfill

## Status

**approved** — the design and approach are approved and codified here. Implementation is
the next tranche (targeted v0.1.7); no behaviour changes until it ships behind this ADR.
Filed per the convention in [ADR-0001](ADR-0001-adr-convention-approved.md).

## Context

The harness's value is dropping into *existing* work, but `init` assumes a greenfield team
answering a seven-area questionnaire from scratch. Adopting into a mature repo yields an
empty operating profile → the user churns, abandons, or defers. Two failure paths: the
user skips `init` entirely, or faces a blank seven-area form and half-fills it.

## Decision

Build **existing-repo requirement backfill**:

- On adoption into a non-empty repo, a **read-only** inspection pass pre-fills the
  seven-area profile with **inferred** values, each carrying a mandatory evidence pointer.
- Provenance is three-state, made scannable with visual markers:

  | Marker | State | Meaning | Accountability |
  |---|---|---|---|
  | 🤖 | `inferred` | model backfilled from repo evidence | not yet owned — needs review |
  | ✅ | `verified` | a named human reviewed and confirmed | carries handle + date |
  | ⬜ | `unknown` | genuinely open | owner + resolving trigger |

- **`verified` is never anonymous** — it records who confirmed it and when. That is the
  accountability trail: if an inferred value was wrong, the record shows who approved it.
- The `seed` → `active` promotion gate **blocks** while any field is still `inferred`, so
  unreviewed inference can never masquerade as owned fact, and rubber-stamping is a
  deliberate, attributed act rather than a silent default.

## Consequences

Implementation (next tranche, spec-first):

- A read-only repo-inspection pass in the initializer emitting inferred values + evidence.
- A profile provenance schema (`verified` / `inferred` / `unknown` with evidence, confirm,
  owner, trigger sub-fields).
- The validator learns the `inferred` state and fails `--require-active` on any
  unconfirmed inferred field; a fixture-repo regression test.
- `operating-model-bootstrap` gains a "ground from existing repo evidence" step; `init`
  runs backfill before the human interview, then presents the pre-filled profile for
  deliberate, per-field confirmation.

## Adversarial gate — how would I break this?

- **Trust inversion / rubber-stamping.** Inferred fields *look* answered. Mitigation:
  unskippable per-field review; active-gate blocks on any 🤖.
- **Over-confident inference.** A dependency is not the architecture. Keep confidence low;
  evidence pointer mandatory.
- **Hallucinated authority.** Never infer R2/R3 authority, roles, or DoD acceptance;
  `CODEOWNERS` may seed candidate names but accountability stays `unknown` until confirmed.
- **Vendor lock-in.** Inference rules stay vendor-neutral; the evidence set is extensible.
- **Scope creep.** Backfill is read-only — it proposes profile values, never writes code
  or config.
