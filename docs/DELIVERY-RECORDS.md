# The four delivery records

> **One fact, one owner.** Four artefacts carry a project's delivery state. Each answers exactly
> one question. When two of them answer the same question, they drift — and a reader who checks
> the wrong one gets the wrong answer.

This is the default way of working. A project may add records; it may not merge these four.

---

## The four

| Record | The one question it answers | Written when |
|---|---|---|
| **GitHub issues** | *What exactly is this piece of work, and how will we know it is done?* | Before the first line of code |
| **`STATUS.md`** | *What is happening right now, and what is waiting on whom?* | One entry per working session |
| **`ROADMAP.md`** | *What are we building toward, in what order?* | When a milestone or the plan changes |
| **`CHANGELOG.md`** | *What shipped — proven, tested, delivered?* | When user-visible work merges |

Two rules keep them apart:

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

---

## STATUS: the live record, pruned

Reverse-chronological, newest first. One entry per working session, and each entry says: what
landed, what is waiting on the operator, and the lesson — **stated once**.

It is a *working* document, so it gets pruned. When an entry stops being live, delete it and let
git history hold it. A status file that only grows becomes an archive nobody reads, which is the
same as having no status file, except it takes longer to discover.

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

**Write it when the work merges, not at release time.** A changelog reconstructed at tag time is
reconstructed from memory, and memory flatters.

---

## The loop

```
issue filed (DoD, scope, thread)
   ↓
branch → build → gate → independent review
   ↓
merge → CHANGELOG entry → issue closed with evidence
   ↓
STATUS entry (what landed, what waits, the lesson)
   ↓
ROADMAP reconciled if the plan moved
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

**Route the audit to a reviewer that did not write the records.** Self-auditing planning
documents finds what you remember, not what you missed.
