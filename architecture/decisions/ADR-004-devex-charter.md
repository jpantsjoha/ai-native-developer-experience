# ADR-004: DevEx Charter identity and staged migration

## Status

Accepted — 2026-11-05


Decision owner: JP. Accepted name: **DevEx Charter**. Work item:
[#34](https://github.com/jpantsjoha/ai-native-developer-experience/issues/34).

DevEx Charter establishes the shared delivery contract for human–AI teams. DevDash
makes delivery state and evidence visible. The plugin remains useful independently.
The repository stays `ai-native-developer-experience`, preserving source and release
links. The canonical plugin slug becomes `devex-charter` in every host projection;
Kimi's display name becomes DevEx Charter. No runtime functionality is added.

Keep `join-the-team-marketplace` as the marketplace identity and
`JOIN_THE_TEAM_ORIENTATION` as the existing configuration interface. Neither is a
plugin alias. Renaming those interfaces too would add migration work without improving
the public product name. Historical releases, screenshots and pinned eval evidence
retain their provenance. Do not invent redirects or dual installation compatibility.

Manifest versions remain 0.4.0 while this is an unreleased source change. Before
publication select a new aligned version, at least 0.5.0 for the pre-1.0 identifier
break, and complete the host migration gates in the [guide](../../docs/install/rebrand.md).
Never publish different identities under the existing v0.4.0 tag.

Status, 6 November 2026: merged in PR #35 and released as v0.5.0. Host migration
and upstream listing gates remain open.

Acceptance: all manifests agree; active command references use the new slug; README,
changelog and migration guidance agree; local `make check` and fresh read-only Council
review pass. Live host upgrades and upstream listing publication are separate gates.

How would I break this? Load both plugins and duplicate hooks, update the old slug
and assume it becomes the new one, or advertise a nonexistent directory URL. Mitigate
with one active installation, explicit migration, preserved rollback and verified
external links. Source packaging tests cannot prove host cache/update behaviour.
