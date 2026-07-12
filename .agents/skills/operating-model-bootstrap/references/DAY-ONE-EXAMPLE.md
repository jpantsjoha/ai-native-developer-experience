# Day-One Example — Atlas Service

This fictional example shows the intended readiness boundary. It is a calibration aid,
not project policy to copy without grounding.

## Starting point

Three developers and one product lead are beginning a new API service. The repository has
an initial `README.md`, an architecture sketch, and no application code. The team copies
the baseline `.agents/skills/` directory and runs:

```bash
python3 .agents/skills/operating-model-bootstrap/scripts/bootstrap_operating_model.py \
  --project-name "Atlas Service" .
```

The initializer creates the immutable manual, project profile, task templates, and three
thin discovery adapters. The code assistant then grounds the seed from the repository and
records these day-one facts:

- profile owner: tech lead; accountable operator: product lead;
- integration owner: rotating named developer, recorded per checkpoint;
- R0: repository reading and design exploration;
- R1: reversible documentation and local scaffolding changes;
- R2: application interfaces, dependencies, schemas, or multi-file implementation;
- R3: production, secrets, personal data, external messages, spend, destructive work, or
  changes to the operating contract;
- protected paths: operating-model documents, CI, infrastructure, schemas, auth, and
  secret/deployment configuration;
- local mutating lanes: one branch/worktree each, with unique ports and local data stores;
- shared/production services: controlled only by the designated operator from the
  canonical operational checkout;
- convergence command: not yet established — owner: tech lead; required before: first R2
  implementation;
- delivery and rollback: not yet established — owner: platform lead; required before:
  first deployable milestone.

The profile remains `seed`. That is honest and useful: the team can start R0 system design,
write ADRs, form the backlog, define interface contracts, and plan delivery without
pretending production controls already exist.

## Initial capability routing

The same team contract routes work consistently regardless of assistant syntax:

| Need | Capability |
|---|---|
| Break the outcome into owned strands | `delivery-orchestrator` |
| Develop system context and ADRs | `the-architect` |
| Turn the selected design into acceptance criteria | `spec-first-delivery` |
| Attack assumptions and silent failure | `adversarial-gate` |
| Validate domain invariants | `domain-validator` |
| Review the exact integrated candidate | `pr-reviewer` |
| Decide whether delivery and rollback are ready | `release-readiness` |
| Reconcile decisions, state, risks, and next action | `sitrep` |

## First shared prompt

```text
Use $operating-model-bootstrap to ground this repository and complete its day-one seed.
Do not invent project facts. Resolve the day-one minimum from tracked evidence; record
unknowns with an owner and the trigger that must resolve them. Then use the architecture,
specification, and delivery-orchestration capabilities to propose the first system design
and technical delivery plan. Stop before any R2/R3 mutation or external action that lacks
explicit authority and runnable controls.
```

## Promotion to active

Before the first R2/R3 implementation, the team resolves applicable protected paths,
invariants, commands, reviewers, evidence, delivery, observation, and rollback. It changes
the profile status to `active`, creates a checkpoint and evidence manifest, and runs the
validator with `--require-active`.

This boundary is deliberate: the bootstrap removes blank-page operating-model work on day
one, but does not manufacture facts about a system that the team has not designed yet.
