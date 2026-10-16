# ADR-003: source-only plugin release

Date: 16 October 2026. Decision owner and release authority: Jaroslav Pantsjoha.
Scope: the owner-authorised PR #33 merge and version-tag cut, conditional on passing
checks and independent review. This records that execution; it grants no standing
agent authority for later tags, installations or production promotion.

This repository publishes source, not a built service. Existing releases contain
GitHub source archives and no uploaded binaries. Continue that manual source-release
path for v0.4.0; do not invent a tag-triggered build pipeline. The optional adopting
project release-preflight profile is not installed in this maintainer repository.

Use SemVer: 0.4.0 adds compatible role/workflow capabilities to 0.3.0. Keep every
plugin manifest and the changelog aligned. Merge only the exact reviewed tree after
`make check`, independent adversarial/secret review and required GitHub checks pass.
Then verify main's tree, create an annotated `v0.4.0` tag on that main commit, and
publish a GitHub source release with the changelog entry. Retain candidate, tree and
archive digest with validation/review results in PR/release metadata, not a public
research or evidence directory. Inspect the source archive and exercise bootstrap
and validation from the extracted package before publication.

Rollback means selecting the preserved v0.3.0 source/package, not moving or deleting
published tags. Verify the previous source can still bootstrap a disposable consumer.
Existing consumer records are preserved; downgrading the package does not undo a
project's accepted contract changes. Do not overwrite installed skills automatically.
If validation, archive integrity or publication verification fails, stop publication
and retain the failure; after publication correct defects with a new reviewed version.

Observe tag-to-main identity, release visibility and source/package contents immediately
after publication. The maintainer owns follow-up install issues. There is no runtime
service, automatic paid call or production deployment in this cut; host adoption and
measured efficiency remain separate follow-up work.
