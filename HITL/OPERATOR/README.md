# HITL/OPERATOR

This folder holds one person's local queue of what waits on them: decisions, actions
and observations an agent has raised. Specification:
[AMH-001](../../requirements/ADOPTION-MODES-HITL.md); decision:
[ADR-006](../../architecture/decisions/ADR-006-adoption-modes-and-hitl-queue.md).

- Solo: `Master-TODO.md`. Team: `<gh-id>-TODO.md`, one for each person.
- Queue files are git-ignored and never committed. Only this README is tracked. The queue
  changes many times a day; `docs/STATUS.md` carries the shared record.
- The queue is not a record. An answer counts when it is recorded in an issue, an ADR or
  `STATUS.md`.

## Row format

One Markdown table, these columns in this order:

| Column | Content |
| --- | --- |
| Item | The decision, action or observation asked of the person |
| Type | `decision`, `action` or `observation` |
| Role | The roster role it is asked of |
| Ref | `#123` escalation issue, `local`, or `pending` |
| Unblocks | Issues and milestone that wait on it, or `-` |
| Cost if wrong | What a bad or late answer costs, or `-` |
| Reversibility | `cheap`, `costly` or `one-way` |
| Recommendation | The agent's recommended answer, or `-` |
| Raised | `YYYY-MM-DD` |
| Due | `YYYY-MM-DD`, or `-` |
| Record | `#123`, `ADR-006` or `STATUS` |

## Commands

```text
python3 scripts/hitl_queue.py validate
python3 scripts/hitl_queue.py migrate --source <file> [--yes]
```

`validate` skips cleanly when no queue file exists. `migrate` lists what it would copy
and writes only with `--yes`; it never edits the source file.
