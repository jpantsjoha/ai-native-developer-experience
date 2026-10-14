# Guarded model-routing pilot

Policy version: `guarded-routing-v1`. Tracking issue: #30.

**Mode: guarded**

This is an instruction policy for this repository, effective only on branches containing
it. It does not launch agents, intercept tools, collect usage automatically or alter
consumer projects. An installed plugin supplies guidance; each adopter must explicitly
select its own mode, model mapping, owner and budget. Existing authority, review and risk
floors always take precedence. JP owns this repository's pilot.

## Before dispatch

Consider decomposition for incoming backlog tasks. Delegate when a bounded output can
be independently checked and the handoff is cheaper than doing the work directly.
Avoid splitting trivial or tightly coupled work just to increase agent count. Each
assignment names its input, output, Definition of Done, allowed paths, dependencies,
owner, requested model/effort, time/attempt ceiling and executable acceptance check.
Use isolated worktrees for mutating lanes; one owner integrates and verifies the result.

| Work and evidence | Routing instruction |
|---|---|
| Search, arithmetic, parsing or transformation with an existing reliable command | Use deterministic tools first; no model needed |
| Bounded read-only, non-sensitive extraction or formatting; explicit source/output; independently executable checks; no code, state or credential effects | Small model at medium effort may be used as a monitored pilot; otherwise baseline |
| Code changes, unqualified task families, ambiguity, missing checks, or interacting state | Baseline at medium effort; a one-file diff or short ticket does not qualify a downgrade |
| Security, permissions, privacy, data integrity or other higher-consequence work | At least the baseline; preserve any stricter project model/review floor |
| Architecture or substantial uncertainty | Deliberately assess whether greater reasoning is needed; record rationale and budget |
| Independent review | Existing fresh-context Council policy; never let the author approve its own change |

For the current Codex-selected workflow, small means requested `gpt-6-luna` and baseline
means requested `gpt-6.1-sol`. Verify host availability before dispatch, explicitly set
medium, and record requested versus observed identity separately. Do not infer identity
from inheritance or availability from a table. If unavailable, stop that lane and use
an already-authorised available baseline only after recording the change; no automatic
subscription switch. Other providers need their own verified mapping and evaluation.

All reported benchmark workers used medium. Luna high has not been evaluated here.
A deliberate effort change is a separate experiment, with its reason and usage recorded;
never pool it with medium or describe it as a proven improvement. This matrix is a
conservative proposal informed by failures, not a universally qualified routing policy.

## Acceptance, recovery and rollback

Run the independent check before accepting any output. Preserve a failed small-model
attempt, its diagnostics and usage; escalate at most once to the authorised baseline,
then recheck. Existing stricter attempt limits win. Count both attempts and any parent
planning/review work. If recovery fails, stop and use the project's diagnostic/review
process rather than continuing a cheap-model loop.

Set **Mode: off** above to disable pilot small-model selection immediately. Keep useful
decomposition and all existing safety gates; return unqualified work to the baseline.
Record the timestamp and reason in the pilot log. Revert the introducing PR to remove
the complete policy. Neither operation requires changing product code. Instructions are
not an enforced kill switch: the orchestrator must read and honour the mode before each
dispatch. Already-running work must be explicitly stopped or allowed to finish safely.

Review after seven calendar days from the first recorded pilot assignment or 20 eligible
assignments, whichever comes first; no receipts means not started. On expiry default to
`off` until an explicit reviewed renewal is recorded. Any safety regression, additional
acceptance failure relative to the matched baseline, or missing acceptance evidence
suspends the affected family immediately. Missing usage means unmeasured economics,
not zero cost. Do not promote a family on a small all-pass sample alone.

## Monitor the actual workflow

The orchestrator maintains an append-only local JSONL receipt per attempt. Keep it outside
tracked source, or in a gitignored local folder. Do not store prompts, code, customer
content, credentials or identifiable task text. A minimal example (null means unknown):

```json
{"task_id":"pilot-001","policy_version":"guarded-routing-v1","mode":"guarded","family":"read-only-extraction","arm":"pilot","baseline_model":"gpt-6.1-sol","requested_model":"gpt-6-luna","requested_effort":"medium","observed_model":null,"observed_effort":null,"attempt":1,"parent_task_id":null,"started_at":null,"finished_at":null,"accepted":false,"check_receipt":null,"input_tokens":null,"cached_input_tokens":null,"output_tokens":null,"api_equivalent_usd":null,"pricing_date":null,"fallback_reason":null}
```

Fill acceptance only after the named check runs; missing evidence is not a pass. Record
all dispatched attempts, including errors and timeouts. Add actual host usage only when
available; never infer tokens from character count. Cached tokens are a subset of input,
not extra input. Keep reasoning tokens within their provider's reported output total
unless documentation establishes a different accounting contract. API-equivalent price
estimates and subscription charges are separate. No tracking script is installed by this
policy; receipts require orchestrator/host integration and must not be claimed automatic.

Compare predeclared matched task families against a fixed-baseline control; retain source
and acceptance identity and randomise assignment where practical. Report assigned tasks,
accepted tasks, failed/retried attempts, known-cost coverage, total cost per accepted
outcome, token totals by model/effort and end-to-end latency. Include planner, review and
repair costs or explicitly disclose their absence. Rebaseline after policy/effort changes.
A lower estimate is useful only if quality is preserved: target at least 20% lower cost,
no additional acceptance failures and no material delivery slowdown. Small pilot counts
are a stopping/learning signal, not statistical proof. Phoenix or equivalent replay can
validate the records; a green integrity check does not turn a failed quality claim green.

## Why the policy is conservative

The [anonymised benchmark](research/model-routing-2026-10.md) found cheaper selected
outcomes but an additional failed patch. JEV made the same decisions as rules. Neither
policy earned general rollout. The next experiment should measure acceptance-gated
escalation on untouched tasks, not silently tune these results into a success claim.
