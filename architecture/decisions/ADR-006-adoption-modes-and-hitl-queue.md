# ADR-006: Two adoption modes and a local human-in-the-loop queue

## Status

Accepted — 2026-11-20. Decision owner: JP, who accepted it as drafted on 20 November
2026. It records his direction of the same date on the queue's path and privacy.
Specification:
[AMH-001](../../requirements/ADOPTION-MODES-HITL.md).

## Context

The harness is run by one person across whole projects and by teams of accountable leads
in one repository. It documents neither mode. Projects have each invented a file for what
waits on the operator, in different formats and places, and no skill maintains it.

The shared record of what waits on whom is `STATUS.md`, written by the records task after
each merge batch. A personal working list changes far more often than that and holds
items that mean nothing to anyone else.

## Decision

1. **Two adoption modes, one workflow.** The operating profile records `solo` or `team`.
   Workflow, gates, risk tiers, records and release cadence do not differ. The mode sets
   who holds each decision.
2. **A queue file for each person, kept local.** Solo: `HITL/OPERATOR/Master-TODO.md`.
   Team: `HITL/OPERATOR/<gh-id>-TODO.md`. The folder is git-ignored; only its `README.md`
   is committed. (JP, 20 November 2026: the list changes too quickly to track in the
   repository, and `STATUS.md` and `ROADMAP.md` already carry the tracked state.)
3. **One row format**, set in AMH-001 FR-3, including what each item unblocks and how
   reversible it is.
4. **The queue is not a record.** Answers count when recorded in an issue, an ADR or
   `STATUS.md`. No gate reads the queue as evidence.
5. **The tracker is the shared channel; the queue is the local view.** A halt on a human
   opens an escalation issue assigned to the accountable roster role and labelled
   `needs-human`. `delivery-orchestrator`, `sitrep` and `wrap-it-up` collect the current
   person's open escalations into their queue, remove a row once its answer is recorded and
   its issue closed, and print a digest.
   They never write another person's queue and never answer a row.
6. **Delivery work enters through the orchestrator.** A specialist skill may answer a
   bounded read-only question directly and hands over when the work becomes a change.
7. **A specialist skill may have a named maintainer** in the roster. Maintenance carries
   no decision authority; halts go to the accountable role for the domain.
8. **Outside context is checked against the vision and recorded before it justifies a
   change**, in the repository or as a comment on the affected issue.
9. **Milestone blockers reach `STATUS.md` without a merge.** The records task also runs at
   session close whenever a milestone blocker is open and not yet in `STATUS.md`. This
   extends the reconciliation rule in `docs/DELIVERY-RECORDS.md`.

## Alternatives considered

- **Commit the queue.** The team and any dashboard would see every item. Rejected by JP:
  the churn is high, the content is personal working state, and the durable part already
  lives in `STATUS.md`.
- **One queue file for each role, not each person.** Follows the roster directly.
  Rejected: two people can share a role, and a person wants one list. The row's Role field
  keeps the routing.
- **Use issue labels and assignees only.** Nothing new to store. Rejected as the only
  mechanism: machine-local steps and unfiled questions have no issue, and it ties the
  harness to GitHub. Issues remain where the answer is recorded.
- **Keep per-project formats.** No migration. Rejected: each format would need its own
  adapter in every skill and tool that reads it, and one format costs less to build and
  keep.

## Consequences

- A person sees, in one file, what waits on them and what each item unblocks.
- A local dashboard can read the file on the machine it runs on. It cannot show another
  person's queue; team-wide visibility of blockers comes from `STATUS.md`.
- Bootstrap gains three questions (mode, GitHub login, role) and the validator two checks
  (ignored, well-formed).
- Projects with an existing operator to-do file migrate it once, by an explicit command
  that names the file; durable decisions move to `STATUS.md` and open items to the queue.
- Escalations add issues to the tracker. When the tracker cannot be reached, the
  escalation is held as a `pending` row in the current person's queue, announced through
  the roster's escalation channel, and filed as an issue when the tracker returns.
- The queue can go stale if the orchestrator is not used. The digest lists the oldest
  item first to make that visible.

How would I break this? Commit a queue file by force-adding it: the validator check on
tracked files catches it. Let an agent treat an old row as approval: rows carry no
answers, and FR-5 forbids answering for the person. Let a milestone blocker sit only in
one person's queue: FR-5 opens a shared escalation issue at once and FR-4 writes it to
`STATUS.md` at session close whenever it is not yet there. That path is the one most likely
to be skipped, so it is tested first.
