---
description: Initialise the team roster — record human members, roles, and escalation channels in the operating profile
---

Initialise the human side of the harness. Skills supply capability; named humans
supply authority — this command records who they are.

1. If this repository has no operating profile yet, run `/join-the-team:bootstrap`
   first.
2. Ask the user for each team member, one at a time:
   - name or handle;
   - role — offer the standard set: accountable operator, product owner, data owner,
     integration owner, domain reviewer, governance/docs reviewer;
   - accountable scope (e.g. which data domain, which requirements area);
   - escalation channel (GitHub @mention, chat handle, or other).
3. Fill the profile's **Team roster and escalation** table with the answers. Keep any
   unfilled seat as an explicit `not yet established — owner: <role>; required before:
   <trigger>` placeholder — never invent a person or a scope.
4. Reconcile the profile's **Authority and approval roles** table and escalation path
   with the roster so the two agree.
5. Run `/join-the-team:validate` and report the result.
6. Remind the user: roster seats are humans, not agents; an agent may *route* a
   question to a seat but can never hold one. Insufficient evidence = lane stops and
   the seat is tagged; silence never converts to permission.
