# AI-Native Developer Experience Harness

This repository captures how I think about **developer experience in an AI-powered world** — where AI agents are rapidly becoming part of the delivery team. This notion of the **Agentic Harness** - think of this as the opinionated scaffolding, ways of working, and hard-won patterns we wrap around the models so they actually ship safe, consistent, coherent and complete output of value, that you can scale - as you adopt this DevEx Agent-powered development within your Team.

The good news is that I battle-tested this version of rather opinionated harness myself several times and these further enhancements and improvements (and feedback from industry peers) should make this re-usable-enough for you to get started with.

With over 2 years of building, hacking, shipping, breaking, fixing, and refining real products and then finally proving, delivering value with this kit. Enjoy, Rinse and Repeat and let me know how this works for you and your team.

> **Speed is easy. Safe speed is engineered.**

> **This is opinionated, and it should be.** This Harness works for my team, shaped by my own delivery experience, defined by my requirements.
You may need to adjust to your team requirements, and expertise. I.e. your ways of working, your technology choices, your use cases, and your definition of done almost certainly will. Borrow the Patterns, but Your mileage may vary.


---

### This repo is about:
- A **living DX harness** for AI-augmented development
- A record of **what actually worked** in real delivery environments
- A set of **minimum viable guardrails** for agent-driven workflows
- Opinionated by design

Hyper-personalised workflows are inevitable. - my version here is one of many.
Shared contracts, validation, and discipline are not optional.



## Where The Harness came from

I’ve been building and writing under the banner of **#HarnessEngineering** for a while now — the idea that the model is the easy, commoditised part - relatively speaking, and the durable engineering lives in the scaffolding you wrap around it. So the rule files, the tools and MCP servers, the sandboxes, the orchestration, the hooks, the evals. This repo is the firsthand version of that argument — a reflection of over a year working hands-on across a variety of agent systems, coding copilots, and orchestrated multi-agent delivery.

The industry has now caught up to the same narrative, fast. The clearest recent marker is Google’s 2026 paper **“The New SDLC With Vibe Coding: From ad-hoc prompting to Agentic Engineering”** (Addy Osmani, Shubham Saboo, and Sokratis Kartakis).

A few of its headline findings in this report for your perusal, which line up closely with what this repo has been saying from the field:

- **The model is roughly 10% of a working agent; the harness is the other ~90%.** The behaviour you experience using Claude Code, Cursor, Codex, Gemini, or Cline is dominated by the harness, not the model underneath. **( i think its more 35:65 split but thats just me )**
- **Most agent failures are configuration failures.** Examined honestly, the cause is usually a missing tool, a vague rule, an absent guardrail, or a context window stuffed with noise — not the model.
- **The harness effect is measurable.** On Terminal Bench 2.0, one team moved a coding agent from outside the Top 30 to the Top 5 by changing *only the harness*, no model change; a separate LangChain study lifted an agent’s score by 13.7 points the same way.
- **Adoption is already mainstream.** As of early 2026, ~85% of professional developers regularly use AI coding agents, ~51% daily, and an estimated ~41% of new code is AI-generated.
- **The role is shifting from syntax to intent** — from writing code to specifying, verifying, and directing — with “intent as the new interface” as the destination.

Basically, read that report.


## What’s inside this repo

- **[DEVELOPER_EXPERIENCE.md](DEVELOPER_EXPERIENCE.md)** (DX-001)  
  The main guide covering guardrails, workflows, validation, spec-driven delivery, and AI-agent integration — the mechanics.

This repository is expected to **evolve** as tools, models, and workflows change.



## Projects that helped shaped this harness

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



## Status

This is an active, evolving project.  
Expect revisions, additions, and corrections as tools and practices mature.

Feedback, discussion, and constructive disagreement are welcome.
