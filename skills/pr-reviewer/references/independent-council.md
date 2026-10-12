# Independent Council review and loop recovery

AI Council is a review capability, not a required provider, model roster or number
of agents. Use one qualified independent reviewer by default. A fresh context on the
same model is valid independence; it does not provide model diversity. Use additional
perspectives when the risk or unresolved uncertainty justifies their cost.

## Contract, adapter and local policy

| Layer | Owns |
| --- | --- |
| Shared plugin | Independence, exact-candidate evidence, verdicts and escalation |
| Host adapter | Fresh-context invocation, read-only boundaries and receipts |
| Project profile | Permitted reviewers/subscriptions, budgets and fallback authority |

Discover available capabilities without installing, authenticating or spending on new
services. Availability is not permission. Respect the selected subscription and any
explicit model requirement; switch only within an already-authorised policy or a new
operator decision. Do not import one maintainer's local provider preferences into the
portable contract. The same requirements apply in every supported host.

Give a fresh reviewer the requirements, governing contract, exact candidate and raw
evidence. Do not inherit the author's conversation or suggest an intended verdict.
Keep it read-only and bounded. Require actionable findings with evidence and a final
verdict. PASS has zero conditions; process exit, agreement, an empty review or a
conditional verdict is not approval. Local receipt metadata is not authentication.

## Recover a stuck loop

The project declares an attempt/time ceiling before consequential review starts.
Track it by stable work-item identity, including changed commits and reviewer runs.
When the ceiling is reached, or findings recur without relevant progress:

1. Stop dependent dispatch and retain all findings, candidates and attempt history.
2. Diagnose whether the constraint is requirements, design, implementation, missing
   evidence, environment or reviewer availability. A tool failure is not a code defect.
3. Replan or narrow the work with its accountable owner and a falsifiable next check.
4. If useful and authorised, use an alternative independent perspective. Supply the
   unresolved finding ledger so it can verify resolutions rather than forget blockers.
5. Reconcile disagreement against source and acceptance criteria. Never choose the
   most favourable verdict or average votes into PASS. Resolve every blocking finding
   with evidence; a disputed finding needs an explicit, evidenced disposition.
6. Any renewed budget has an owner, reason and scope; preserve earlier attempts.
   Changing SHA, branch, provider or model must not silently reset the ledger.
7. Re-run applicable checks and obtain review of the final assembled candidate.

This is an orchestration procedure. The optional helper below executes one review;
it does not enforce the cross-session attempt ledger. Declare that limitation until
the project's work system enforces the ceiling. Missing review never authorises merge.

## Optional local receipt helper

Native fresh-context review is preferred when available under project policy. A host
may instead use `scripts/review-gate.sh --staged`, `--range BASE..HEAD`, or `--pr N`.
Set `REVIEW_GATE_LANE` and `REVIEW_GATE_MODEL` explicitly. There is no default or
automatic fallback. The model field records the requested identity or a declared
host-default selection, not a verified resolved model.

For a host-owned wrapper, select `REVIEW_GATE_LANE=adapter` and set
`REVIEW_GATE_ADAPTER` to an absolute executable path. The wrapper receives the complete
prompt on stdin, no arguments, and the requested model/effort in environment variables.
It returns plain UTF-8 analysis ending in exactly one `VERDICT: PASS`,
`VERDICT: CONCERNS` or `VERDICT: BLOCK`; only PASS succeeds. The operator must approve
its data boundary and read-only invocation. This seam makes no claim that an untested
host wrapper works. Concrete CLI adapters (`claude`, `agy`, `gemini`) are optional
explicit transports, not a provider policy. The Claude adapter checks its JSON result
and reported model identity; other adapters do not authenticate a resolved model.

The helper refuses failed/empty/conditional results, timeouts, input changes and
oversized inputs rather than truncating. PR diffs that omit binary content are refused;
obtain complete candidate-bound material for a separate review. A minimum-length check rejects empty rubber
stamps; semantic review quality still requires judgement. Retain the full inputs,
stdout/stderr, candidate identities and result under the worktree's Git directory.
Async mode and `--last` are advisory history, not approval of a later candidate.
PR comments require explicit `--comment` and posting authority; none are automatic.
Hook opt-in is local (`git config review.gate async|block`). A local helper does not
enforce branch protection or grant commit, merge, release or deployment authority.
