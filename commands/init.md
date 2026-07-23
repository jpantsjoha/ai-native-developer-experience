---
description: Initialise the planning seed and record the human team, roles, and escalation channels
---

Initialise the project's delivery-planning records and human side of the harness. Skills
supply capability; named humans supply authority.

1. Run `/join-the-team:bootstrap` first, including its dry-run. This is safe for an
   existing adoption: matching operating files are unchanged, existing project planning
   records are preserved, and missing vision/workflow/roadmap/status/changelog files are
   seeded. Stop on a reported operating-contract or adapter conflict.
2. **If the repo already has code**, run the read-only inspection pass to pre-fill what
   the repository reveals instead of presenting a blank form:
   `python3 .agents/skills/operating-model-bootstrap/scripts/inspect_repo.py .`
   Transcribe each finding into the profile as its `inferred — source: …; confirm: …`
   marker, then confirm them one at a time with the accountable human. Never promote an
   inferred value to a verified fact without confirmation; the profile cannot go `active`
   while any inferred field remains.
3. Ground the vision and delivery workflow from verified project evidence. Leave roadmap
   outcomes and status claims unpopulated until the Product Owner validates them; never
   turn template placeholders into invented progress.
4. Ask the user for each team member, one at a time:
   - name or handle;
   - role — offer the standard set: accountable operator, product owner, data owner,
     integration owner, domain reviewer, governance/docs reviewer;
   - accountable scope (e.g. which data domain, which requirements area);
   - escalation channel (GitHub @mention, chat handle, or other).
5. Fill the profile's **Team roster and escalation** table with the answers. Keep any
   unfilled seat as an explicit `not yet established — owner: <role>; required before:
   <trigger>` placeholder — never invent a person or a scope.
6. Reconcile the profile's **Authority and approval roles** table and escalation path
   with the roster so the two agree.
7. Run `/join-the-team:validate` and report the result.
8. Remind the user: roster seats are humans, not agents; an agent may *route* a
   question to a seat but can never hold one. Insufficient evidence = lane stops and
   the seat is tagged; silence never converts to permission.
