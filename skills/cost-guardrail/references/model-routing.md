# Guarded model routing

Use deterministic tools when they can complete the task reliably. Delegate only when
an independently checkable output justifies the handoff cost. Each assignment names
its inputs, output, allowed paths, owner, requested model/effort, acceptance command and
time/attempt limit. Isolate mutating lanes; one owner integrates the result.

## Adopt explicitly

Installing these skills does not activate routing. A project must select its own mode
(`off` or `guarded`), owner, available model/effort mapping, budget and private receipt
location. Without an adopted policy, retain the project’s existing baseline and gates.
Do not copy another project’s active pilot settings as authority.

| Work | Route |
|---|---|
| Search, arithmetic, parsing or transformation with a reliable command | Deterministic tool |
| Bounded, non-sensitive read-only extraction or formatting with explicit sources and executable acceptance checks | Small-model pilot if adopted; otherwise baseline |
| Code, unqualified families, ambiguity, missing checks or interacting state | Baseline; a short ticket does not qualify a downgrade |
| Security, permissions, privacy or data integrity | At least baseline; preserve stricter project floors |
| Architecture or substantial uncertainty | Assess greater reasoning; record rationale and budget |
| Independent review | Existing fresh-context Council policy; never author self-approval |

Verify host availability before dispatch. Record requested versus observed identity
separately; unknown observed identity stays unknown. Preserve existing authority and
risk floors. An unavailable model requires a recorded, already-authorised alternative;
never switch subscriptions automatically.

## Accept, recover and stop

Run the independent check before accepting output. Retain failed attempts and their
cost; escalate at most once to the authorised baseline and recheck. If recovery fails,
stop and diagnose. Stricter project limits take precedence.

Set the adopted mode to `off` to stop small-model selection and return to the existing
baseline. Record the reason. The orchestrator must check mode before every dispatch;
this instruction does not enforce a kill switch. Explicitly stop running work or allow
it to finish safely.

Review after seven calendar days from the first recorded pilot assignment or 20 eligible
assignments, whichever comes first. Default to `off` on expiry until the owner records a
reviewed renewal. Missing acceptance evidence, a safety regression or an additional
acceptance failure against the matched baseline suspends that family immediately.

## Measure privately

Keep an append-only local receipt per attempt outside tracked source, at the location
selected by the owner. Record task/source and acceptance identifiers, policy version,
model/effort, timestamps, outcome, check result, retries and available usage. Include
parent planning, review and repair, or disclose their absence. Exclude prompts, code,
credentials, customer content and identifiable task text. Do not publish raw receipts.

Unknown usage is unmeasured, not free. Never infer tokens from character counts. Cached
input is a subset of total input; use the provider’s documented output-token accounting.
Separate dated API-equivalent estimates from subscription charges. Collection is manual
unless the adopting host supplies and verifies an integration.

Compare predeclared matched task families against a fixed-baseline control, randomising
assignment where practical. Track accepted outcomes, all attempts, cost coverage, total
cost per accepted outcome and end-to-end latency. Rebaseline after model/effort or policy
changes. Target at least 20% lower cost with no additional acceptance failures or material
slowdown; a small pilot is a learning signal, not proof. Do not promote on cost alone.
