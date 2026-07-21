---
description: Initialise the planning seed and record the human team, roles, and escalation channels
---

Initialise the project's delivery-planning records and human side of the harness. Skills
supply capability; named humans supply authority.

1. Run `/join-the-team:bootstrap` first, including its dry-run. This is safe for an
   existing adoption: matching operating files are unchanged, existing project planning
   records are preserved, and missing vision/workflow/roadmap/status/changelog files are
   seeded. Stop on a reported operating-contract or adapter conflict.
2. Ground the vision and delivery workflow from verified project evidence. Leave roadmap
   outcomes and status claims unpopulated until the Product Owner validates them; never
   turn template placeholders into invented progress.
3. Ask the user for each team member, one at a time:
   - name or handle;
   - role — offer the standard set: accountable operator, product owner, data owner,
     integration owner, domain reviewer, governance/docs reviewer;
   - accountable scope (e.g. which data domain, which requirements area);
   - escalation channel (GitHub @mention, chat handle, or other).
4. Fill the profile's **Team roster and escalation** table with the answers. Keep any
   unfilled seat as an explicit `not yet established — owner: <role>; required before:
   <trigger>` placeholder — never invent a person or a scope.
5. Reconcile the profile's **Authority and approval roles** table and escalation path
   with the roster so the two agree.
6. Run `/join-the-team:validate` and report the result.
7. Remind the user: roster seats are humans, not agents; an agent may *route* a
   question to a seat but can never hold one. Insufficient evidence = lane stops and
   the seat is tagged; silence never converts to permission.
