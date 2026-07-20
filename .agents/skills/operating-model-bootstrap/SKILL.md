---
name: operating-model-bootstrap
description: Bootstrap or harden a project's operating model for mixed human and AI delivery teams. Use when starting a repository, adopting an agent harness, defining authority and risk tiers, coordinating parallel agents safely, binding evidence and review to an exact candidate, or correcting fragmented rules that prevent coherent, consistent, complete delivery.
---

# Operating Model Bootstrap

## When to use

- Starting a new repository or team project that will use AI agents or agent-harness skills
- Adopting this harness into an existing project for the first time
- Defining or repairing authority, risk tiers, lane isolation, or evidence-binding contracts
- Coordinating parallel human and agent lanes safely (worktrees, ownership, integration)
- Binding review to an exact candidate commit before R2/R3 work
- Correcting fragmented or contradictory rules across AGENTS.md, CLAUDE.md, and GEMINI.md

---

Establish a portable operating kernel and one tracked project profile. Treat humans,
agents, skills, tools, and gates as one delivery system with explicit authority,
ownership, evidence, and completion semantics. The day-one seed lets a new team begin
system design and delivery planning while explicitly owned project unknowns are resolved.

## Portability boundary

The operating model is model-, vendor-, and IDE-agnostic. Thin surface adapters only make
the same contract discoverable and invocable. They may not change authority, risk,
evidence, review, or completion semantics. This is a team-project harness bootstrap, not a
production application scaffold or a substitute for project/domain controls.

## Load the assets

Read the four contract assets before editing the target project:

- `assets/OPERATING-MANUAL.md` — released vendor-neutral normative kernel; copy it unchanged.
- `assets/PROJECT-OPERATING-PROFILE.template.md` — project-specific contract.
- `assets/CHECKPOINT.template.yaml` — durable state for R2/R3 work.
- `assets/EVIDENCE-MANIFEST.template.yaml` — exact-candidate evidence and review record.

Use the thin starter files under `assets/adapters/` for agent surfaces the target
project supports. They are discovery adapters, not competing constitutions.
For a greenfield adoption, read `references/DAY-ONE-EXAMPLE.md` to calibrate what may
start in `seed` state and what must wait for `active` controls.

Do not copy project details into the universal manual. Bind its exact SHA-256 in the
profile and adapters. Unknown profile facts must be owned and time-bounded, never
fabricated. Never call a seed profile active while applicable placeholders remain.

## Initialise safely

From a target repository containing this skill, preflight and install the day-one seed:

```bash
python3 .agents/skills/operating-model-bootstrap/scripts/bootstrap_operating_model.py \
  --dry-run --project-name "<project name>" .
python3 .agents/skills/operating-model-bootstrap/scripts/bootstrap_operating_model.py \
  --project-name "<project name>" .
```

The initializer creates the manual, seed profile, checkpoint/evidence templates, and
`AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` adapters. It preflights the whole file set and
refuses to overwrite any different existing file. For an existing adapter, merge the
protected contract deliberately rather than forcing replacement.

## Bootstrap workflow

1. **Ground the project.** Read its existing constitutions, architecture, delivery
   flow, test commands, deployment path, protected surfaces, and current state. List
   contradictions and stale claims before adding policy.
2. **Classify risk.** Map project work into R0–R3. Round ambiguity upward. Name the
   highest-impact silent failure, rollback owner, and observation surface.
3. **Confirm authority.** Separate useful intent from permission at the classified
   risk tier. Obtain explicit approval before constitutional, destructive, credential,
   external, deployment, production-data, or capital changes.
4. **Install the kernel.** Run the safe initializer or copy the released manual byte for
   byte to the canonical governance location. Record version, digest, owner, adoption
   status, and review trigger.
5. **Ground the profile.** Resolve the day-one minimum first. Fill applicable fields
   with verified facts and use `not applicable — reason` or `not yet established — owner:
   role; required before: trigger` elsewhere. Keep status `seed` for design/R0/R1; require
   `active` and runnable controls before R2/R3. Never invent a command, role, or control.
6. **Route baseline skills.** Confirm paths or equivalents for orchestration,
   architecture, specification, domain/adversarial validation, candidate review, release
   readiness, status, and cost. Invocation syntax may vary; semantics may not.
7. **Define the squad.** Assign one accountable human/operator, one integration owner,
   bounded mutating lanes, and independent reviewers. Give every lane owned files,
   owned resources, and a falsifiable success test. A skill supplies capability; it
   never supplies authority.
8. **Wire lightweight adapters.** Use only the adapters the team needs. Keep the
   generated protected block identical across surfaces and surface-specific workflow
   details outside it. Run the deterministic drift check.
9. **Isolate mutation.** Require one branch/worktree and resource namespace per
   mutating lane. Read-only reviewers may share. Only the integration owner assembles
   pinned lane commits in a clean worktree.
10. **Bind evidence.** Instantiate both checkpoint and evidence-manifest assets for R2/R3.
    Retain exact base/candidate identity, commands, exit status, environment, data
    provenance, artifacts, reviewers, conditions, and rollback. Any candidate change
    invalidates prior review.
11. **Enforce verdicts.** PASS means zero conditions. Conditional/amendment verdicts
    block until fixed and re-reviewed; REJECT/BLOCKING halts. Make any override an
    explicit operator path with a durable reason, never a passing reviewer token.
12. **Close the lifecycle.** Run focused and convergence gates, obtain independent
    review of the exact integrated candidate, deliver only with authority, observe the
    result, and reconcile status, changelog, HLD/runbooks, evidence, open risk, and
    rollback.

## Minimum mechanical controls

Implement controls proportionate to the project:

- a profile/adapter drift check;
- a protected-path gate that detects edits, modes, deletions, and renames;
- regression-first tests for defects;
- one convergence command for the assembled candidate;
- secret and dependency scanning;
- exact-snapshot review invalidation;
- post-delivery health/rollback checks.

Prefer a required remote check or signed attestation for high-risk approval. A local
hook is defence in depth and does not authenticate reviewer identity.

## Validation

Before completion:

1. Validate the distributed assets before adoption:

   ```bash
   python3 .agents/skills/operating-model-bootstrap/scripts/validate_operating_model.py \
     --template-root .agents/skills/operating-model-bootstrap
   ```

2. Validate an adopted seed. Before R2/R3, repeat with `--require-active` and pass the
   resolved checkpoint/evidence paths:

   ```bash
   python3 .agents/skills/operating-model-bootstrap/scripts/validate_operating_model.py \
     --target .
   python3 .agents/skills/operating-model-bootstrap/scripts/validate_operating_model.py \
     --target . --require-active \
     --checkpoint docs/operating-model/checkpoints/<task-id>.yaml \
     --evidence docs/operating-model/evidence/<task-id>.yaml
   ```

3. Verify all mutating lanes and external resources have one owner.
4. Change one adapter inside its protected block; confirm semantic drift fails.
5. Rename a protected file; confirm the project-specific protected-path gate catches it.
6. Change the candidate after review; confirm checkpoint/evidence binding fails or is stale.
7. Run the project's lint, type, test, security, and convergence commands.
8. Run the Adversarial Gate: name how authority, isolation, evidence, delivery, or
   observation could still fail silently.

## Required outputs

- Adopted universal manual with version/digest.
- Completed, tracked project operating profile.
- Lightweight surface adapters plus drift enforcement.
- Durable checkpoint for active R2/R3 work.
- Exact-candidate evidence manifest for active R2/R3 work.
- Validation evidence and explicitly owned unresolved platform/operator actions.
- Updated project status, changelog, and architecture/runbook documentation when the
  operating contract or delivery flow changes.

Do not claim complete enforcement while local checks remain bypassable, reviewer
identity is unauthenticated, credentials remain exposed, or delivery has not been
observed.
