# AI-Native Developer Experience (DevEX) Playbook

This repository captures how I think about **developer experience in an AI-augmented world** — where AI agents are part of the delivery team, not just productivity tools.

Over the last few months, I’ve been actively building, shipping, breaking, fixing, and refining real products using AI agents (Gemini, Claude, MCP tooling) inside constrained, enterprise-grade environments.

> **Speed is easy. Safe speed is engineered.**

---

### This repo is about:
- A **living DX playbook** for AI-augmented development
- A record of **what actually worked** in real delivery environments
- A set of **minimum viable guardrails** for agent-driven workflows
- Opinionated by design

Hyper-personalised workflows are inevitable.  
Shared contracts, validation, and discipline are not optional.

---

## Core principles

- **AI agents amplify your system** — [good or bad](https://cloud.google.com/resources/content/2025-dora-ai-assisted-software-development-report)
- **Developer experience is now a control surface**
- **Parallelism requires validation, lots of it**
- **Specs, tests, and Makefiles beat vibes**
- **Documentation is executable context**

---

## What’s inside

- **`DEVELOPER_EXPERIENCE.md`**  
  The main guide covering guardrails, workflows, validation, spec-driven delivery, and AI-agent integration.

- Future additions will cover:
  - Agent guardrails and failure modes
  - Parallel agent execution patterns
  - Spec → Plan → Tasks pipelines
  - DX patterns that scale beyond a single team

This repository is expected to **evolve** as tools, models, and workflows change.

---

## Real projects that shaped this playbook

These ideas were not written in isolation — they were forged while building, shipping, breaking, and iterating on real systems using AI-assisted and agent-driven workflows.

### 🧩 Chrome Extensions

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


## Writing & thought leadership

This repository complements longer-form writing where these ideas are explored narratively:

- **Medium**: https://jaroslav-pantsjoha.medium.com  

Topics include:
- Developer experience
- Platform engineering
- Cloud & AI delivery
- Agentic workflows
- Applied (not theoretical) AI

Relevant posts will be cross-linked here as this playbook evolves.

---

## How to use this repository

- **As a reference** — borrow patterns, not dogma
- **As a starting point** — adapt guardrails to your constraints
- **As a discussion tool** — developer experience is a team sport
- **As a living document** — revisit as the ecosystem changes

If AI agents are now part of your delivery model,  
**your developer experience *is* your control plane.**

---

## Status

This is an active, evolving project.  
Expect revisions, additions, and corrections as tools and practices mature.

Feedback, discussion, and constructive disagreement are welcome.
