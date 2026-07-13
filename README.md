# AI-Native Developer Experience Harness

> **A team-project AI harness bootstrap that gives humans and agents a shared operating contract from day one, moving AI leverage from an individual “IC superhero” advantage to a repeatable team capability on an equal playing field.**

This is my personal, public example of the scaffolding, skills, operating model, and ways
of working I use to help a team start coherently in a new project direction. It is a
conversation starter and adaptable baseline, not a production application starter kit or
a claim that one process fits every team.

The operating-model kernel is model-, vendor-, and IDE-agnostic. Thin platform adapters
handle discovery and invocation without changing authority, risk, evidence, review, or
completion semantics.

**Start here:** [bootstrap a new team project](BOOTSTRAP.md), then adapt the tracked
project profile as the team learns.

> **Speed is easy. Safe speed is engineered.**

> **This is deliberately opinionated.** Refine it for your team, technology, domain,
> authority model, and definition of done. Keep one coherent shared contract while doing so.


---

## This repo is about

- A **living DX harness** for AI-augmented development.
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
Engineering”](https://www.kaggle.com/whitepaper-the-new-SDLC-with-vibe-coding) by Addy
Osmani, Shubham Saboo, and Sokratis Kartakis.

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
  report](https://blog.jetbrains.com/research/2025/10/state-of-developer-ecosystem-2025/)
  and [Stack Overflow 2025 survey](https://survey.stackoverflow.co/2025/ai).
- **The role is shifting from syntax to intent** — from writing code to specifying, verifying, and directing — with “intent as the new interface” as the destination.

Basically, read that report.


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
  Thirteen tracked capabilities for orchestration, architecture, specification, validation,
  review, release readiness, status, cost, and selected platform work.
- **[Operating Model Bootstrap](.agents/skills/operating-model-bootstrap/SKILL.md)**
  A reusable released manual, project profile, checkpoint, evidence manifest, and thin
  agent-surface adapters for assigning authority, isolating parallel human/agent lanes,
  binding review to an exact candidate, and carrying work through delivery, observation,
  and honest completion.
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



## Status

This is an active, evolving project.  
Expect revisions, additions, and corrections as tools and practices mature.

Feedback, discussion, and constructive disagreement are welcome.
