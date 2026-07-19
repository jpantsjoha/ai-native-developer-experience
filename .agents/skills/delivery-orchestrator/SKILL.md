---
name: delivery-orchestrator
description: Decompose an epic into atomic parallelizable tasks and route each task to the right skill. Use this as a meta-router when you have more than one skill available and need to decide which applies. Trigger at the start of any multi-track epic or when the skill count in your harness exceeds ~12.
---

# Delivery Orchestrator

> **A skill for choosing skills.** Once your harness grows past a handful of skills, the agent needs a way to select the right one. This is that skill.

The orchestrator has two jobs: decompose work into the smallest independently executable units, then route each unit to the skill that owns it.

## When to use

- Starting a new epic or multi-track piece of work
- When an agent is about to attempt everything in one context window
- When parallel execution across multiple agents is needed
- When you need to decide which skill applies to an incoming task

## Procedure

### Part 1 — Decomposition

1. **Read the spec or brief** — confirm a feature spec or HLD exists. If not, invoke `spec-first-delivery` first.
2. **Identify tracks** — group work into independent tracks (e.g. backend API, frontend, infrastructure, testing). Tracks can run in parallel. Dependencies between tracks must be explicit.
3. **Break each track into atomic tasks** — an atomic task is one that:
   - Can be assigned to a single agent
   - Has a clear input and a clear output
   - Does not require coordination with another concurrent task to complete
   - Can be validated independently
4. **Sequence dependencies** — where task B requires output from task A, mark the dependency. Everything else is parallel.
5. **Assign context boundaries** — each agent gets only the context it needs. Avoid stuffing all specs into every agent's context.

### Part 2 — Skill routing

1. **Map each task to a skill** using the routing table below. If no skill matches exactly, use the closest and note the gap.
2. **Validate integration after parallel work** — run the full regression suite (`make validate-regression-suite` or equivalent) after all parallel tracks complete. Parallel work that skips integration validation is not done.

## Skill routing table

| Task type | Route to skill |
|---|---|
| New feature / epic planning | `spec-first-delivery` |
| Architecture decision or trade-off | `the-architect` |
| High-stakes design review | `adversarial-gate` |
| Pre-deployment go/no-go | `release-readiness` |
| Google ADK agent patterns | `adk-expert` |
| Cloud infrastructure guardrails | `gcp-expert` / `aws-expert` / `azure-expert` / `alibaba-expert` |
| MCP server design or governance | `mcp-server-scaffold` |
| Agent output validation | `domain-validator` |
| PR or code review | `pr-reviewer` |
| LLM cost or model selection | `cost-guardrail` |
| Status or standup synthesis | `sitrep` |
| Routing this list | `delivery-orchestrator` (you are here) |

## Outputs

- Task breakdown: tracks, atomic tasks, dependencies
- Skill routing: task → skill mapping
- Parallel execution plan with integration validation step
- A brief orchestration summary for the human lead

## Guardrails

- **Atomic means independently validatable.** If you cannot describe how to verify a task in isolation, it is not atomic — split it further or merge it with its dependency.
- **Parallel agents must not share mutable state without a coordination strategy.** If two tracks write to the same file or schema, they are not independent. Use worktrees or serialise them.
- **Integration validation is not optional.** Parallel work that skips the post-merge regression check is not complete.
- **Keep agent context lean.** Each agent gets its task spec and relevant ADRs, not the entire repo.
