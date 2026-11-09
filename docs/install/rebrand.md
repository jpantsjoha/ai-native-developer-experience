# Migrating to DevEx Charter

Tracking: [#34](https://github.com/jpantsjoha/ai-native-developer-experience/issues/34).
The plugin was renamed in [v0.5.0](https://github.com/jpantsjoha/ai-native-developer-experience/releases/tag/v0.5.0);
v0.6.0 makes the rename backward compatible ([ADR-005](../../architecture/decisions/ADR-005-complete-devex-charter-rename.md)).

| Surface | Use from v0.6.0 | Still works |
| --- | --- | --- |
| Product / plugin display name | DevEx Charter | Join the Team (historical) |
| Plugin and command namespace | `devex-charter`, `/devex-charter:*` | `join-the-team`, `/join-the-team:*` (legacy alias of the same plugin) |
| Claude marketplace identifier | `join-the-team-marketplace` (unchanged) | — |
| Orientation configuration | `DEVEX_CHARTER_ORIENTATION` | `JOIN_THE_TEAM_ORIENTATION` (read when the new variable is unset) |
| GitHub repository | `jpantsjoha/ai-native-developer-experience` (unchanged) | — |

## Install

```bash
claude plugin marketplace add jpantsjoha/ai-native-developer-experience
claude plugin install devex-charter@join-the-team-marketplace --scope user
```

`join-the-team@join-the-team-marketplace` installs the same plugin under its old name.
Install one name, not both: two names mean two copies of the hooks and skills.

## If `devex-charter` is "not found"

`claude plugin marketplace add` does not refresh a marketplace that is already on disk.
An install made before v0.5.0 holds an old copy that lists only `join-the-team`. Refresh it:

```bash
claude plugin marketplace update join-the-team-marketplace
```

## Moving an existing install to the new name

1. Record the installed plugin, version and scope for every scope: `claude plugin list`
   and `~/.claude/plugins/installed_plugins.json`.
2. Drop dead project-scope registrations first. The hygiene report lists them:
   `python3 <plugin-root>/scripts/lane_hygiene.py --root <git-repo> --installed-plugins ~/.claude/plugins/installed_plugins.json`.
3. Refresh the marketplace (above), then in each live scope uninstall
   `join-the-team@join-the-team-marketplace` and install
   `devex-charter@join-the-team-marketplace` in the same scope.
4. Rename `JOIN_THE_TEAM_ORIENTATION` to `DEVEX_CHARTER_ORIENTATION` where you set it.
5. Reload the host. Verify one skill set and one orientation hook, and run
   `/devex-charter:validate` in an adopted project.
6. Rollback: uninstall `devex-charter` and reinstall `join-the-team` in the same scope.

Staying on `join-the-team` is supported; moving is optional. Kimi, Codex and Antigravity
install from the repository URL and are unaffected by the Claude marketplace.

## Adopted projects and the operating manual

v0.6.0 ships operating manual 2.2.0. A project adopted at 2.1.0 pins its own copy by
version and SHA-256, so upgrading the plugin does not fail its validation. Re-adopting
2.2.0 is a deliberate project change: replace the manual, update the profile's
**Manual version** and **Manual SHA-256**, and re-run `/devex-charter:validate`.
Bootstrap refuses to overwrite a different existing manual; that refusal is the guard.
