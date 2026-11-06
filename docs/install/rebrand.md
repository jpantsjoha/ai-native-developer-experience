# Migrating to DevEx Charter

Tracking: [#34](https://github.com/jpantsjoha/ai-native-developer-experience/issues/34).
This is an **unreleased source candidate**, not an installed global update.

| Surface | Decision |
| --- | --- |
| Product / plugin display name | DevEx Charter |
| Plugin and command namespace | `devex-charter` |
| GitHub repository | `jpantsjoha/ai-native-developer-experience` (unchanged) |
| Claude marketplace identifier | `join-the-team-marketplace` (retained) |
| Orientation configuration | `JOIN_THE_TEAM_ORIENTATION` (retained) |
| DevDash | Unchanged companion project |

## Operator migration after a reviewed release

1. Record the installed version, scope, source and enabled settings. Preserve project
   contracts and customised skills. Keep the previous v0.4.0 source for rollback.
2. Obtain the reviewed renamed release through the host's supported marketplace/source
   flow. Disable the old `join-the-team` plugin in the same scope before enabling the
   new one; do not run two copies of its hooks or skills. Updating the old slug is not
   a supported alias migration. Do not edit generated host caches by hand.
3. For Claude, refresh the retained marketplace and install
   `devex-charter@join-the-team-marketplace` in the intended scope. Use
   `/devex-charter:bootstrap`, `/devex-charter:init` and `/devex-charter:validate`.
   Preserve existing project records. In Codex/Kimi/Gemini use the supported host
   installation flow and inspect the discovered source paths; commands vary by host.
4. Reload the host. Verify one skill set and one orientation hook where supported.
   Exercise bootstrap, initialise and validation in a disposable consumer, then check
   an existing adopted project for preservation. Test both fresh and migrated installs.
5. If a host cannot load the renamed package, disable it and restore the previous
   installation/settings from step 1. A package rollback does not reverse accepted
   project changes. Keep one active source throughout rollback.

Live host migration is not yet verified. Packaging fixtures prove source consistency
and consumer-script behaviour, not marketplace refresh or installed cache behaviour.
The release owner must record fresh-install, upgrade, duplicate-discovery and rollback
results on each supported host before advertising the migration as supported.

## Upstream references

The existing [Agent Plugins Directory listing](https://agent-plugins.directory/jpantsjoha/join-the-team)
is a legacy URL; retain it until the directory confirms its replacement or redirect.
Do not substitute an assumed `devex-charter` URL.

The installed Claude marketplace README identifies the upstream as
[Claude Plugin Hub](https://www.claudepluginhub.com/plugins/jpantsjoha-join-the-team).
The existing page returned HTTP 200 and links to this source repository. This is a
directory listing; a separate editable registry repository has not been established.
Its follow-up payload is: display name **DevEx Charter**, plugin slug `devex-charter`,
unchanged source repository and marketplace identifier, plus the new release version
once cut. Confirm the directory's supported owner-update process before submitting; follow
[submission policy](../PLUGIN-SUBMISSION.md) for any external submission.
No upstream listing, installed global cache or third-party repository has been updated
by this source change. Old issue titles and release records remain historical evidence.

The locally installed official Claude marketplace README describes a top-level
`renames` map for slug migration. Treat this as a candidate host-specific mechanism:
verify current host support and upgrade/rollback behaviour before enabling it here.
No automatic migration mapping is included in this source candidate.
