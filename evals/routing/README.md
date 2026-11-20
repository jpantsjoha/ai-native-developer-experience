# Routing evaluation

Does a delivery ask enter through `delivery-orchestrator`, and does the right role then
load? Skill selection is a model decision, so the answer is a rate, not a guarantee.

## Method

- **Prompt set:** [`prompts.json`](prompts.json), version 1: 18 prompts, three from each of six
  kinds of people. Each names the role expected to do the work. Two are bounded read-only
  questions, which the rule allows to go straight to the specialist.
- **Run:** [`scripts/routing_eval.py`](../../scripts/routing_eval.py) runs each prompt
  headless in a copy of [`fixture/`](fixture/) with only one checkout's skills available.
- **Claude Code:** the checkout is the only plugin, with no user settings or user skills;
  writes and shell are denied; 10 turns. A skill is loaded when its skill call returns
  without error.
- **Codex:** the skills sit at project scope (`.agents/skills/`), the Codex home holds only
  the sign-in, `HOME` is an empty directory so user skills take no part, and the sandbox is
  read-only. The recorded runs predate the `HOME` change; they ran on a machine with no
  `~/.agents/skills` directory. Codex has no session-start hook, so nothing
  points it at the orchestrator except the skill descriptions. A skill is loaded when a
  command reads its `SKILL.md` and the skill's name appears in the output.
- A run that does not end normally scores nothing.

| Measure | Meaning |
|---|---|
| Orchestrator first | The first skill loaded, other than `using-the-harness`, is `delivery-orchestrator` |
| Direct specialist | A read-only prompt whose first skill is its expected specialist |
| Role reached | The expected role's skill loaded |
| No skill after orientation | Nothing loaded, or only `using-the-harness` |
| No skill at all | Nothing loaded |

```bash
python3 scripts/routing_eval.py --label claude-code-after --max-turns 10
python3 scripts/routing_eval.py --host codex --label codex-after
```

## Results

Counts out of 18, one run per prompt, 2026-11-20.

| Run | Model | Commit tested | `skills` tree | Valid runs | Orchestrator first | Direct specialist | Role reached | No skill after orientation | No skill at all |
|---|---|---|---|---|---|---|---|---|---|
| Claude Code, before | `sonnet` | `d155127` | `1611628f6f20` | 18 | 1 | 1 | 9 | 9 | 8 |
| Claude Code, after | `sonnet` | `0424324` | `18360154f373` | 18 | 16 | 1 | 17 | 1 | 1 |
| Codex, before | `gpt-6.1-sol` | `d155127` | `1611628f6f20` | 18 | 1 | 2 | 17 | 0 | 0 |
| Codex, after | `gpt-6.1-sol` | `86b32fe` | `18360154f373` | 18 | 17 | 1 | 18 | 0 | 0 |

The tree id is `git rev-parse <commit>:skills`; a later commit with the same id carries the
same skills. Raw results, with full ids: [`results/`](results/).

What the two hosts show:

- Before the change, Claude Code loaded no skill beyond orientation for 9 prompts, and
  none at all for 8. Codex loaded a
  specialist for every prompt and reached the expected role for 17, but entered through the
  orchestrator once.
- After the change, both hosts enter through the orchestrator and then load the role.
- Codex loads more skills per ask than the role table calls for, `operating-model-bootstrap`
  among them, because the fixture project has not adopted the operating model.

### Claude Code

| Id | Person | Prompt | Expected role | Loaded before | Loaded after |
|---|---|---|---|---|---|
| solo-1 | Solo owner | Let's get the sign-up milestone finished. What's left and what do we do next? | `sitrep` | using-the-harness | delivery-orchestrator → sitrep |
| solo-2 | Solo owner | Create a ticket for adding password reset to the sign-up flow. | `spec-first-delivery` | none | delivery-orchestrator → spec-first-delivery |
| solo-3 | Solo owner | I want to add billing with Stripe next. Plan it. | `spec-first-delivery` | none | delivery-orchestrator → spec-first-delivery |
| po-1 | Product owner | Users are dropping off at email verification. I want that fixed as the next priority. | `product-owner` | none | delivery-orchestrator → product-owner |
| po-2 | Product owner | Is the sign-up journey still aligned with our vision and acceptance criteria? | `product-owner` | product-owner | delivery-orchestrator → product-owner |
| po-3 | Product owner | Change the requirement: sign-up must work with Google login as well. | `product-owner` | product-owner | delivery-orchestrator → product-owner |
| dd-1 | Delivery director | Where are we on the sign-up milestone, and what's blocked? | `sitrep` | none | delivery-orchestrator → sitrep |
| dd-2 | Delivery director | What's waiting on me this week? | `sitrep` | sitrep | delivery-orchestrator → sitrep |
| dd-3 | Delivery director | Are we on track to ship M1? Show me the golden thread from goal to tickets. | `sitrep` | none | delivery-orchestrator → sitrep |
| tl-1 | Technical lead | Should we move session storage from Postgres to Redis? I need a decision recorded. | `the-architect` | the-architect | delivery-orchestrator → the-architect |
| tl-2 | Technical lead | Review the open pull request for the sign-up form before we merge. | `pr-reviewer` | none | delivery-orchestrator → pr-reviewer |
| tl-3 | Technical lead | Break the billing epic into tasks the agents can run in parallel. | `delivery-orchestrator` | delivery-orchestrator | delivery-orchestrator |
| qa-1 | QA lead | How do we prove the sign-up flow actually works before we call it done? | `test-strategy` | test-strategy | delivery-orchestrator → test-strategy |
| qa-2 | QA lead | What's our definition of done for email verification, and what evidence do we have? | `test-strategy` | none | delivery-orchestrator → test-strategy |
| qa-3 | QA lead | I don't trust the green test run. Try to break the sign-up flow. | `adversarial-gate` | adversarial-gate | delivery-orchestrator → adversarial-gate |
| sre-1 | Data or SRE specialist | Is everything live in production? Any errors this week? | `cloud-checkup` (direct allowed) | cloud-checkup | cloud-checkup |
| sre-2 | Data or SRE specialist | Are we ready to release M1 to production on Friday? | `release-readiness` | release-readiness | delivery-orchestrator → release-readiness |
| sre-3 | Data or SRE specialist | What will the LLM calls in the support bot cost us per month? | `cost-guardrail` (direct allowed) | none | none |

### Codex

| Id | Person | Prompt | Expected role | Loaded before | Loaded after |
|---|---|---|---|---|---|
| solo-1 | Solo owner | Let's get the sign-up milestone finished. What's left and what do we do next? | `sitrep` | using-the-harness → sitrep | using-the-harness → delivery-orchestrator → sitrep → operating-model-bootstrap |
| solo-2 | Solo owner | Create a ticket for adding password reset to the sign-up flow. | `spec-first-delivery` | using-the-harness → product-owner → github-manager → adversarial-gate | using-the-harness → delivery-orchestrator → spec-first-delivery → product-owner |
| solo-3 | Solo owner | I want to add billing with Stripe next. Plan it. | `spec-first-delivery` | using-the-harness → spec-first-delivery → product-owner → the-architect → adversarial-gate → test-strategy → governance-guardrail → delivery-orchestrator | using-the-harness → delivery-orchestrator → spec-first-delivery → operating-model-bootstrap → the-architect → test-strategy → adversarial-gate |
| po-1 | Product owner | Users are dropping off at email verification. I want that fixed as the next priority. | `product-owner` | using-the-harness → product-owner → adversarial-gate | using-the-harness → delivery-orchestrator → product-owner → spec-first-delivery → operating-model-bootstrap |
| po-2 | Product owner | Is the sign-up journey still aligned with our vision and acceptance criteria? | `product-owner` | using-the-harness → product-owner → adversarial-gate | using-the-harness → delivery-orchestrator → product-owner → test-strategy |
| po-3 | Product owner | Change the requirement: sign-up must work with Google login as well. | `product-owner` | using-the-harness → product-owner | using-the-harness → delivery-orchestrator → product-owner |
| dd-1 | Delivery director | Where are we on the sign-up milestone, and what's blocked? | `sitrep` | using-the-harness → sitrep | using-the-harness → delivery-orchestrator → sitrep |
| dd-2 | Delivery director | What's waiting on me this week? | `sitrep` | sitrep → using-the-harness → adversarial-gate | using-the-harness → delivery-orchestrator → sitrep |
| dd-3 | Delivery director | Are we on track to ship M1? Show me the golden thread from goal to tickets. | `sitrep` | using-the-harness → sitrep | using-the-harness → delivery-orchestrator → sitrep |
| tl-1 | Technical lead | Should we move session storage from Postgres to Redis? I need a decision recorded. | `the-architect` | using-the-harness → the-architect → adversarial-gate | using-the-harness → delivery-orchestrator → the-architect → adversarial-gate → operating-model-bootstrap |
| tl-2 | Technical lead | Review the open pull request for the sign-up form before we merge. | `pr-reviewer` | using-the-harness → pr-reviewer → adversarial-gate | using-the-harness → delivery-orchestrator → pr-reviewer |
| tl-3 | Technical lead | Break the billing epic into tasks the agents can run in parallel. | `delivery-orchestrator` | using-the-harness → delivery-orchestrator → spec-first-delivery → adversarial-gate | using-the-harness → delivery-orchestrator → spec-first-delivery → operating-model-bootstrap → test-strategy → adversarial-gate |
| qa-1 | QA lead | How do we prove the sign-up flow actually works before we call it done? | `test-strategy` | using-the-harness → test-strategy | using-the-harness → delivery-orchestrator → test-strategy |
| qa-2 | QA lead | What's our definition of done for email verification, and what evidence do we have? | `test-strategy` | using-the-harness → sitrep → test-strategy | using-the-harness → delivery-orchestrator → test-strategy |
| qa-3 | QA lead | I don't trust the green test run. Try to break the sign-up flow. | `adversarial-gate` | using-the-harness → adversarial-gate → test-strategy | using-the-harness → delivery-orchestrator → adversarial-gate → test-strategy |
| sre-1 | Data or SRE specialist | Is everything live in production? Any errors this week? | `cloud-checkup` (direct allowed) | using-the-harness → cloud-checkup → adversarial-gate | using-the-harness → cloud-checkup |
| sre-2 | Data or SRE specialist | Are we ready to release M1 to production on Friday? | `release-readiness` | using-the-harness → release-readiness → adversarial-gate | using-the-harness → delivery-orchestrator → release-readiness |
| sre-3 | Data or SRE specialist | What will the LLM calls in the support bot cost us per month? | `cost-guardrail` (direct allowed) | using-the-harness → cost-guardrail → adversarial-gate | using-the-harness → delivery-orchestrator → cost-guardrail |

## Limits

- One run per prompt. Counts from 18 single runs are an indication; the same prompt can
  route differently on a second run, and repeat runs would give a spread.
- Two hosts. Other hosts are not measured.
- The fixture is an unadopted project with three small records. An adopted project with a
  profile and workflow is not yet measured.
- The prompts were written by the author of the change. A prompt set written by someone
  else is a fairer test.
- An earlier, uncommitted version of the changed skills entered through the orchestrator
  on Claude Code but reached the expected role for only 4 prompts: the orchestrator
  answered from its own file. The "Bring the role in" section was added in response. That
  run is not in `results/`.
