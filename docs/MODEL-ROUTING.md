# Repository model-routing pilot

Policy version: `guarded-routing-v2`. Tracking issue: #30. Owner: JP.

**Mode: guarded**

These settings apply only to work on this harness repository on branches containing
this policy. Consumer projects must adopt their own policy; installation grants no
routing authority. Existing operator instructions and risk floors take precedence.

Follow the [portable routing guide](../skills/cost-guardrail/references/model-routing.md)
for assignment contracts, acceptance, recovery, measurement and expiry.

| Setting | Repository selection |
|---|---|
| Small-model pilot | Requested `gpt-6-luna`, high effort; bounded read-only work only |
| Baseline | Requested `gpt-6.1-sol`, medium effort; preserve stricter task floors |
| Review | Existing fresh-context Council policy on the selected subscription |
| Budget | Declare a time/attempt ceiling before each assignment; at most one baseline recovery |
| Receipt location | Owner-selected private local log; establish its path before the first assignment and reuse it across sessions |
| Expiry | Seven calendar days from the first receipt or 20 eligible assignments; then default off pending reviewed renewal |

Verify model availability before dispatch. JP selected Luna high on 15 October 2026;
it remains unevaluated here. Historical medium-effort results did not preserve quality
and do not qualify high effort or establish savings. Start a separate v2 comparison.

Before dispatch, inspect the private log for expiry and suspended families. If its state
cannot be established, use mode `off` until the owner resolves it. No receipts means not
started only after verifying the selected log. Keep measurements outside tracked source.

To stop the pilot, set **Mode: off** above and record the reason in the private log.
Retain decomposition and existing safety gates. Stop running work or allow it to finish
safely. Revert the introducing change to remove the policy entirely. Routing and receipt
collection are instructions, not an automatic dispatcher or enforced control.
