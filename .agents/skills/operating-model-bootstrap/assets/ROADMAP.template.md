# <Project Name> Roadmap

The roadmap orders outcomes and records their gates. The configured work system owns
active milestones, epics, tasks, assignment, and queue state.

## Now

| Outcome ID | Outcome | Product Owner gate | Milestone / epic | Dependencies | Status |
| --- | --- | --- | --- | --- | --- |
| `<ID>` | `<measurable outcome>` | `<Draft or Accepted + evidence>` | `<links>` | `<IDs or none>` | `<state>` |

## Next

| Outcome ID | Outcome | Entry condition | Dependencies |
| --- | --- | --- | --- |
| `<ID>` | `<measurable outcome>` | `<condition>` | `<IDs or none>` |

## Later

| Outcome ID | Outcome | Revisit trigger |
| --- | --- | --- |
| `<ID>` | `<possible outcome>` | `<evidence or date>` |

## Rules

- Product Owner owns outcome order, scope, and acceptance.
- `delivery-orchestrator` proposes task decomposition and reconciles dependencies.
- Material scope or acceptance changes return the outcome to Product Owner review.
- Do not duplicate mutable task state here; link to the configured work system.
- Completed means delivery evidence, status, roadmap, changelog, and open risk agree.
