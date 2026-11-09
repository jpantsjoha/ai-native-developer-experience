# ADR-005: Backward-compatible DevEx Charter naming

## Status

Accepted — 2026-11-09. Decision owner: JP (operator instructions, 9 November 2026:
keep the legacy name `join-the-team` so existing installs and listings stay valid;
use `devex-charter` going forward). Extends [ADR-004](ADR-004-devex-charter.md).

## Context

ADR-004 renamed the plugin to `devex-charter` in v0.5.0 and kept the marketplace
`join-the-team-marketplace`. Every install command published before v0.5.0 used
`join-the-team@join-the-team-marketplace`, and stopped resolving. Directories inherited
it: ClaudePluginHub's install test ran that command on 6 November 2026 and failed on
Linux, macOS and Windows. Renaming the marketplace too was tried on the candidate and
reversed: it would have broken the v0.5.0 command as well and forced every listing to
be edited.

## Decision

From v0.6.0:

- `devex-charter` is the plugin name for all new installs, docs and listings.
- The Claude marketplace keeps the identifier `join-the-team-marketplace`.
- The marketplace lists `join-the-team` as a legacy alias: a second entry with the same
  source and version. `join-the-team@join-the-team-marketplace` installs the same plugin.
  Verified on 9 November 2026 in a scratch Claude config: both names install 0.6.0 with
  the skills and session-start hook.
- `scripts/validate_plugin.py` accepts only aliases named in `LEGACY_ALIASES` that share
  the primary entry's source and version; anything else fails the packaging gate.
- The orientation variable is `DEVEX_CHARTER_ORIENTATION`; the hook still reads
  `JOIN_THE_TEAM_ORIENTATION` when the new variable is unset.
- The repository name stays `ai-native-developer-experience`. Historical records keep
  the name they were written under.

## Consequences

- Published `join-the-team` commands, directory listings and articles keep working
  without edits; they can be updated to `devex-charter` at leisure.
- Installing both names gives two copies of the hooks and skills. Docs say: install
  one. The alias's description says the same.
- Under the alias, commands are namespaced `/join-the-team:*`; under the new name,
  `/devex-charter:*`.

How would I break this? Let the alias drift to an older version or a different source,
so the old command installs something else. Mitigation: the validator rejects it, and
a test proves the rejection.
