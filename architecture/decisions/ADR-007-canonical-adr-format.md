# ADR-007: Canonical ADR format and macOS Python 3.9 compatibility floor

## Status

Proposed — 2026-11-25. Decision owner: JP (`@jpantsjoha`).

## Context

Two contradictions existed between the repository's documentation, skills, and executable gates:

1. **ADR format drift (`0.1.6` vs. `DDG-001`):** Release `0.1.6` (2026-07-23) updated `the-architect` and `operating-model-bootstrap` to teach `ADR/ADR-NNNN-<slug>-DRAFT.md` → `-approved.md` with YAML frontmatter and lowercase `draft | approved | superseded` statuses. Later, `scripts/validate_delivery.py` (`DDG-001`, shipped in `v0.6.0`) enforced `architecture/decisions/ADR-NNN-<slug>.md` with `# ADR-NNN: Title` and `## Status` values in `{Proposed, Accepted, Rejected, Superseded}`—matching all existing ADRs (`ADR-001` through `ADR-006`) in this repository. As a result, any adopter following `the-architect` produced ADRs that failed `make planning`.
2. **Python floor on stock macOS:** `BOOTSTRAP.md` declared Python `3.10+`, CI ran only Python `3.11`, and `validate_operating_model.py` used `zip(..., strict=False)` (a Python 3.10+ runtime keyword argument, even though `strict=False` is the default). Stock macOS Command Line Tools still ship `/usr/bin/python3` at Python `3.9.6`, causing `make test` to fail at runtime with `TypeError` on a fresh macOS checkout despite `make typecheck` (`py_compile`) passing.

## Decision

1. **Reverse the `0.1.6` ADR skill convention to match `validate_delivery.py` and `docs/DETERMINISTIC-GATES.md`:**
   - Canonical path: `architecture/decisions/ADR-NNN-<slug>.md` (or the project's mapped `"decision"` root in `.delivery.json`).
   - Canonical grammar: `# ADR-NNN: <short title>` with a `## Status` section whose first non-blank line begins with `Proposed`, `Accepted`, `Rejected`, or `Superseded` (with `**Superseded by:** ADR-MMM` when superseded).
   - Adopters already using `ADR/` from `0.1.6` may keep that directory by mapping `"decision": "ADR"` in `.delivery.json`, **and must update every tracked ADR's `## Status` value (`draft` → `Proposed`, `approved` → `Accepted`, `superseded` → `Superseded` with `**Superseded by:** ADR-MMM`) before enabling `validate_delivery.py`**, because the validator checks every `*.md` file under the mapped decision root. Legacy YAML frontmatter and `-DRAFT`/`-approved` filename suffixes do not fail `validate_delivery.py` and may be removed separately (removing stale frontmatter `status:` is recommended so human-visible status lines do not conflict).
   - `tests/test_delivery_validation.py` extracts and validates the documented template from `skills/the-architect/SKILL.md` so skill guidance and validator grammar cannot drift again.
2. **Support Python `3.9+` as the practical runtime floor for stdlib scripts, backed by CI:**
   - Although upstream Python 3.9 reached end of life in October 2025, macOS Command Line Tools still ship Python `3.9.6` as default `/usr/bin/python3`.
   - Remove the unnecessary `strict=False` keyword in `validate_operating_model.py`, align `BOOTSTRAP.md` and `antigravity-tools.md` to `Python 3.9+`, and add a dedicated `operating-model-py39` job in `.github/workflows/dx-validation.yml` (preserving the existing `Operating Model Contract` Python 3.11 check name) so runtime 3.9 compatibility is exercised in CI rather than assumed from `py_compile`.

## Alternatives considered

- **Keep the `0.1.6` `ADR/` + `-DRAFT`/`-approved` convention and rewrite `validate_delivery.py` and `ADR-001`..`ADR-006`:** Rejected. All six repository ADRs, `docs/WORKFLOW.md`, `docs/DETERMINISTIC-GATES.md`, and `spec-first-delivery` already use `architecture/decisions/ADR-NNN-*.md` and `## Status`.
- **Keep `Python 3.10+` and fail closed on Python 3.9:** Considered. Reasonable once macOS ships 3.10+, but right now breaking out-of-the-box macOS `/usr/bin/python3` for a single redundant `strict=False` parameter adds adopter friction with zero benefit. Revisit when Apple updates Xcode CLT Python or GitHub Actions drops `setup-python` 3.9.

## Consequences

- One canonical ADR convention across skills, docs, repository decisions, and `make planning`, guarded by automated template and negative drift tests.
- Adopters who followed `0.1.6` have an explicit, tested migration path before enabling `make planning`.
- Stdlib scripts remain runnable on stock macOS Python 3.9.6 and verified in CI on both Python 3.9 and 3.11; contributors must avoid 3.10+ runtime-only stdlib APIs until this ADR is superseded.
