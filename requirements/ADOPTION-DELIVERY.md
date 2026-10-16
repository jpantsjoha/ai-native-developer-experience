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


## Accepted extension: golden-thread delivery (16 October 2026)

JP explicitly requested this extension; scope remains issue #32 / PR #33. The public
contract captures the operational requirements, not the private source conversation.

| ID | Requirement | Verification |
| --- | --- | --- |
| ADP-01 | Identical lean root adapters and compact default hook for adopted/unadopted projects | Adapter parity and executed hook mode tests |
| ADP-02 | Product/vision ownership, material CXO oversight and acceptance-driven test strategy | Discoverable skills, packaging checks and independent scenario review |
| ADP-03 | Stable requirement identity, changed decisions/journeys, owned/sized GitHub tickets and in-flight checks | Portable workflow, issue template and independent scenario review |
| ADP-04 | Completion traces to accepted requirement; source merge, release and observation stay distinct | Workflow and delivery-record review |
| ADP-05 | Reconcile records and safely clean only integrated owned lanes | Cleanup procedure review including squash merge and dirty-worktree scenarios |

Reuse the existing installed DELIVERY-WORKFLOW asset as the detailed portable contract;
root adapters route to it through delivery-orchestrator. Three narrowly scoped skills
supply missing role capabilities. Default hooks emit a pointer; full content is opt-in.
No tracker daemon, automatic semantic coverage validator or global installation change
is included. The broader DPS planning validator remains separate work.

Validation: full local convergence, then one fresh independent Codex review and at most
one repair review for this extension. Review must exercise an evolving requirement,
a duplicate active lane and a partial delivery, plus secret inspection of the added diff.


## Authorised close-out and source release (16 October 2026)

The owner extended scope to the useful advisory clarifications, fresh checks/review,
merge of PR #33, branch cleanup and a new version tag. This supersedes the earlier
no-release boundary for this cut only. Clarify unadopted starting steps, optional hooks,
planning versus test execution, and affected-record-only reconciliation. Prepare v0.4.0
under ADR-003; verify source archive/bootstrap and rollback before publishing. One fresh
Codex review and at most one repair review cover the final clarification/release tree.
