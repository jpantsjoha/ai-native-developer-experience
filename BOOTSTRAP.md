# Team Project AI Harness — Day-One Bootstrap

This is the shortest path from a new repository to a shared human–AI delivery contract.
It gives the team a common operating model and capability vocabulary before application
architecture and delivery details are known.

The goal is not to declare a blank project production-ready. The goal is to remove the
blank page around authority, risk, ownership, evidence, review, and completion so the team
can start system design and technical delivery planning coherently on day one.

## Fifteen-minute path

### 1. Put the baseline skills in the project

Copy this repository's `.agents/skills/` directory into the new repository. Keep it
tracked. The operating-model initializer and validator require Python 3.10 or newer but
have no package or provider SDK dependency; they use only the standard library.

If the chosen assistant does not discover `.agents/skills/` automatically, point its
project adapter or configuration at that directory. Skill discovery syntax is
surface-specific; the operating contract is not.

### 2. Preflight and initialise

Run from the new repository:

```bash
python3 .agents/skills/operating-model-bootstrap/scripts/bootstrap_operating_model.py \
  --dry-run --project-name "My Project" .
python3 .agents/skills/operating-model-bootstrap/scripts/bootstrap_operating_model.py \
  --project-name "My Project" .
```

The initializer creates:

- `docs/operating-model/OPERATING-MANUAL.md` — the unchanged, versioned kernel;
- `docs/operating-model/PROJECT-OPERATING-PROFILE.md` — the local day-one seed;
- `docs/operating-model/DELIVERY-WORKFLOW.md` — the project lifecycle and work-system
  mapping;
- `docs/VISION.md` — Product Owner outcome framing and initial focus;
- `docs/ROADMAP.md` and `docs/STATUS.md` — minimal, initially unpopulated delivery
  records;
- `CHANGELOG.md` — the project's material release history;
- checkpoint and evidence templates for consequential/protected work;
- thin `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` discovery adapters.

It computes and binds the manual SHA-256 and preflights the entire output set. Different
existing project planning records are preserved and only missing records are seeded;
conflicting operating contracts or surface adapters stop the initializer before it
writes. Select only required adapters with repeated `--surface agents`,
`--surface claude`, or `--surface gemini` options.

### 3. Give the assistant one grounding instruction

```text
Use $operating-model-bootstrap to ground this repository and complete its day-one seed.
Do not invent project facts. Resolve the day-one minimum from tracked evidence; record
unknowns with an owner and the trigger that must resolve them. Then use the architecture,
specification, and delivery-orchestration capabilities to propose the first system design
and technical delivery plan. Stop before any R2/R3 mutation or external action that lacks
explicit authority and runnable controls.
```

The assistant should inspect existing project facts, surface contradictions, populate the
minimum profile, route the initial skills, and leave decisions requiring the team explicit.

### 4. Validate the shared seed

```bash
python3 .agents/skills/operating-model-bootstrap/scripts/validate_operating_model.py \
  --target .
```

A seed may pass with warnings about unresolved project facts. That is enough for discovery,
architecture, ADRs, backlog formation, interface design, and R0/R1 work. Before R2/R3,
resolve applicable controls, set the profile to `active`, and validate again with
`--require-active` plus the task checkpoint/evidence paths.

## Baseline capability map

| Team need | Included skill |
|---|---|
| Shared operating contract | `operating-model-bootstrap` |
| Work decomposition and routing | `delivery-orchestrator` |
| System design and ADRs | `the-architect` |
| Requirements and acceptance criteria | `spec-first-delivery` |
| Adversarial self-review | `adversarial-gate` |
| Domain correctness | `domain-validator` |
| Exact-candidate review | `pr-reviewer` |
| Delivery and rollback readiness | `release-readiness` |
| Durable team state | `sitrep` |
| Cost/time discipline | `cost-guardrail` |

The remaining included skills add platform and specialist capabilities. A skill supplies a
repeatable procedure; it never supplies permission or accountability.

## Honest readiness boundary

This bootstrap formalises the shared baseline. It does not automatically:

- choose the product, architecture, language, framework, cloud, or deployment topology;
- discover facts that are absent from the repository and team;
- configure remote branch protection, secrets, CI identities, environments, or budgets;
- authenticate an independent reviewer or make a bypassable local check authoritative;
- make a seed profile sufficient for production, security, data, money, or destructive work.

Those are project decisions and controls. The profile makes their owners and activation
triggers visible so refinement strengthens one shared contract instead of creating a new
constitution for each person or code assistant.
