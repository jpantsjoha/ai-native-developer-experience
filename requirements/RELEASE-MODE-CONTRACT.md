# Release mode contract — issue 27

**Status:** implementation approved by JP, 2026-10-02 (issue 27 proposal).
**Risk:** R2; changes portable guidance and an offline validator, not an adopter's policy.
**Owner:** harness maintainer. **Scope:** existing skills and operating-model validator.

## Outcome and design

Respect each project's approved delivery mode while keeping candidate, artifact,
review, rollback and observation evidence mandatory. This supports the coherent,
portable delivery objective in [VISION](../docs/VISION.md).

Use six explicit fields in the existing project profile: release mode, build trigger,
build executor, promotion trigger, release owner and release decision. Modes are
`tag-ci` and `approved-alternative`. The latter requires the same evidence, and a
human must check that its decision record authorises the alternative. No mode grants
authority by itself. The immutable operating manual remains unchanged.

Extend the existing validator with `--release-evidence FILE --candidate ID`. This
release-preflight path requires an active profile, compares the declared policy with
one JSON evidence record, validates candidate/artifact identities, and checks that
local evidence references exist and are nonempty within the project. It does not run
commands, fetch links, authenticate approvals or determine semantic adequacy. Normal
seed/profile validation remains compatible; it is not a release check. The profile
must name this additional gate in the adopter's release command before enforcement
can be claimed. Existing adopters are not modified or silently opted in.

## Acceptance and implementation sequence

1. Reconcile release-manager, github-manager and release-readiness around the declared
   mode. A tag is not deployment authority; an approved alternative is not a bypass.
2. Add CLI regressions, observe failure on the baseline, then extend the existing
   validator and profile template; document the evidence format with a worked example.
3. Prove default and approved-alternative paths; reject missing/duplicate/unknown mode,
   contradictory trigger/executor declarations, stale policy/candidate, conditional
   review, missing/empty/out-of-project receipts and malformed JSON. Evidence paths
   cannot substitute for human verification of their contents.
4. Run all repository gates and obtain independent review of the exact candidate.
   Commit the reviewed change and publish a PR linked to issue 27. Merge, release,
   installation, remote enforcement and the private scanner proposal are out of scope.

## Adversarial check and rollback

How would I break this? Supply self-authored receipts, stale evidence, misleading PASS
text or a symlink outside the project. Structural checks must reject detectable drift
and invalid references; the human reviewer still authenticates authority, tests and
artifact provenance. A successful structural check must never be called release
approval. Review and runtime observation remain separate gates.

No provider calls or new dependencies are required. Revert this implementation if its
checks admit weaker declarations, retaining the project's existing release controls.
No time or cost savings are claimed. This is a narrow implementation design within
issue 27, not approval of a new release strategy for this repository or its adopters.
