# <Project Name> Operating Profile

**Manual version:** <version>
**Manual SHA-256:** <digest>
**Profile owner:** <accountable human or role>
**Last verified:** <YYYY-MM-DD>
**Review trigger:** <cadence and material-change triggers>

This tracked profile supplies project-specific authority, invariants, commands, and
delivery controls for the vendor-neutral operating manual. Replace every angle-bracket
placeholder before adoption.

## Policy precedence

1. Platform and safety policy.
2. Explicit instruction from <accountable operator/role> for the current task.
3. <canonical project constitution and this profile>.
4. The adopted universal operating manual.
5. Local conventions, memories, examples, and inference.

Conflicts in authority, invariants, or current facts block the affected action until
reconciled. Infer intent; never infer permission.

## Authority and approval roles

| Role | Accountable for | May approve |
|---|---|---|
| <human/operator/product owner> | Outcome, scope, external effects, protected changes | R3, production, credentials, constitution, spend, destructive/external actions |
| <integration owner> | Exact assembled candidate and merge order | Assembly only; cannot self-approve R3 |
| <mutating lane owner> | Owned files/resources and lane evidence | Its isolated implementation only |
| <domain reviewer> | Refutation of domain correctness | Final PASS on exact candidate; no scope authority |
| <governance/docs reviewer> | Policy, docs, status, and evidence coherence | Final PASS on exact candidate; no scope authority |

A skill, model, agent name, CI label, or previous PASS never grants permission.

## Risk tier overrides

| Tier | Project examples | Required evidence |
|---|---|---|
| R0 | <bounded read-only work> | <grounding and load-bearing verification> |
| R1 | <small reversible local edit> | <focused check and rollback> |
| R2 | <multi-file/interface/data change> | <checkpoint, worktree, regression, convergence review> |
| R3 | <security/production/money/constitution/destructive/external work> | <explicit authority, domain invariants, exact review, rollback, observation> |

Ambiguity rounds upward.

## Protected path inventory

List complete file or directory paths. State whether renames, deletions, modes, generated
outputs, and gate self-changes are covered.

- `<path>` — <invariant/blast radius>
- `<path>` — <invariant/blast radius>
- `<gate/config path>` — governance/self-enforcement
- `<this profile path>` — constitutional contract

## Non-negotiable invariants

- <safety/security/business invariant>
- <data or accounting invariant>
- <availability/recovery invariant>
- <privacy/compliance invariant>
- <evidence/no-look-ahead/no-silent-failure invariant, if applicable>

## Worktree and resource isolation

- One branch/worktree per mutating lane: <naming/location rule>.
- One integration owner and clean integration worktree: <rule>.
- Resource namespaces: <ports, databases, caches, queues, cloud resources, datasets>.
- Canonical operational checkout/process: <path/owner>; agent worktrees never control it.
- Forbidden cross-lane git/state actions: <stash/reset/clean/rebase/merge rules>.

## Exact validation and security commands

Run from <worktree/environment>:

```bash
<focused test command>
<lint command>
<typecheck command>
<full/convergence command>
<security/secret/dependency commands>
<profile drift command>
<exact review or post-commit command>
```

Record exact commands, exit codes, environment, base, and candidate identity.

## Data freshness and statistical gates

- Sources and owners: <list>.
- Freshness/completeness/correctness criteria: <criteria>.
- Frozen vintage, expected/actual scope, exclusions, and hashes: <rules>.
- Statistical floors, sample size, multiple-testing, and aggregate verdict: <rules>.
- Fail-closed and remediation behavior: <rules>.

Use `not applicable — <reason>` when the project has no data-dependent decision. Do not
delete the section.

## Review roles and verdict semantics

- Required independent roles by tier: <mapping>.
- Exact candidate binding: <tree/manifest/SHA mechanism>.
- PASS: zero conditions.
- Conditional/amendment: blocking until fixed and re-reviewed.
- REJECT/BLOCKING: halt.
- Override: <explicit operator path, durable reason, and non-reuse control>.
- Residual local/remote enforcement gap: <honest limitation>.

## Documentation triggers

- Status: <file and trigger>.
- Changelog: <file and append-only rule>.
- Architecture/HLD/ADR: <triggers and approval owner>.
- Runbooks/user docs: <behavior/operation triggers>.
- Invalid evidence: <withdrawal/supersession rule>.

## Deployment and observation

- Authorized delivery destination: <branch/environment/service>.
- Pre-delivery gates: <commands/evidence>.
- Deployment owner and authority: <role>.
- Observation window and signals: <health, logs, metrics, alerts, user journey>.
- Stop/rollback triggers: <thresholds>.
- External mutation idempotency: <mechanism>.

## Rollback

- Code/config: <forward revert or rollback method>.
- Data/state: <backup/restore or compensating action>.
- Production kill switch: <mechanism and owner>.
- Post-rollback verification: <commands/signals>.

## Cost and concurrency budget

- Maximum active lanes: <number>; maximum mutating integrators: one.
- Model/tool/compute/network budget: <limits and approval threshold>.
- Timebox/escalation: <rule>.
- Paid/external loops: <explicit authorization requirement>.

## Artifact retention

- Permanent evidence: <ADRs, manifests, review artifacts, reports, changelog>.
- Generated/local evidence: <what, where, retention duration>.
- Sensitive evidence: <sanitisation and secret-handling rule>.
- Stale evidence: never reuse; <supersession/quarantine rule>.

## Completion contract

Complete means the exact integrated candidate passed every applicable gate, all review
conditions are closed, delivery was authorized and observed, docs/status/changelog agree,
remaining risks and operator actions are explicit, and rollback is known.
