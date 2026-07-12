---
name: operating-model-bootstrap
description: Bootstrap or harden a project's operating model for mixed human and AI delivery teams. Use when starting a repository, adopting an agent harness, defining authority and risk tiers, coordinating parallel agents safely, binding evidence and review to an exact candidate, or correcting fragmented rules that prevent coherent, consistent, complete delivery.
---

# Operating Model Bootstrap

Establish a portable operating kernel and one tracked project profile. Treat humans,
agents, skills, tools, and gates as one delivery system with explicit authority,
ownership, evidence, and completion semantics.

## Load the templates

Read all three assets before editing the target project:

- `assets/OPERATING-MANUAL.template.md` — vendor-neutral normative kernel.
- `assets/PROJECT-OPERATING-PROFILE.template.md` — project-specific contract.
- `assets/CHECKPOINT.template.yaml` — durable state for R2/R3 work.

Do not copy project details into the universal manual. Do not leave profile
placeholders unresolved.

## Bootstrap workflow

1. **Ground the project.** Read its existing constitutions, architecture, delivery
   flow, test commands, deployment path, protected surfaces, and current state. List
   contradictions and stale claims before adding policy.
2. **Confirm authority.** Separate useful intent from permission. Obtain explicit
   approval before constitutional, destructive, credential, external, deployment,
   production-data, or capital changes.
3. **Classify risk.** Map project work into R0–R3. Round ambiguity upward. Name the
   highest-impact silent failure, rollback owner, and observation surface.
4. **Install the kernel.** Copy the universal template to the project's canonical
   governance location. Record version, digest, owner, adoption status, and review
   trigger.
5. **Complete the profile.** Fill every profile field with project facts: precedence,
   protected paths, invariants, authority roles, isolation, exact validation commands,
   data gates, reviewers, docs triggers, delivery/observation, rollback, budgets, and
   retention.
6. **Define the squad.** Assign one accountable human/operator, one integration owner,
   bounded mutating lanes, and independent reviewers. Give every lane owned files,
   owned resources, and a falsifiable success test. A skill supplies capability; it
   never supplies authority.
7. **Wire lightweight adapters.** Make `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or other
   surface files point to the same kernel/profile. Keep only surface-specific workflow
   details in adapters. Add a deterministic drift check for authority, risk invariants,
   version/digest, and critical current facts.
8. **Isolate mutation.** Require one branch/worktree and resource namespace per
   mutating lane. Read-only reviewers may share. Only the integration owner assembles
   pinned lane commits in a clean worktree.
9. **Bind evidence.** For R2/R3, retain exact base/candidate identity, commands, exit
   status, environment, data provenance, artifacts, reviewers, conditions, and
   rollback. Any candidate change invalidates prior review.
10. **Enforce verdicts.** PASS means zero conditions. Conditional/amendment verdicts
    block until fixed and re-reviewed; REJECT/BLOCKING halts. Make any override an
    explicit operator path with a durable reason, never a passing reviewer token.
11. **Close the lifecycle.** Run focused and convergence gates, obtain independent
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

1. Verify the universal manual contains no project, vendor, model, account, path, or
   secret-specific policy.
2. Verify every project-profile field is resolved and every command is runnable.
3. Verify all mutating lanes and external resources have one owner.
4. Change an adapter while retaining its marker; confirm semantic drift still fails.
5. Rename a protected file; confirm the source remains protected.
6. Change the candidate after review; confirm the evidence becomes stale.
7. Run the project's lint, type, test, security, and convergence commands.
8. Run the Adversarial Gate: name how authority, isolation, evidence, delivery, or
   observation could still fail silently.

## Required outputs

- Adopted universal manual with version/digest.
- Completed, tracked project operating profile.
- Lightweight surface adapters plus drift enforcement.
- Durable checkpoint for active R2/R3 work.
- Validation evidence and unresolved platform/operator actions.
- Updated project status, changelog, and architecture/runbook documentation when the
  operating contract or delivery flow changes.

Do not claim complete enforcement while local checks remain bypassable, reviewer
identity is unauthenticated, credentials remain exposed, or delivery has not been
observed.
