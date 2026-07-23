# AI-Native Developer Experience Harness

> **A team-project AI harness bootstrap that gives humans and agents a shared operating contract from day one, moving AI leverage from an individual “IC superhero” advantage to a repeatable team capability on an equal playing field.**

This repository has gone through three real phases — and the progression tracks something
happening across the field.

It started as a **reference guide**: [`DEVELOPER_EXPERIENCE.md`](DEVELOPER_EXPERIENCE.md)
and [`BOOTSTRAP.md`](BOOTSTRAP.md), something to read, walk through, and adapt. A concrete
baseline for teams getting serious about AI-native delivery — the operating model, the
guardrails, spec-first discipline, the Adversarial Gate.

Then it became **context for your agents**: `CLAUDE.md` and `GEMINI.md` here, plus the
thin `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` adapters the bootstrap generates — drop them
into a project and the agent picks up the operating contract at session start without a
briefing. The harness shifted from something humans read to something agents use.

Now it ships as an **installable plugin** — `join-the-team` (v0.1.3). One install across
Claude Code, Codex, Kimi, and Antigravity, and the full harness is live: 19 skills,
session-start orientation, slash commands, drift-checked in CI. The discipline travels
with the agent from day one, across every project, without anyone copying files or
re-explaining the contract.

The point: this stopped being something you read and became something you install.

And what you install is the **operating model** — that is the value proposition here.
Skill libraries are everywhere now; what teams are missing is the contract: who holds
authority, how risk is tiered, what evidence binds a review, what "done" actually means
when humans and agents ship together. The 19 skills are the capability layer that
executes inside that contract — not the other way round.

The kernel stays model-, vendor-, and IDE-agnostic throughout. Thin platform adapters
handle discovery and invocation; the authority, risk, evidence, review, and completion
semantics are non-negotiable.

> **Speed is easy. Safe speed is engineered.**

> **This is deliberately opinionated.** Refine it for your team, technology, domain,
> authority model, and definition of done. Keep one coherent shared contract while doing so.

**New project?** [Bootstrap in fifteen minutes](BOOTSTRAP.md). **Existing agent setup?**
[Two ways to adopt](#two-ways-to-adopt) below — by hand, or as a plugin.

## Two ways to adopt

**By hand** — clone the repo and share it with your agents. Copy `.agents/skills/` into
your project, keep the `CLAUDE.md`/`GEMINI.md`/`AGENTS.md` adapters at root, and your
assistant picks up the contract at session start. [BOOTSTRAP.md](BOOTSTRAP.md) is the
fifteen-minute walkthrough.

```bash
git clone https://github.com/jpantsjoha/ai-native-developer-experience
```

**As a plugin** — the harness ships as `join-the-team` (v0.1.3): one canonical skill
set, thin per-harness adapters, drift-checked in CI. Install straight from this
repository into whichever coding assistant you run:

**Claude Code**

```text
/plugin marketplace add jpantsjoha/ai-native-developer-experience
/plugin install join-the-team@join-the-team-marketplace
```

**Kimi Code**

```text
/plugins install https://github.com/jpantsjoha/ai-native-developer-experience
```

**Antigravity (Gemini)**

```bash
agy plugin install https://github.com/jpantsjoha/ai-native-developer-experience
```

**Codex** — no install command needed: Codex discovers `.agents/skills/` natively and
reads `AGENTS.md` as its always-on adapter. The by-hand clone above is the install.

Full per-harness detail (session-start hooks, verification, update path):
[Claude Code](docs/install/claude.md) · [Kimi Code](docs/install/kimi.md) ·
[Codex](docs/install/codex.md) · [Antigravity](docs/install/antigravity.md)

Antigravity is a first-class surface: this harness was built and battle-tested on
Google Cloud's agent stack, and ships cloud-expert guardrails (`gcp-expert`,
`aws-expert`, `azure-expert`, `alibaba-expert`) plus `adk-expert` and
`mcp-server-scaffold` alongside the vendor-neutral contract.

The plugin composes with — never duplicates — companion skill plugins;
see [INTEGRATIONS.md](INTEGRATIONS.md).

---

## The Hybrid Human-AI Squad Model & Workflow

Installing the harness gets you the skills. What it doesn't give you is the operating
model — who decides, who executes, what counts as done, where the escalation circuit
breakers sit. This is that model.

Moving from an individual "copilot user" to a team delivering value requires shifting from ad-hoc prompting to a **governed value stream**. In this model, **AI agents and harness skills scale execution velocity**, while **named human Subject Matter Experts (SMEs) retain non-delegable accountability** for decisions, governance, and production state.

```mermaid
sequenceDiagram
    autonumber
    actor PO as Product Owner (Human SME)
    participant Orch as delivery-orchestrator (AI Workflow)
    participant SpecArch as spec-first & the-architect (AI Skills)
    actor SME as Human SME Roster (Architect / Data / Delivery Lead)
    participant Lanes as Agent Execution Lanes (AI Agents & Hooks)
    participant Gates as domain-validator & adversarial-gate (AI Gates)
    actor Ops as Operations / SRE (Human SME)

    rect rgb(238, 242, 255)
        note over PO,SpecArch: Phase 1: Intake & Acceptance Contracts (Human Intent & AI Spec)
        PO->>Orch: 1. Submit Epic / Feature Intent
        Orch->>SpecArch: 2. Route Work & Draft Contracts
        SpecArch-->>Orch: 3. Return Acceptance Contract & ADRs
    end

    rect rgb(252, 231, 243)
        note over Orch,SME: Phase 2: Risk Governance & Escalation Circuit Breaker (Human SME Authority)
        Orch->>Orch: Classify Risk Tier (R0-R3) & Check Evidence
        alt Missing Evidence or High-Risk (R2/R3)
            Orch-->>SME: LANE HALT: Tag Accountable Human SME
            SME->>Orch: Approve Authority Grant & Sign Decision Record (ADR)
        end
    end

    rect rgb(240, 253, 244)
        note over Orch,Gates: Phase 3: Agent Task Execution & Red-Team Pass (AI Execution Lanes)
        Orch->>Lanes: 4. Dispatch Discrete Tasks to Mutating Lanes (R0/R1 Scoped)
        Lanes->>Gates: 5. Execute Code & Run Red-Team Pass ("How would I break this?")
        Gates-->>Lanes: 6. Pass Verification & Bind Exact-Candidate SHA
    end

    rect rgb(224, 242, 254)
        note over Lanes,Ops: Phase 4: Release Readiness & Derived Receipts (Human Sign-off & Audit)
        Lanes->>Ops: 7. Submit Candidate Release Check (pr-reviewer & release-readiness)
        Ops-->>Lanes: 8. Authorise Production Deployment
        Lanes-->>PO: 9. Deploy & Emit Derived Status (sitrep)
    end
```

### Accountabilities: Human Squad vs. AI Harness

Skills supply capability; **named humans supply authority**.

| Delivery Stage | Primary AI Skill / Harness Primitive | AI Agent Capability | Accountable Human SME |
| :--- | :--- | :--- | :--- |
| **Requirements & Scope** | `spec-first-delivery` | Drafts acceptance contract & spec | **Product Owner** |
| **Architecture & ADRs** | `the-architect`, `cloud-experts` | Drafts ADRs & validates vendor constraints | **Lead Architect / Head of Eng** |
| **Data & Access Seams** | `mcp-server-scaffold` | Queries governed MCP data seams | **Head of Data / Security** |
| **Risk & Authority** | `using-the-harness` | Classifies risk tier (R0–R3) | **Delivery Manager / Lead** |
| **Verification & Red-Teaming** | `adversarial-gate`, `make check` | Runs red-team checks & test suite | **Lead Developer** |
| **Release & Rollback** | `release-readiness` | Validates deployment readiness | **Operations / SRE** |
| **Status & Receipts** | `sitrep` | Synthesises status from git artifacts | **Delivery Manager** |

### Core Operating Invariants

- **Capabilities scale velocity; Authority remains human**: AI agents draft code, specs, and execution plans, but named humans approve decisions at declared risk tiers.
- **The Escalation Circuit Breaker ("Silence never converts to permission")**: When evidence is missing or work touches R2/R3 risk, the execution lane halts and tags the human owner.
- **Receipts over polish**: Done means checks pass (`make check`), evidence manifests bind to exact commit SHAs, and status is derived from artifacts, not prose.

---

## Licence

This repository is open source under the [Apache License, Version 2.0](LICENSE) — free for personal and commercial use, modification, and redistribution.

The plugin's data-handling statement is available in the [Privacy Policy](docs/PRIVACY.md).

Attribution is part of the deal: derivative works must carry the [NOTICE](NOTICE)
file (Apache-2.0 §4(d)), which credits the author and this project's origin. The repository contains no usage telemetry; the licence cannot identify silent use. Stars, feedback, and voluntary adoption notes are welcome evidence that the harness is useful, but they are not licence conditions.

## This repo is about

- A **living DevEx harness** for AI-augmented development.
- A record of **what worked** in firsthand delivery experience.
- A set of **minimum viable guardrails** for agent-driven workflows.
- An opinionated baseline designed for team refinement.

Hyper-personalised workflows are inevitable; this is one of many. Shared contracts,
validation, and discipline remain essential.

## Where the harness came from

I’ve been building and writing under the banner of **#HarnessEngineering** for a while now — the idea that the model is the easy, commoditised part - relatively speaking, and the durable engineering lives in the scaffolding you wrap around it. So the rule files, the tools and MCP servers, the sandboxes, the orchestration, the hooks, the evals. This repo is the firsthand version of that argument — a reflection of over a year working hands-on across a variety of agent systems, coding copilots, and orchestrated multi-agent delivery.

If you want the narrative rather than the code, the write-ups that unpack this harness live here:

- **Part 2 — [Harness Engineering with Google Antigravity](https://medium.com/google-cloud/the-ai-native-developer-experience-part-2-harness-engineering-with-google-antigravity-7fb72dab243f)** (Medium, Google Cloud Community) — one harness across three surfaces: the IDE, the Agent Manager, the CLI.
- **Companion — [Supercharging Your Harness: Skills, Rules and MCP with Google Antigravity](https://itnext.io/supercharging-your-harness-skills-rules-and-mcp-with-google-antigravity-d2142e61c4fd)** (ITNEXT) — how the Skills, Rules and MCP primitives in this repo actually come together to make the harness invocable.

The broader industry is converging on similar language. One useful marker is Google’s
2026 paper [“The New SDLC With Vibe Coding: From ad-hoc prompting to Agentic
Engineering”](https://www.kaggle.com/whitepaper-the-new-SDLC-with-vibe-coding) by Addy Osmani, Shubham Saboo, and Sokratis Kartakis.

A few related themes and external signals line up with what this repository has been
saying from the field:

- **The harness can dominate the experience.** “10% model / 90% harness” is a useful
  engineering heuristic, not a universal measured ratio. The practical point is to debug
  tools, context, rules, permissions, and feedback loops as first-class system components.
- **Many apparent model failures are harness failures.** Missing tools, vague rules,
  absent guardrails, poor context, and weak validation are common, actionable causes. This
  is a field observation, not a claim that every failure has the same root cause.
- **The harness effect can be measured.** LangChain reported improving Deep Agents from
  52.8 to 66.5 on Terminal Bench 2.0 through harness changes, moving from outside the Top
  30 to the Top 5 at that time. Treat the result and rank as a historical experiment, not
  a permanent benchmark fact. See [LangChain’s experiment](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)
  and the [current Terminal Bench leaderboard](https://www.tbench.ai/leaderboard/terminal-bench/2.0).
- **Adoption is widespread, but measurements differ.** Surveys often mix AI tools,
  coding assistants, and agents, so this repo does not turn tool-use percentages into an
  “agent adoption” or “AI-generated code” claim. See the [JetBrains 2025 ecosystem
  report](https://blog.jetbrains.com/research/2025/10/state-of-developer-ecosystem-2025/) and [Stack Overflow 2025 survey](https://survey.stackoverflow.co/2025/ai).
- **The role is shifting from syntax to intent** — from writing code to specifying, verifying, and directing — with “intent as the new interface” as the destination.

Basically, **read that report.**

## Patterns worth borrowing: agent-skills convergence

Addy Osmani followed the paper with a practical artifact — **[agent-skills](https://github.com/addyosmani/agent-skills)** (MIT), 24 SKILL.md workflows encoding SDLC discipline for coding agents. I reviewed the lot against this harness. Most of it my setup (or your agent CLI of choice) already does natively. Four patterns are genuinely worth lifting, and they slot straight into the harness thinking above:

1. **Anti-rationalization tables.** Every skill ships a table of the excuses an agent makes to skip a step — paired with the rebuttal. This is a harness primitive I had not formalised: my gates ban bad *output*; this pattern pre-empts bad *reasoning* before the output exists. If you maintain your own skills, add one of these tables to each. Cheap to write, compounds fast.
2. **Doubt-driven development.** Adversarial in-flight review of high-stakes decisions — the agent must argue against its own approach before proceeding. I've been running this as the **Adversarial Gate** ("how would i break this?") since the start of this harness. Good to see the industry converge on the same move. If you only borrow one behavioural pattern, borrow this one.
3. **A meta-router skill.** As a skill library grows, the agent needs explicit routing.
   This harness implements that capability in `delivery-orchestrator`; the operating
   profile then maps capability names to whichever invocation syntax the team uses.
4. **Exit criteria over aspirational guidance.** The repo's quiet philosophy: process over prose. A skill that says "ensure quality" is decoration; a skill that says "done means these three checks pass" is a harness. Same discriminator i keep landing on everywhere: receipts, not polish.

Borrow the patterns. As ever — your mileage may vary.

## What’s inside this repo

- **[BOOTSTRAP.md](BOOTSTRAP.md)**
  The drop-in, fifteen-minute path for a new team project.
- **[DEVELOPER_EXPERIENCE.md](DEVELOPER_EXPERIENCE.md)** (DX-001)
  The main guide covering guardrails, workflows, validation, spec-driven delivery, and AI-agent integration — the mechanics.
- **[Agent Skills Library](.agents/skills/README.md)**
  Eighteen tracked capabilities for orchestration, architecture, specification, validation,
  review, release readiness, plugin submission, status, cost, and selected platform work.
- **[Plugin Submission](.agents/skills/plugin-submission/SKILL.md)**
  The policy-backed directory and marketplace listing gate; its
  [capability specification](docs/PLUGIN-SUBMISSION.md) defines the external-send
  confirmation and receipt contract.
- **[Operating Model Bootstrap](.agents/skills/operating-model-bootstrap/SKILL.md)**
  A reusable released manual, project profile, checkpoint, evidence manifest, and thin
  agent-surface adapters for assigning authority, isolating parallel human/agent lanes,
  binding review to an exact candidate, and carrying work through delivery, observation,
  and honest completion.
- **[Companion Plugins](INTEGRATIONS.md)**
  The evaluated companion-plugin map: agent-craft lanes (TDD methodology, simplicity
  discipline, frontend design) route to installed sister plugins; the team contract
  stays canonical here. Reference, never vendor.
- **[Team Workflow](docs/WORKFLOW.md)**
  The skills dependency diagram, the requirement → ADR → ticket → evidence → status
  traceability chain, and the accountability model: how skills route work while named
  humans hold authority.
- **[CHANGELOG.md](CHANGELOG.md)**
  Material changes, narrow public-source attribution, and known usage limitations.

This repository is expected to **evolve** as tools, models, and workflows change. Dated
facts and prices are snapshots; verify them before making a current decision.

## Projects that helped shape this harness

These ideas were not written in isolation — they were forged while building, shipping, breaking, and iterating on real systems using AI-assisted and agent-driven workflows. (Besides my own delivery experience in the field)

### My Hackathons and Builds

- **[Devpost — project & hackathon portfolio](https://devpost.com/jpantsjoha/achievements)**
  My running track record of things I’ve designed, built, and shipped — hackathon entries, prototypes, and production tools. The proof-of-work behind the opinions in this harness.

### Chrome Apps

- **[Simple Focus Mode – Chrome Extension](https://github.com/jpantsjoha/simple-focus-chromeExt)**
  A minimalist Pomodoro-style productivity extension focused on intentional work and reduced distraction.
  Built as a fast-feedback experiment in shipping, UX constraints, and iterative delivery.
  Related write-up:

  - https://medium.com/devops-dudes/simple-focus-mode-boost-your-productivity-with-my-chrome-extension-3f5cf0f7b843
- **[C4X – C4 Model Diagrams for VS Code](https://marketplace.visualstudio.com/items?itemName=jpantsjoha.c4x)**
  A VS Code extension for authoring and visualising C4 architecture diagrams with AI-assisted generation and live preview.
  Used to explore developer experience, documentation-as-code, and AI-assisted design workflows.
  Additional links:

  - Open VSX: https://open-vsx.org/extension/jpantsjoha/c4x
  - Source: https://github.com/jpantsjoha/c4x-vscode-extension
  - Build story: https://medium.com/google-cloud/how-i-built-the-c4x-antigravity-ide-extension-with-googles-gemini-3-6feb74f8a4b2

### 🧠 Slack + Cloud AI

- **[BriefOps – Slack + Google Cloud AI Summarisation](https://github.com/jpantsjoha/briefops-public)**
  A Slack application leveraging Google Cloud and Vertex AI to summarise conversations, documents, and shared context.
  Used to explore agent-assisted knowledge extraction, permissions, governance, and delivery guardrails in a real SaaS workflow.
  Related article:
  - https://medium.com/google-cloud/slack-googlecloud-briefops-streamlining-slack-comms-with-gcp-ai-powered-summarisation-ec2151672731

## My Thoughts on this Agentic Ways of Working

- [The New Ways of Working: Leading with Agent-Powered Hybrid Teams](https://www.cognizant.com/uk/en/insights/blog/articles/the-new-ways-of-working-leading-with-agent-powered-hybrid-teams)
  The published thesis behind this harness, with reflection on hybrid human-and-agent teams, the harness over the model, machine-readable contracts, and orchestration as the new core skill, and more
- **Medium**: https://jaroslav-pantsjoha.medium.com  My GDE and Technical write-ups
  Typical subjects i cover:

  - Developer experience
  - Platform engineering
  - Cloud & AI delivery
  - Agentic workflows
  - Applied AI

Relevant posts will be cross-linked here as this harness evolves.

- [Supercharging Your Harness: Skills, Rules and MCP with Google Antigravity](https://itnext.io/supercharging-your-harness-skills-rules-and-mcp-with-google-antigravity-d2142e61c4fd) (ITNEXT) — how the Skills, Rules and MCP primitives come together to make the harness ship safe, consistent output.

## About the author

Created and maintained by **Jaroslav Pantsjoha** — Technical Director and Enterprise Agent Solution Architect, Google Developer Expert (Google Cloud), speaker, and consulting thought leader on AI systems and adoption. Prolific builder, learner, and the author of the **"Ways of Working and AI Adoption at the Enterprise"** series and two books:

- *Building the Agentic Enterprise on Google Cloud* (Packt) — a practical field guide to designing, deploying, and operating agentic AI systems.
- *Mastering Multi-Agent Systems on Google Cloud* (AVA Publishing, Co-Author with Anupam Phoghat) — build, deploy, and operate production agentic AI with ADK, Vertex AI, and the complete GCP stack.

- LinkedIn: [uk.linkedin.com/in/johas](https://uk.linkedin.com/in/johas)
- Google Developer Expert: [me.developers.google.com/u/jpantsjoha](https://me.developers.google.com/u/jpantsjoha)

Attribution requirements for copies and adaptations live in [NOTICE](NOTICE). The Adversarial Gate name and "how would I break this?" framing are his contribution to the #HarnessEngineering body of work.

## Status

This is an active, evolving project.
Expect revisions, additions, and corrections as tools and practices mature.

Feedback, discussion, and constructive disagreement are welcome.
