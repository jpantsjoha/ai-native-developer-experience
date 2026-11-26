# The four delivery records

> **One fact, one owner.** Four artefacts carry a project's delivery state. Each answers exactly
> one question. When two of them answer the same question, they drift — and a reader who checks
> the wrong one gets the wrong answer.

This is the default way of working. A project may add records; it may not merge these four.

---


The [portable workflow](../skills/operating-model-bootstrap/assets/DELIVERY-WORKFLOW.template.md#golden-thread-evolving-intent-to-accepted-capability)
defines evolving requirements, role ownership and safe cleanup. This repository's
[task template](../.github/ISSUE_TEMPLATE/delivery-task.md) carries the ticket fields.
Unreleased records merged source; version sections link published tags/releases.
Neither establishes installed adoption or observed use.

## The four

| Record | The one question it answers | Written when |
|---|---|---|
| **GitHub issues** | *What exactly is this piece of work, and how will we know it is done?* | Before the first line of code |
| **`STATUS.md`** | *What is happening right now, and what is waiting on whom?* | The records task, after each merge batch: one entry per working session, amended by later batches in that session |
| **`ROADMAP.md`** | *What are we building toward, in what order?* | The records task, after each merge batch, when the batch changed what comes next or its order |
| **`CHANGELOG.md`** | *What shipped — proven, tested, delivered?* | The records task, after each merge batch that merged user-visible work |

Two rules keep them apart (the third, reconciliation, is [below](#reconciliation-one-records-task-per-merge-batch)):

- **`ROADMAP` owns build order.** Where any other document disagrees about what comes next, the
  roadmap wins. Sequence from there and nowhere else.
- **`CHANGELOG` records the proven, not the intended.** If it could not be demonstrated, it does
  not go in. A changelog of intentions is worse than none, because it reads as evidence.

---

## Issues: atomic scope, checkable DoD

**An issue that is not filed is not started.** The tracker is brought current *before* the first
line of code — because the failure this prevents is work that accretes from a small fix and is
reconciled to the plan afterwards, if at all.

Every issue carries five things. Fewer, and the next person re-derives what you already knew:

1. **Golden thread** — what it traces to. The vision, the requirement, the ADR, the parent epic.
   An issue that traces to nothing is either the first of something or nobody's priority.
2. **Scope** — what it *owns*, and what it **explicitly excludes**. The exclusions do more work
   than the inclusions: they are what stops a ticket growing in the dark.
3. **Definition of done** — as *checkable items*, not prose. "The validator refuses a planted
   violation" is checkable. "Improve validation" is not.
4. **Test and validation plan** — how the DoD is proven. Name the command.
5. **Dependencies and authority** — what must land first, and whether anything needs a decision
   only the operator can make. Say **"not blocked"** explicitly when it isn't; silence reads as
   blocked.

**Atomic means independently validatable.** If you cannot describe how to verify it in isolation,
it is not atomic — split it, or merge it with its dependency.

**State moves in one direction:** `not started → specified → built → gated → shipped`. Two of
those are routinely overclaimed and are worth defining hard:

- **`gated`** — a test proves a *user* can reach it. Not that the code exists. Not that the units
  pass. A feature whose units pass and whose journey does not has been written, not delivered.
- **`shipped`** — a person used it. Deployment is not shipping.

### One state, four vocabularies

The harness describes the same work in four places. Each answers a different question;
this crosswalk keeps them from contradicting one another.

| Record lifecycle | Tracker status (`validate_delivery.py`) | Operating-manual state | Changelog wording |
|---|---|---|---|
| `not started` | Proposed, Draft | INTAKE → AUTHORIZED | — |
| `specified` | Accepted, Ready | PLANNED | — |
| `built` | In progress, In review | ISOLATED → APPROVED (handoffs H1, H2) | — |
| `gated` | Done (merged, user-path test walks it) | — | merged, under Unreleased |
| `gated` (released, not yet used) | Done | DELIVERED (H3) | released / deployed |
| `shipped` | Done (closed with evidence) | OBSERVED → COMPLETE | observed in use |
| — | Blocked, Parked | BLOCKED (H4) | — |
| — | Superseded | SUPERSEDED, ABORTED | — |

A row never implies the next. Merged is not released, released is not deployed, and
deployed is not used. COMPLETE also requires the lane's worktree and merged branch to be
removed, or their retention recorded with an owner; the read-only lane hygiene report
(`make hygiene` here, `python3 <plugin-root>/scripts/lane_hygiene.py` elsewhere) shows what is left.
The full Definition of Done ladder lives in the delivery workflow template
(`skills/operating-model-bootstrap/assets/DELIVERY-WORKFLOW.template.md`).

---

## STATUS: the live record, pruned

Reverse-chronological, newest first. One entry per working session, and each entry says: what
landed, what is waiting on the operator, and the lesson — **stated once**.

It is a *working* document, so it gets pruned. When an entry stops being live, delete it and let
git history hold it. A status file that only grows becomes an archive nobody reads, which is the
same as having no status file, except it takes longer to discover.

**Where operator items live.** An item that others must see or act on is a GitHub issue,
and `STATUS.md` points to it by number. An item only the operator needs sits in the local,
git-ignored queue `HITL/OPERATOR/` ([AMH-001](../requirements/ADOPTION-MODES-HITL.md)),
which is a working list and never a record; an answer counts once it is recorded in an
issue, an ADR or `STATUS.md`. A local dashboard may read the queue on the operator's own
machine.

**It ends with the decisions waiting on the operator** — a table with options, a recommendation
and reversibility. See the `sitrep` skill for the format; that section is the one most operators
read first.

---

## ROADMAP: the plan of record

Milestones are **outcomes, not buckets**. "P1 — Author a book" is an outcome. "Frontend work" is
a bucket. If you cannot say what becomes true when a milestone closes, it is a bucket.

It carries: the dispatch order, the milestone set, the deferred queue, and the gate ledger.

**A deferred item costs something to defer**, or the deferred queue becomes where things go to be
forgotten. Every deferral names four things: the reason code, the next action, **what it blocks**,
and where the evidence lives. An item missing any of them has been dropped, not deferred.

---

## CHANGELOG: what shipped

Append-only, newest first, grouped by what the reader cares about — not by which branch it came
from. Each entry names the change, the issue, and what proves it.

**Write it in the records task that follows the merge batch, never at release time and never inside the feature PR.** A changelog reconstructed at tag time is reconstructed from memory, and memory flatters.

---

## Reconciliation: one records task per merge batch

The three state files drift unless one owner writes them, so this applies to every project and every session, solo or parallel. The rule:

- **Builders never edit `ROADMAP.md`, `STATUS.md` or `CHANGELOG.md`.** They describe the record
  change their work implies in the PR body instead.
- **After each batch of merges, one records task reconciles all three together** (it checks each one, and edits a file only where the batch changed its fact):
  - `ROADMAP.md`: what is next, and in what order.
  - `STATUS.md`: the issues and PRs in progress, and what waits on whom, including operator
    decisions. A later batch in the same session amends that session's entry; it does not add a second one.
  - `CHANGELOG.md`: user-visible work that merged or shipped, each entry with its PR number and what proves it.
- **Every entry links its issue or PR**, so the three files can be cross-checked and never
  disagree. An entry without a link is a claim, not a record.
- The orchestrator owns the records task. In a solo session the person or agent leading the session is the orchestrator, and the batch is the merges since the last records task. The records task runs after the batch merges, as its own commit or PR, never per feature PR and never mixed into a feature PR. Its PR gets an independent review like any other.

---

## The loop

```
issue filed (DoD, scope, thread)
   ↓
branch → build → gate → independent review (PR body notes the record changes)
   ↓
merge → issue closed with evidence
   ↓
batch merged → one records task: CHANGELOG + STATUS + ROADMAP together, each entry linked
```

Closing an issue means **closing it with evidence** — the command that proved it, the verdict
that reviewed it. An issue closed with "done" teaches the next reader that closure means nothing.

---

## The audit — run it when the records feel stale

Six questions. Each has a command, so the answer is derived rather than asserted:

| Question | How |
|---|---|
| Is anything in flight untracked? | `git branch -r --no-merged origin/main` against open PRs and issues |
| Does any issue lack a milestone? | `gh issue list --json milestone --jq '[.[]\|select(.milestone==null)]\|length'` — the answer should be 0 |
| Is any state overclaimed? | For each `gated` row, find the test that walks it. No test, no `gated` |
| Do the records contradict each other? | Grep the same fact in all four. Two answers is a drift |
| Does the CHANGELOG match `git log`? | Spot-check the newest entries |
| What no longer earns its place? | Superseded plans, dated snapshots, duplicated inventories |
| Are merged lanes left behind? | `make hygiene` (read-only; add `HYGIENE_ARGS=--pr-state` for squash merges) |

**Route the audit to a reviewer that did not write the records.** Self-auditing planning
documents finds what you remember, not what you missed.
