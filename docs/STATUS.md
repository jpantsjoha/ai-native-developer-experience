# Delivery status

**As of:** 2026-10-12. **Owner:** harness maintainer.

## Current candidate

PR #28 combines the approved release-mode correction (#27) with portable independent
review and delivery-coherence guidance. Scope and acceptance are in
[HARNESS-COHERENCE](../requirements/HARNESS-COHERENCE.md) and
[RELEASE-MODE-CONTRACT](../requirements/RELEASE-MODE-CONTRACT.md).

This is an unreleased source candidate. Local validation and an independent reviewer
must bind to its exact tree/commit before merge. The PR records the final identities,
commands, results and remaining conditions; this file is not a review attestation.
No installed plugin or adopter has inherited these changes merely because they exist
on this branch. Release version, installation and promotion are separate decisions.

The repository follows its existing GEMINI.md/CLAUDE.md contract and `make check`.
The optional review helper is tested with offline fixtures; this change does not
install hooks, select a provider or claim compatibility for untested host wrappers.
Review-loop history is an owned procedure, not newly automated enforcement.

## Next action and remaining work

Finish exact-candidate validation/review, reconcile PR #28 and merge if its controls
permit. Keep the [roadmap](ROADMAP.md) and release changelog separate from this state.
Historical audit proposals beyond this slice remain proposals; measured effectiveness,
semantic traceability and cross-project adoption are not declared complete.

The operator retains release/tag/install decisions. The selected local review policy
belongs to the session/project, not the portable plugin's model roster.
