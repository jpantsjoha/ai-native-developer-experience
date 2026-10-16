# Adoption from installation to delivery

Issue: #32. Owner: harness maintainer. Date: 16 October 2026.
Scope: user-authorised adoption improvements; no release or global configuration writes.

## Outcome and design

A builder or team installs the reusable skills at project or user scope, then establishes
project-owned vision, practices, tickets, model choices, tests and route to live. Global
installation makes capabilities available; it does not grant authority across projects.

Reuse the existing initializer, inspector, validator and host adapters. Claude plugin
commands resolve scripts through the host-substituted package root. Other hosts resolve
scripts relative to the discovered bootstrap skill. The target directory stays explicit
and separate from the installed package. Generated adapters route through the project
profile instead of assuming skills were copied locally. No new dispatcher or installer.

## Acceptance and plan

1. Repair commands, skill instructions and initializer follow-up commands for external
   installations, including paths with spaces and consumer working directories.
2. Prove dry-run, bootstrap, inspection, validation, rerun, preservation on conflict and
   no writes to the source package for copied-skill and external-package layouts.
3. Explain project/user installation and team adoption with one delivery sequence from
   accepted intent through tickets, model choice, implementation, review and live checks.
4. Reconcile README, bootstrap, current vision/status/roadmap and Unreleased changelog.
   Keep product behaviour separate from release/install state and unmeasured benefits.
5. Run `make check` and a fresh read-only Codex implementation/editorial review on the
   exact tree. One initial review and one repair review within this slice; repeated
   substantive failures require narrowing the work before further dispatch.

## Failure modes and rollback

Wrong working directory could write into the plugin cache; missing assets could break
bootstrap; copying maintainer adapters could import authority; competing installations
could load different guidance. Tests exercise separate directories and existing-file
conflicts. Instructions require the selected installation and explicit consumer target.
Project controls remain authoritative; installation does not authorise publication or
production. Revert this change to restore the prior commands/docs. Existing adopter
files remain untouched; upgrading their protected adapters requires deliberate adoption.

## Verification boundaries

Local fixtures prove script behaviour and documented path substitution. They do not
prove every live host UI, enterprise adoption, delivery speed or financial savings.
Host scope/path documentation checked 16 October 2026:
[Claude plugin scopes](https://code.claude.com/docs/en/discover-plugins#choose-an-install-scope),
[Claude package substitution](https://code.claude.com/docs/en/plugins-reference#environment-variables),
[Codex skill locations](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).
