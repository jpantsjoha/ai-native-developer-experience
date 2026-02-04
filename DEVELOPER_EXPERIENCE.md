# Developer Experience Guide


 - **Document ID**: DX-001
 - **Author**: Jaroslav Pantsjoha
 - **Version**: 1.0.0  
 - **Last Updated**: 2026-02-04  
 - **Pricing Verified**: 2026-02-04 (Gemini 3 Flash $0.50/$3.00, Gemini 3 Pro $2.00/$12.00 - Preview)  
 - **Audience**: Developers adopting AI-augmented development workflows  
 - **Purpose**: Bootstrap new team members to deliver rapid value from day one
---

## Table of Contents

1. [Introduction](#introduction)
2. [Development Philosophy](#development-philosophy)
3. [AI-Assisted Development Workflow](#ai-assisted-development-workflow)
4. [MCP Tools Configuration](#mcp-tools-configuration)
5. [Three Musketeers Pattern](#three-musketeers-pattern)
6. [Pre-Commit Hooks](#pre-commit-hooks)
7. [Testing & Validation](#testing--validation)
8. [Branch-Based Development](#branch-based-development)
9. [Spec-Driven Development](#spec-driven-development)
10. [Project Tracking](#project-tracking)
11. [Quick Reference](#quick-reference)

---

## Introduction

This guide documents an **AI-augmented development workflow** that combines human expertise with AI agents to accelerate delivery while maintaining quality.

### Core Principles

1. **Parallel Execution**: Use AI agents for independent tasks, humans for decisions
2. **Validation First**: Every change must pass automated gates before commit
3. **Documentation as Code**: ADRs, specs, and roadmaps are living documents
4. **Trunk-Based + Feature Branches**: Short-lived branches, frequent merges

---

## Development Philosophy

### Development Stance

Every feature, bug fix, and refactor should answer: **"Does this add measurable value to the product and its users?"**

### Quality Gates

No code merges to `main` without passing all gates:

| Gate              | Command          | Benefit                                         |
| ----------------- | ---------------- | ----------------------------------------------- |
| **Linting**       | `make lint`      | Code style consistency, catches common errors   |
| **Type Checking** | `make typecheck` | Static type validation, prevents runtime errors |
| **Unit Tests**    | `make test`      | Fast feedback, component isolation              |
| **E2E Tests**     | `make e2e`       | User journey validation, integration confidence |
| **Documentation** | ADR or commit    | Captures "why" for future maintainers           |

### Branch Protection Rules

The `main` branch is protected with these enforced rules:

| Rule                            | Purpose                                |
| ------------------------------- | -------------------------------------- |
| **Require PR reviews**          | At least 1 approval before merge       |
| **Require status checks**       | CI must pass (tests, lint, typecheck)  |
| **Require up-to-date branches** | Must be rebased on latest `main`       |
| **No force pushes**             | History is immutable                   |
| **No deletions**                | `main` cannot be deleted               |
| **Dismiss stale reviews**       | New commits invalidate prior approvals |

**Configuring via `gh` CLI**:

```bash
gh api repos/{owner}/{repo}/branches/main/protection \
  -X PUT \
  -F required_status_checks='{"strict":true,"contexts":["test","lint","typecheck"]}' \
  -F enforce_admins=true \
  -F required_pull_request_reviews='{"required_approving_review_count":1}'
```

---

## AI-Assisted Development Workflow

This guide covers **two enterprise-grade AI CLIs** for development. Both connect through enterprise endpoints (Vertex AI), not personal subscriptions.

### AI CLI Comparison

| Capability              | Claude Code (Anthropic)           | Gemini CLI (Google)                  |
| ----------------------- | --------------------------------- | ------------------------------------ |
| **Enterprise Endpoint** | Vertex AI Claude                  | Vertex AI Gemini                     |
| **Context File**        | `CLAUDE.md`                       | `GEMINI.md`                          |
| **Configuration**       | `~/.claude/settings.json`           | `~/.gemini/settings.json`              |
| **MCP Support**         | Built-in                          | Built-in                             |
| **Sub-Agents**          | Explore, Plan, QA Agents          | Orchestrator Plugin (multi-agent)    |
| **Background Tasks**    | ❌                                | ✅ Background Agents                 |
| **Custom Commands**     | Skills (slash commands)           | Slash commands                       |
| **Interactive Mode**    | Default                           | `/chat` or shell mode                |
| **Best For**            | Deep reasoning, complex refactors | Parallel workflows, GCP integrations |

### Claude Code (Primary)

Claude Code connects via **Vertex AI Enterprise** endpoint for enterprise-compliant consumption.

#### Agents & Subagents

| Agent Type               | Purpose                                      | When to Use                  |
| ------------------------ | -------------------------------------------- | ---------------------------- |
| **Main Agent**           | Primary conversation, orchestration          | Default interaction          |
| **Explore Agent**        | Codebase search, context gathering           | "Where is X implemented?"    |
| **Plan Agent**           | Architecture design, implementation planning | Before significant changes   |
| **QA Validation Agent**  | Post-implementation testing                  | After completing features    |
| **Docs Quality Auditor** | Documentation review                         | After creating/updating docs |

#### Model Selection

| Model                | Use Case                                               | Cost    |
| -------------------- | ------------------------------------------------------ | ------- |
| **Sonnet** (default) | 95% of tasks — implementation, config, code generation | Higher  |
| **Haiku**            | Trivial tasks — formatting, simple CRUD, file moving   | Lower   |
| **Opus**             | Complex reasoning, architecture decisions, debugging   | Highest |

**Rule**: Default to Sonnet. Use Haiku only for truly trivial operations.

### Gemini CLI + Conductor Plugin

**Conductor** ([github.com/gemini-cli-extensions/conductor](https://github.com/gemini-cli-extensions/conductor)) enables **context-driven development** — formalizing specs and plans as persistent Markdown files.
Install: `gemini extensions install https://github.com/gemini-cli-extensions/conductor`

**What it does**: Breaks objectives into Tracks → Phases → Tasks, stored in `conductor/spec.md` and `conductor/plan.md`. Tasks should be **atomic enough for parallel execution**.

#### Model Selection (February 2026)

| Provider | Model | Context | Input $/MTok | Output $/MTok | Long Context (>200K) | Best For |
|----------|-------|---------|--------------|---------------|---------------------|----------|
| **Google** | Gemini 3 Flash | 1M | $0.50 | $3.00 | N/A (flat rate) | 95% of coding |
| **Google** | Gemini 3 Pro* | 1M | $2.00 | $12.00 | $4.00/$18.00 | Complex reasoning |
| **Anthropic** | Claude Sonnet 4.5 | 200K/1M† | $3.00 | $15.00 | $6.00/$22.50 | Balanced quality |
| **Anthropic** | Claude Opus 4.5 | 200K | $5.00 | $25.00 | N/A | Deep analysis |

*Preview pricing - may reduce Q2 2026  
†1M context in beta for organizations in usage tier 4

> **Cost Guidance**: Gemini 3 Flash offers the best value for routine coding. Use higher-tier models only when reasoning depth is insufficient.
> ⚠️ Preview pricing as of February 2026 - verify before production use

#### Essential Plugins

Install: `gemini extensions install <github-url>`

| Plugin                                                         | Purpose                                |
| -------------------------------------------------------------- | -------------------------------------- |
| [Conductor](https://github.com/gemini-cli-extensions/conductor)          | Context-driven specs, plans, tracks    |
| [GitHub MCP](https://github.com/modelcontextprotocol/servers)  | PR reviews, issue triage               |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | E2E testing, browser automation        |
| [Jules](https://github.com/google/gemini-cli-extensions)       | Async agent for refactoring, bug fixes |

### Parallel Agent Execution

Both CLIs support launching multiple agents for independent tasks:

```
# Example: Parallel work on 3 independent tracks
Agent 1: Track 1 — Backend API (Task 2.1: Create BullMQ job)
Agent 2: Track 2 — Frontend UI (Task 2.1: Bulk selection component)
Agent 3: Track 3 — Testing (Task 1.1: Unit tests)
```

**Critical**: After parallel work, ALWAYS validate integration:

```bash
# Single command for full regression validation
e.g. make tests; make validate-regression-suite
```

> **📋 Definition of Done — Validation Requirements**
>
> Both `GEMINI.md` and `CLAUDE.md` must instruct agents to:
>
> 1. Run validation automatically at the end of every task
> 2. Include **test harness/suite** coverage for new features
> 3. Add **integration tests** for API changes
> 4. Add **UI/UX validation** (E2E tests) for frontend changes
> 5. Execute full regression suite before marking task complete
>
> Agents should run `make validate-regression-suite` autonomously — or prompt the user to approve execution.

#### Validation Makefile Targets

| Target                           | Scope                                            | When to Use                  |
| -------------------------------- | ------------------------------------------------ | ---------------------------- |
| `make validate-regression-suite` | Full regression (lint + typecheck + unit + E2E)  | After any feature completion |
| `make ci-validate`               | Quick CI checks (lint + typecheck + TF validate) | Before commits               |
| `make validate-staging`          | Staging health + E2E smoke                       | After deployments            |
| `make e2e`                       | Full E2E suite only                              | UI/UX validation             |

### Skills (Slash Commands)

Custom skills provide specialized workflows:

| Skill              | Trigger            | Purpose                      |
| ------------------ | ------------------ | ---------------------------- |
| `/commit`          | After code changes | Guided git commit workflow   |
| `/review-pr`       | PR review          | Structured code review       |
| `/release`         | Deployment time    | Release management workflow  |
| `/speckit.specify` | New feature        | Create feature specification |
| `/speckit.plan`    | After spec         | Generate implementation plan |
| `/speckit.tasks`   | After plan         | Generate actionable tasks    |

#### Spec-Kit Workflow

```bash
# 1. Define what to build
/speckit.specify "Add bulk image ALT text regeneration"

# 2. Plan the implementation
/speckit.plan

# 3. Generate tasks
/speckit.tasks

# 4. Implement
/speckit.implement
```

---

## MCP Tools Configuration

### What is MCP?

Model Context Protocol (MCP) extends AI coding assistants with external capabilities. MCP servers provide domain-specific tools for schema introspection, code validation, browser automation, and documentation search.

### Categories of MCP Tools

| Category               | Purpose                                                             |
| ---------------------- | ------------------------------------------------------------------- |
| **API & Schema**       | GraphQL introspection, schema validation, type-safe code generation |
| **Browser Automation** | E2E testing, visual validation, session management                  |
| **Infrastructure**     | Cloud deployment, IaC validation, security scanning                 |
| **Documentation**      | Official docs search, API reference lookup                          |

### Configuration

MCP servers are configured in:

- **Global**: `~/.claude/settings.json` (Claude Code) or `~/.gemini/settings.json` (Gemini CLI)
- **Project**: `.claude/settings.json` or `.gemini/settings.json`

Refer to each MCP server's documentation for installation and setup instructions.

---

## ClickOps Engineering

### What is ClickOps Engineering?

ClickOps Engineering transforms manual UI interactions into **codified, deterministic automation**. Rather than ad-hoc clicking through interfaces, every UI journey is captured as executable test code.

### How It Works

1. **Session Reuse**: Launch a browser (Playwright, Selenium) using an existing logged-in Chrome profile via CDP (Chrome DevTools Protocol)
2. **Journey Recording**: Navigate through complete user flows—the AI observes and can generate equivalent test code
3. **Codified Automation**: The resulting tests are version-controlled, repeatable, and CI-ready
4. **Future Conversion**: AI can evaluate these journeys and convert them to equivalent IaC automation (Terraform, Pulumi) when APIs become available

### Benefits

| Benefit           | Description                                                   |
| ----------------- | ------------------------------------------------------------- |
| **Deterministic** | Same journey produces same result every time                  |
| **Auditable**     | Every UI action is logged and version-controlled              |
| **Convertible**   | Journeys can be analyzed and converted to API/IaC equivalents |
| **AI-Evaluable**  | AI can review recordings and suggest optimizations            |

> **Note**: Gemini Enterprise has strong UI click operation capabilities, making it particularly suited for ClickOps workflows.

---

## Three Musketeers Pattern

### What is Three Musketeers?

A pattern where all development tasks are executed through three tools:

1. **Make** — Task orchestration
2. **Docker** — Environment consistency
3. **Compose** — Service orchestration

### Why We Use It

| Benefit               | Explanation                                            |
| --------------------- | ------------------------------------------------------ |
| **Human Reusability** | Any developer runs `make dev` — same result everywhere |
| **CI/CD Alignment**   | GitHub Actions use same Makefile targets               |
| **Documentation**     | `make help` shows all available commands               |
| **Abstraction**       | Complex commands hidden behind simple targets          |

### Makefile Targets

Run `make help` to see all available targets. Common categories:

- **Development**: `make dev`, `make setup`
- **Testing**: `make test`, `make e2e`, `make lint`, `make typecheck`
- **Database**: `make db-migrate`, `make db-studio`
- **Infrastructure**: `make tf-plan-*`, `make tf-apply-*`
- **Deployment**: `make deploy-staging`, `make health-check-staging`
- **Validation**: `make validate-regression-suite` (full regression)

---

## Pre-Commit Hooks

Use `lint-staged` + `husky` to enforce linting and formatting on every commit. This catches issues early, ensures consistent formatting, and provides fast feedback (<10 seconds).

Bypass only for emergencies: `git commit --no-verify`

---

## Testing & Validation

Use a **testing pyramid**: many fast unit tests at the base, fewer integration tests in the middle, and targeted E2E tests at the top.

| Layer           | Purpose                                |
| --------------- | -------------------------------------- |
| **Unit**        | Fast, mocked, high coverage            |
| **Integration** | Real external APIs                     |
| **E2E**         | Browser automation, full user journeys |

For authenticated session testing, use CDP (Chrome DevTools Protocol) to reuse existing browser sessions—no credentials in test files.

---

## Branch-Based Development

### Branch Naming

| Prefix      | Purpose                |
| ----------- | ---------------------- |
| `feat/`     | New features           |
| `fix/`      | Bug fixes              |
| `refactor/` | Code improvements      |
| `docs/`     | Documentation only     |
| `infra/`    | Infrastructure changes |

### Workflow

`main` (protected) ← PR ← feature branch ← commits

### Commit Message Format

```
type(scope): Brief description

- Detailed bullet point 1
- Detailed bullet point 2

Fixes #123
Refs #456
```

**Types**: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `infra`

### Branch Lifecycle

1. **Create**: `git checkout -b feat/my-feature`
2. **Develop**: Make changes, commit frequently
3. **Push**: `git push -u origin feat/my-feature`
4. **PR**: Create PR via `gh pr create`
5. **Review**: Address feedback
6. **Merge**: Squash merge to main
7. **Delete**: Branch auto-deleted after merge

---

## Spec-Driven Development

### Artifact Hierarchy

```
Vision & Strategy
       │
       ▼
┌─────────────────────┐
│ engagement/vision/  │ ← Why we exist
│ VISION.md           │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ engagement/strategy/│ ← Product strategy
│ PRODUCT_STRATEGY.md │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ requirements/       │ ← Feature specs, user journeys
│ FEATURE_SPEC.md     │
│ USER_JOURNEYS.md    │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ architecture/       │ ← Technical decisions
│ decisions/ADR-*.md  │
│ HLD-*.md, LLD-*.md  │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ planning/           │ ← Execution tracking
│ ROADMAP.md          │
│ SCOPE.md            │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│ GitHub Issues       │ ← Actionable work items
│ Epics → Stories     │
└─────────────────────┘
```

### Spec-Kit Workflow

Use Spec-Kit skills to convert requirements into actionable work:

1. **Constitution** → Project principles
2. **Specify** → Feature specification
3. **Clarify** → Requirements refinement
4. **Plan** → Implementation plan
5. **Tasks** → GitHub issues
6. **Implement** → Execute tasks

### ADR (Architecture Decision Record)

Document significant technical decisions with: **Context** (why), **Decision** (what), **Consequences** (trade-offs). Keep ADRs concise and numbered sequentially.

---

## Project Tracking

### File-Based Tracking

| File           | Purpose                         |
| -------------- | ------------------------------- |
| `STATUS.md`    | Current sprint status, blockers |
| `CHANGELOG.md` | Release notes, known issues     |
| `ROADMAP.md`   | Phase milestones                |
| `SCOPE.md`     | Remaining work, priorities      |

### GitHub Issues

Use `gh` CLI for issue management: `gh issue list`, `gh issue create`, `gh pr create`.

### Issue Structure

Issues should include: **Definition of Done**, **cross-references** (ADRs, requirements), **phase label**, and **priority label** (P0-P3).

### Project Board

Use GitHub Projects or a similar Kanban tool to track work across phases.

---

## Quick Reference

### Daily Workflow

```bash
# Morning: Pull latest, check issues
git checkout main && git pull
gh issue list --state open --limit 10

# Start work: Create branch
git checkout -b feat/my-feature

# Development: Code, test, commit
make dev                 # Start dev server
# ... make changes ...
make test && make lint   # Validate
git add . && git commit  # Commit (hooks run)

# End of day: Push, create PR
git push -u origin feat/my-feature
gh pr create --title "My Feature" --body "Description"
```

### Before Every Commit

```bash
make test && make lint && make typecheck
```

### Before Creating PR

```bash
# Ensure all tests pass
make test
make e2e

# Update documentation
# - STATUS.md (if status changed)
# - CHANGELOG.md (what changed)
# - ROADMAP.md (if milestone affected)
```

### Environment Variables

Configure credentials and connections via `.env` file. Common categories:

- **App credentials** (API keys, secrets)
- **Database connections** (PostgreSQL, Redis)
- **External APIs** (AI services, third-party integrations)

### Shell Aliases

Add project-specific aliases to your shell profile for common Makefile targets (`make dev`, `make test`, `make lint`).

---

## Release Management & Tagging

### Semantic Versioning

Follow [SemVer](https://semver.org/):

```
MAJOR.MINOR.PATCH
  │     │     │
  │     │     └── Bug fixes (backwards-compatible)
  │     └──────── Features (backwards-compatible)
  └────────────── Breaking changes
```

### Tag Naming Convention

| Tag Pattern      | Purpose                  | Example          |
| ---------------- | ------------------------ | ---------------- |
| `v1.2.3`         | Production release       | `v1.1.0`         |
| `staging-v1.2.3` | Staging deployment       | `staging-v1.1.0` |
| `infra-v1.0.0`   | Infrastructure milestone | `infra-v1.0.0`   |

### Release Workflow

```bash
# 1. Pre-release checks
make pre-release    # Runs tests, lint, typecheck, build

# 2. Deploy to staging
make release-staging VERSION=1.1.0
# Creates tag: staging-v1.1.0
# Triggers: GitHub Actions → Cloud Run deployment

# 3. Soak period (48h minimum)
make health-check-staging
# Monitor: Error rates, latency, user feedback

# 4. Deploy to production
make release-prod VERSION=1.1.0
# Creates tag: v1.1.0
# Triggers: Canary rollout (10% → 50% → 100%)

# 5. Rollback (if needed)
make rollback-staging   # Revert to previous revision
make rollback-prod      # Revert to previous revision
```

### GitHub Actions Triggers

| Trigger                | Workflow                | Action                     |
| ---------------------- | ----------------------- | -------------------------- |
| Push to `main`         | `ci.yml`                | Run tests, lint, typecheck |
| Tag `staging-v*`       | `deploy-staging.yml`    | Deploy to staging          |
| Tag `v*` (not staging) | `deploy-production.yml` | Deploy to production       |
| PR opened              | `terraform-plan.yml`    | Show infra changes         |

### Milestone Tracking

Milestones are tracked in:

- `planning/ROADMAP.md` — Phase completion status
- `STATUS.md` — Current sprint progress
- GitHub Milestones — Issue grouping

---

## Project Structure & Folder Relationships

### Reference Folder Layout

```
project-root/
│
├── .claude/                      # Claude Code configuration
│   ├── settings.json             # MCP servers, permissions
│   └── skills/                   # Custom slash command skills
│       ├── release-management.md
│       ├── qa-agent-browser.md
│       └── *.skill               # Skill definitions
│
├── .github/                      # GitHub configuration
│   ├── workflows/                # CI/CD pipelines
│   │   ├── ci.yml                # Test/lint on push
│   │   ├── deploy-staging.yml    # Staging deployment
│   │   └── deploy-production.yml # Production deployment
│   └── CODEOWNERS                # Review assignments
│
├── architecture/                 # Technical architecture
│   ├── decisions/                # ADR-NNN-*.md 
│   ├── specs/                    # SPEC-NNN-*.md
│   ├── HLD-*.md                  # High-level designs
│   └── LLD-*.md                  # Low-level designs
│
├── engagement/                     # Business documentation
│   ├── vision/                   # VISION.md — Why we exist
│   │   └── VISION.md
│   ├── strategy/                 # Product strategy
│   │   └── PRODUCT_STRATEGY.md
│
├── docs/                         # Supplementary documentation
│   ├── design/                   # Design documents, HLDs
│   ├── security/                 # Security procedures
│   └── DEVELOPER_EXPERIENCE.md   # This document
│
├── engineering/                  # Engineering documentation
│   ├── operations/               # OP-NNN-*.md (Operations guides)
│   │   ├── OP-011-infrastructure-bootstrap.md
│   ├── runbooks/                 # RB-NNN-*.md (Runbooks)
│   │   ├── RB-000-release.md
│   └── testing/                  # TEST-NNN-*.md (Test docs)
│       └── TEST-001-playwright.md
│
├── planning/                     # Execution tracking
│   ├── ROADMAP.md                # Phase milestones
│   ├── SCOPE.md                  # Remaining work
│
├── requirements/                 # Feature specifications
│   ├── FEATURE_SPEC.md           # Functional requirements
│   ├── USER_JOURNEYS.md          # user flow definitions
│
├── terraform/                    # Infrastructure as Code
│   ├── core/                     # Hub: IAM, OIDC, AR, state bucket
│   ├── staging/                  # Spoke: Staging environment
│   ├── production/               # Spoke: Production environment
│   └── modules/                  # Reusable modules
│       └── spoke/                # Shared spoke module 
│
├── tests/                        # Test suites
│   └── e2e/                      # Playwright E2E tests
│       ├── fixtures/             # Test helpers, CDP fixtures
│       └── *.spec.ts             # Test files
│
├── scripts/                      # Utility scripts
│   └── *.sh                      # Bash scripts
│
├── CLAUDE.md                     # AI agent instructions
├── STATUS.md                     # Current sprint status
├── CHANGELOG.md                  # Change history
├── Makefile                      # Task automation
└── GEMINI.md                     # Commercial grounding
```

### Folder Relationships & Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STRATEGIC LAYER                              │
│                                                                      │
│  engagement/vision/VISION.md ───────────────────────────────────┐    │
│         │                                                       │    │
│         ▼                                                       │    │
│  engagement/strategy/PRODUCT_STRATEGY.md ───────────────────────┤    │
│         │                                                       │    │
│         ▼                                                       │    │
│  requirements/FEATURE_SPEC.md ◄─────────────────────────────────┤    │
│  requirements/USER_JOURNEYS.md                                  │    │
└─────────────────────────────────────────────────────────────────┼────┘
                                                                  │
┌─────────────────────────────────────────────────────────────────┼────┐
│                       ARCHITECTURE LAYER                        │    │
│                                                                 │    │
│  architecture/decisions/ADR-*.md ◄──────────────────────────────┘    │
│         │    │                                                       │
│         │    └──────────────────────────────────────────────────┐    │
│         ▼                                                       │    │
│  architecture/HLD-*.md ─────────────────────────────────────────┤    │
│         │                                                       │    │
│         ▼                                                       │    │
│  architecture/LLD-*.md ─────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────┬──────────────┘
                                                        │
┌───────────────────────────────────────────────────────┼──────────────┐
│                       EXECUTION LAYER                  │              │
│                                                        │              │
│  planning/ROADMAP.md ◄─────────────────────────────────┘              │
│         │                                                             │
│         ▼                                                             │
│  planning/SCOPE.md ─────────────────────────────────────────────┐     │
│         │                                                       │     │
│         ▼                                                       │     │
│  GitHub Issues (gh issue list) ◄────────────────────────────────┘     │
└───────────────────────────────────────────────────────┬───────────────┘
                                                        │
┌───────────────────────────────────────────────────────┼───────────────┐
│                     IMPLEMENTATION LAYER               │              │
│                                                        │              │
│  src/ ◄────────────────────────────────────────────────┘              │
│  terraform/ ◄──────────── architecture/decisions/ADR-*                │
│  tests/e2e/ ◄──────────── requirements/USER_JOURNEYS.md               │
└───────────────────────────────────────────────────────────────────────┘
```

### Document Naming Conventions

| Prefix       | Type                         | Location                         | Example               |
| ------------ | ---------------------------- | -------------------------------- | --------------------- |
| `ADR-NNN-`   | Architecture Decision Record | `architecture/decisions/`        | `ADR-001-EXAMPLE.md`  |
| `HLD-NNN-`   | High-Level Design            | `architecture/`                  | `HLD-001-EXAMPLE.md`  |
| `LLD-NNN-`   | Low-Level Design             | `architecture/`                  | `LLD-001-EXAMPLE.md`  |
| `SPEC-NNN-`  | Specification                | `architecture/specs/`            | `SPEC-001-EXAMPLE.md` |
| `RB-NNN-`    | Runbook                      | `engineering/runbooks/`          | `RB-001-EXAMPLE.md`   |
| `OP-NNN-`    | Operations Guide             | `engineering/operations/`        | `OP-001-EXAMPLE.md`   |
| `TEST-NNN-`  | Test Documentation           | `engineering/testing/`           | `TEST-001-EXAMPLE.md` |
| `01-`, `02-` | Numbered sequence            | `engagement/*/`, `requirements/` | `01-EXAMPLE.md`       |

### Cross-Reference Convention

Documents reference each other using relative paths:

```markdown
# In an ADR

See [HLD-001](../HLD-001-EXAMPLE.md) for infrastructure details.
Related: Architecture Decision Records (ADRs) and GitHub Issues for tracking.
```

---

## CLAUDE.md Configuration

### Purpose

`CLAUDE.md` is the **instruction manual for AI agents** working on this project. It ensures:

1. **Consistent Context**: AI understands project goals, architecture, constraints
2. **Guardrails**: Prevents AI from making decisions outside scope
3. **Workflow Alignment**: AI follows same processes as human developers

### Key Sections in CLAUDE.md

| Section                       | Purpose                                      |
| ----------------------------- | -------------------------------------------- |
| **Your Role & Stance**        | AI's identity as developer/architect/advisor |
| **Project Overview**          | What the project is (and isn't)              |
| **Tech Stack**                | Technologies in use                          |
| **Development Commands**      | Makefile targets reference                   |
| **Project Structure**         | Folder layout (synced with this doc)         |
| **Documentation Conventions** | Naming rules for ADRs, HLDs, etc.            |
| **Architecture**              | Component responsibilities, workflows        |
| **Testing Strategy**          | Test pyramid, E2E patterns                   |
| **Governance & DoD**          | Definition of Done, commit rules             |
| **Important Constraints**     | What AI must NOT do                          |
| **MCP Tools**                 | Available external tools                     |

### How CLAUDE.md Maintains Structure

1. **Folder References**: CLAUDE.md documents where each type of file belongs
2. **Naming Conventions**: Enforces ADR-NNN, HLD-NNN patterns
3. **Cross-Reference Rules**: Requires ADR for decisions, issue refs in commits
4. **Definition of Done**: Mandates doc updates (STATUS.md, CHANGELOG.md)

### Updating CLAUDE.md

When project structure changes:

1. Update CLAUDE.md "Project Structure" section
2. Update this DEVELOPER_EXPERIENCE.md
3. Update any affected ADRs
4. Commit all changes together

---

## How Spec-Driven Development Supports This Approach

### The Spec-Kit Philosophy

Spec-driven development ensures:

1. **Traceability**: Every line of code traces back to a requirement
2. **Alignment**: Technical decisions align with business goals
3. **Quality**: Specs define acceptance criteria before coding

### Artifact Flow with Spec-Kit

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CONSTITUTION                                                 │
│    └── .specify/memory/constitution.md                          │
│        Defines: Core principles, quality gates, decision rules  │
│        Command: /speckit.constitution                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. SPECIFICATION                                                │
│    └── .specify/features/<feature>/spec.md                      │
│        Defines: What to build, user stories, acceptance criteria│
│        Command: /speckit.specify "Feature description"          │
│        Clarify: /speckit.clarify (ask 5 questions)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. PLAN                                                         │
│    └── .specify/features/<feature>/plan.md                      │
│        Defines: How to build, architecture, component design    │
│        Command: /speckit.plan                                   │
│        Cross-ref: Links to ADRs, HLDs                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. TASKS                                                        │
│    └── .specify/features/<feature>/tasks.md                     │
│        Defines: Actionable work items, dependencies, effort     │
│        Command: /speckit.tasks                                  │
│        Convert: /speckit.taskstoissues → GitHub Issues          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. IMPLEMENTATION                                               │
│    └── src/...                                                  │
│        Command: /speckit.implement                              │
│        Validation: Tests, lint, typecheck                       │
│        Documentation: ADR if architectural decision made        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. ANALYSIS                                                     │
│    └── Cross-artifact consistency check                         │
│        Command: /speckit.analyze                                │
│        Checks: Spec ↔ Plan ↔ Tasks alignment                    │
└─────────────────────────────────────────────────────────────────┘
```

### Integration with Existing Docs

| Spec-Kit Artifact | Maps To              | Typical Location               |
| ----------------- | -------------------- | ------------------------------ |
| Constitution      | Project principles   | `CLAUDE.md`, `GEMINI.md`       |
| Specification     | Feature requirements | `requirements/FEATURE_SPEC.md` |
| Plan              | Technical design     | `architecture/HLD-*.md`        |
| Tasks             | Work items           | `gh issue list`                |
| Analysis          | Quality audit        | `reports/`                     |

### When to Use Spec-Kit

| Scenario                    | Use Spec-Kit? | Reason                             |
| --------------------------- | ------------- | ---------------------------------- |
| New feature (>1 day effort) | ✅ Yes        | Full spec → plan → tasks flow      |
| Bug fix                     | ❌ No         | Just fix and document              |
| Refactoring                 | 🟡 Maybe      | Use /speckit.plan if architectural |
| Documentation update        | ❌ No         | Direct update                      |
| Infrastructure change       | ✅ Yes        | Use for Terraform changes >4h      |

### Example: Adding a New Feature

```bash
# 1. Create spec
/speckit.specify "Add bulk image ALT text regeneration with preview"

# 2. Clarify requirements (asks 5 targeted questions)
/speckit.clarify

# 3. Generate technical plan
/speckit.plan
# → Creates plan.md with component design, API changes, test strategy

# 4. Generate tasks
/speckit.tasks
# → Creates tasks.md with ordered, dependency-aware work items

# 5. Convert to GitHub issues
/speckit.taskstoissues
# → Creates GitHub issues with labels, cross-references

# 6. Implement (task by task)
/speckit.implement
# → AI implements each task, runs tests, commits

# 7. Analyze consistency
/speckit.analyze
# → Verifies spec ↔ plan ↔ tasks ↔ code alignment
```

---

## Additional Resources

- **CLAUDE.md** — AI agent instructions
- **GEMINI.md** — Commercial grounding directive
- **engagement/vision/VISION.md** — Project vision
- **architecture/decisions/** — Architecture Decision Records
- **engineering/testing/** — E2E testing guides
- **engineering/runbooks/** — Release and operations procedures


---

## Agent Instructions

> **This section is for AI agents (Claude Code, Gemini CLI, etc.) consuming this document as grounding context.**

### Document Authority

This Developer Experience Guide defines the **canonical ways of working**. The workflows, patterns, conventions, and quality gates documented here are **stable and authoritative** — do not deviate from them unless explicitly instructed by the user.

### What to Verify via Web Search

The following information is **transient and must be verified** before citing or using:

| Always Verify | Why |
|---------------|-----|
| Model pricing ($/MTok) | Changes frequently; preview → GA pricing shifts |
| Context window limits | Models evolve; long-context tiers affect cost |
| Plugin/extension URLs | Repositories move, get renamed, or deprecated |
| API capabilities | New features, deprecations, breaking changes |
| Tool versions | Syntax changes, new flags, compatibility |

**Rule**: If it has a version number, a price, or a URL — search before stating.

### What NOT to Change

- Branch naming conventions
- Quality gate requirements
- Commit message format
- Document naming patterns (ADR-NNN, HLD-NNN, etc.)
- Folder structure hierarchy
- Definition of Done criteria

These are **project standards**, not suggestions.

### Priority Hierarchy
```
1. User's direct instruction        (highest)
2. CLAUDE.md / GEMINI.md            (project-specific)
3. This document                    (workflows & patterns)
4. Agent training knowledge         (lowest — verify if uncertain)
```

### Before Completing Any Task
```
□ Verified transient info (pricing, versions, URLs) via web search?
□ Ran validation suite (make validate-regression-suite)?
□ Followed branch/commit conventions?
□ Updated STATUS.md / CHANGELOG.md if applicable?
□ Referenced GitHub issue in commit?
```

### When Uncertain

Ask the user rather than assume. Propose options with trade-offs. Reference which section of this guide informed your reasoning.

---

**Welcome to the team! Start with `make setup` and you'll be delivering value within the hour.**


