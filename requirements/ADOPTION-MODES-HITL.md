# Adoption modes and the human-in-the-loop queue

**Spec ID:** AMH-001

**Status:** Accepted

Drafted 20 November 2026 from the Product Owner's direction of the same date and
accepted by the Product Owner that day. FR-6 is built; the rest is not.

**Product Owner:** Jaroslav Pantsjoha (`@jpantsjoha`)

**Planning owner:** `delivery-orchestrator` capability

**Related vision:** [`docs/VISION.md`](../docs/VISION.md)
**Proposed architecture decision:**
[`ADR-006`](../architecture/decisions/ADR-006-adoption-modes-and-hitl-queue.md)

## Problem

The harness is used in two ways and describes neither. One person runs a whole project
with it; a team of accountable leads shares it across one repository. The documents do
not say what stays the same between the two or what changes.

Four gaps follow from that:

- **No personal queue.** `STATUS.md` records what waits on whom, but a person has no
  working list of the decisions and actions an agent is waiting on, or what each one
  unblocks. Projects have invented their own files in different formats.
- **No maintainer for a specialist skill.** The roster names who owns requirements, data
  and integration. It does not name who keeps a specialist skill current.
- **Skills can be used in isolation.** Nothing says when a specialist skill may be called
  directly and when the work must go through the orchestrator.
- **Outside context is ungoverned.** A lead may ground an agent in meeting notes, chat or
  a personal folder. Nothing requires that context to be checked against the project
  before it changes scope.

## Users and actors

- **Solo owner:** one person who holds every role and decides everything.
- **Accountable lead (team):** the named person for a domain, such as engineering, data,
  QA or SRE, who directs agents in that domain.
- **Director or programme lead:** adds scope and judges outcomes across leads.
- **Delivery orchestrator (capability):** plans, routes and maintains the queue.

## Functional requirements

### FR-1: Two adoption modes, one workflow

The operating profile records an adoption mode, `solo` or `team`. The workflow, gates,
risk tiers, delivery records and release cadence are identical in both. The mode changes
only who holds each decision and which queue file is used.

- **Solo:** the profile owner holds every roster role.
- **Team:** each roster role names a person. A role with no person is an open question
  with an owner and a trigger, as the profile already requires.

A project moves from solo to team by naming people in the roster and re-running
bootstrap; no record is rewritten.

### FR-2: A local queue for each person

Each person has one queue file in the project, listing what waits on them.

| Mode | Path |
| --- | --- |
| Solo | `HITL/OPERATOR/Master-TODO.md` |
| Team | `HITL/OPERATOR/<gh-id>-TODO.md`, one for each person |

- `HITL/OPERATOR/` is git-ignored. Only `HITL/OPERATOR/README.md`, which explains the
  folder and the row format, is committed.
- The queue is never committed and never read from, or written to, another person's
  machine.
- `<gh-id>` is the person's GitHub login. Bootstrap proposes it from the signed-in GitHub
  account and the person confirms it before any file is created.
- **Solo to team.** Bootstrap proposes renaming `Master-TODO.md` to the owner's
  `<gh-id>-TODO.md` and does it only on confirmation. If the destination already exists
  it changes nothing and reports both files.
- **Existing lists.** A project's earlier operator to-do file is migrated only by an
  explicit command that names the source file. Open items are copied to the queue after
  confirmation; the source file is never deleted or edited by the command.

### FR-3: One row format

The queue file holds one Markdown table with exactly these columns, in this order.

| Column | Content | Empty value |
| --- | --- | --- |
| Item | The decision, action or observation asked of the person | not allowed |
| Type | `decision`, `action` or `observation` | not allowed |
| Role | The roster role it is asked of | not allowed |
| Ref | The escalation issue (`#123`) under FR-5; `local` for an item only this person needs; or `pending` for an escalation not yet filed because the tracker was unavailable | not allowed |
| Unblocks | Issues and milestone that wait on it, such as `#12, #14; M3` | `-` |
| Cost if wrong | What a bad or late answer costs | `-` |
| Reversibility | `cheap`, `costly` or `one-way` | not allowed |
| Recommendation | The agent's recommended answer | `-` |
| Raised | Date added, `YYYY-MM-DD` | not allowed |
| Due | An absolute date, `YYYY-MM-DD`. A request for "end of day" or "end of week" is written as that date | `-` |
| Record | Where the answer will be recorded: an issue (`#123`), an ADR (`ADR-006`) or `STATUS` | not allowed |

The queue holds open items only. A row is removed when:

- `Ref` is an issue: the answer is recorded and that issue is closed;
- `Ref` is `local`: the answer is recorded where the Record column says;
- `Ref` is `pending`: never directly. It first becomes an issue under FR-5.

A conforming file looks like this:

```markdown
| Item | Type | Role | Ref | Unblocks | Cost if wrong | Reversibility | Recommendation | Raised | Due | Record |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Choose the retention period for audit logs | decision | data owner | #41 | #38, #40; M2 | Rework of the store schema | costly | 90 days | 2026-11-20 | 2026-11-22 | ADR-007 |
| Run the signing step on the release machine | action | operator | local | - | - | cheap | - | 2026-11-20 | - | STATUS |
```

The validator accepts a file that matches this table and rejects one that does not.

### FR-4: The boundary with STATUS

`STATUS.md` stays the shared, durable record of what waits on whom. The queue is the
personal working list and may change many times a day.

- The queue never replaces a delivery record, and no gate reads it as evidence.
- An answer counts only when it is recorded in the issue, the ADR or `STATUS.md`.
- A blocker that holds a milestone, or that another person must act on, is shared at once
  through an escalation issue (FR-5). It does not wait for a merge.
- The records task copies open milestone blockers into `STATUS.md`. It runs after each
  merge batch, as now, and also at session close whenever a milestone blocker is open and
  not yet in `STATUS.md`, whether or not anything merged earlier in the session. This
  second trigger is an addition to the reconciliation rule in `docs/DELIVERY-RECORDS.md`
  and changes that document when this specification is built.

### FR-5: Escalation and queue maintenance

A person's queue is local, so one person's agent cannot write another person's queue. The
shared channel is the project's tracker.

- **Raising.** When work halts on a human, the agent finds the accountable role in the
  roster for that domain and opens an escalation issue in the project's mapped tracker,
  assigned to the person in that role and labelled `needs-human`. The issue carries the
  FR-3 fields. In solo mode the assignee is the profile owner. An item that only the
  current person needs, such as a step on their own machine, is written to their queue
  with `Ref` set to `local` and needs no issue.
- **Notifying.** The roster's escalation channel for that role is used to tell the person,
  as the profile already requires. The agent does not create or edit a queue file for
  anyone but the current person.
- **Collecting.** At session start and on request, `delivery-orchestrator`, `sitrep` and
  `wrap-it-up` list open `needs-human` issues assigned to the current person and add any
  that are missing to that person's queue.
- **Clearing.** Rows are removed under the FR-3 conditions. An escalation whose answer
  is recorded but whose issue is still open stays in the queue until the issue is closed.
- **Tracker unavailable.** If the agent cannot open the issue, it states the escalation
  in the session, writes a row to the current person's queue with `Ref` set to `pending`,
  and names the accountable person to tell through the roster's escalation channel. The
  current person owns the pending row. At the next session in which the tracker is
  reachable, the skill opens the escalation issue and replaces `pending` with its number.
- **Digest.** On request the skill prints the open rows, oldest `Raised` first, with what
  each unblocks.

An agent never answers a row or closes an escalation issue on the person's behalf, and
silence is never permission.

### FR-6: Delivery work goes through the orchestrator

Work that changes scope, design, code, configuration or a delivery record enters through
`delivery-orchestrator`, which works with `product-owner` against the project vision
before it routes to a specialist skill.

A specialist skill may still be called directly for a bounded question that changes
nothing, such as advice or a read-only review. When such a call turns into a change, the
skill hands the work to the orchestrator before continuing.

The routing table in `using-the-harness` and the entry conditions in
`delivery-orchestrator` are rewritten to say the same thing, so the three places agree.

### FR-7: A named maintainer for a specialist skill

The roster may name a maintainer for a specialist skill. The maintainer approves changes
to that skill's procedure and keeps it current. A skill with no named maintainer is
maintained by the profile owner.

Maintaining a skill gives no decision authority. When a skill halts on a product, data,
architecture or release question, the question goes to the accountable roster role for
that domain under FR-5, and the profile's existing approval roles are unchanged. A
maintainer cannot change the shared workflow, gates or records alone.

### FR-8: Outside context is checked and recorded

Agents may use context from outside the repository, such as meeting notes, chat, shared
documents or a personal folder.

- Context that would change scope, design or acceptance is checked against
  `docs/VISION.md` and the accepted requirements first. If it conflicts, the agent stops
  and raises it to the Product Owner under FR-5.
- It can justify a change only once it is recorded with its source and date in one of two
  places: the repository, as a requirement or an ADR; or the project's mapped tracker, as
  a comment on the issue it affects.
- Unrecorded outside context is personal context. It may inform a question; it may not
  justify a change.
- Private material is summarised, not copied, and credentials are never recorded.

The adapter templates (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) carry this rule in the same
words.

## Out of scope

- The outcome contract (the declared success metric): its own specification.
- A team-wide view of every person's queue. Each queue stays local by design.
- Any tool that reads the queue; a dashboard may read the local file on its own machine.
- Hook enforcement of FR-6: its own issue.
- Sending notifications: the roster's existing escalation channel is used as it is.

## Acceptance criteria

Structure:

1. Bootstrap in solo mode creates `HITL/OPERATOR/Master-TODO.md` and the committed
   README and adds the ignore rule; in team mode it creates `<gh-id>-TODO.md` only after
   the person confirms the login (FR-1, FR-2).
2. A second bootstrap run overwrites nothing (FR-2).
3. Solo to team: with confirmation, `Master-TODO.md` becomes `<gh-id>-TODO.md`; when the
   destination exists, nothing changes and both files are reported (FR-2).
4. The migration command copies open items from a named source file after confirmation
   and leaves the source byte-identical (FR-2).
5. `git check-ignore` reports every queue file as ignored; the validator fails if one is
   tracked (FR-2).
6. The validator accepts the conforming example in FR-3 and rejects each of: a missing column, a
   reordered column, an unknown Type or Reversibility, a date not in `YYYY-MM-DD`, and an
   empty value where none is allowed (FR-3).
7. The roster template has a skill-maintainer column and the profile an adoption-mode
   field; a skill with no maintainer resolves to the profile owner (FR-1, FR-7).
8. The three adapter templates carry the FR-8 rule in identical words; the existing
   drift check covers it (FR-8).
9. `make check` passes.

Behaviour, each shown by a worked scenario kept with the tests:

- **S1 Halt on another lead.** Work halts on a data question in team mode. An escalation
  issue is opened, assigned to the roster's data owner and labelled `needs-human`; no
  queue file other than the current person's is created or changed (FR-5).
- **S2 Collect.** The data owner starts a session; the open issue appears as a row in their
  queue with its `Ref` (FR-5).
- **S3 Clear.** The answer is recorded and the issue closed; the row is removed. With the
  answer recorded and the issue still open, the row stays. An agent asked to answer or
  close it on the person's behalf refuses (FR-3, FR-5).
- **S4 Blocker with no later merge.** A milestone blocker is raised, in one case with no
  merge in the session and in another after the session's last merge batch was
  reconciled. In both, the records task at session close writes the blocker to
  `STATUS.md`, and the escalation issue was visible from the moment it was raised (FR-4).
- **S5 Queue is not evidence.** A gate given a queue row marked as answered, with no
  recorded answer, does not treat it as approval (FR-4).
- **S6 Direct call turns into a change.** A specialist skill asked a read-only question
  answers it; asked to change code, it hands over to `delivery-orchestrator`, which
  consults `product-owner` first. `using-the-harness`, `delivery-orchestrator` and each
  specialist skill state the same rule, and a test asserts it (FR-6).
- **S7 Maintainer is not an approver.** A skill halts on a release decision; the question
  goes to the release authority in the roster, not to the skill's maintainer (FR-7).
- **S8 Outside context.** Meeting notes that would widen scope are not acted on until
  recorded with source and date in a requirement, an ADR or an issue comment; notes that
  conflict with the vision are raised to the Product Owner (FR-8).
- **S9 Tracker unavailable.** Work halts on another lead and the tracker cannot be
  reached. The current person's queue gains a `pending` row and the session names who to
  tell. At the next session with the tracker reachable, an escalation issue is opened and
  the row's `Ref` becomes its number (FR-5).

## Failure modes

- **A queue file is committed.** The ignore rule and the validator check prevent it; the
  README says why.
- **The queue becomes the record.** FR-4 keeps answers in the delivery records, and no
  gate reads the queue.
- **A blocked milestone is invisible to the team.** The escalation issue is shared at
  once; the records task writes it to `STATUS.md` at the next merge batch or at session
  close, whichever comes first.
- **The tracker cannot be reached.** The escalation is held as a `pending` row owned by
  the current person and filed when the tracker returns (FR-5); the roster's escalation
  channel carries the message meanwhile.
- **Two people share one GitHub login on a machine.** The file follows the login; the
  profile's roster remains the authority on who holds a role.
- **A lead bypasses the workflow with a direct skill call.** FR-6 sets the handover rule;
  enforcement by hook is tracked separately.
