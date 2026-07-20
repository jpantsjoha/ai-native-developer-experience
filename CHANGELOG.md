# Changelog

Material changes to the public harness are recorded here. Public-source attribution is
included only where a change directly adopts or discusses an external pattern.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project
does not infer a repository release number from the internal version of one document or
operating-manual asset; from 0.1.0 the changelog tracks the `join-the-team` plugin
packaging version declared in the harness manifests.

## [0.1.0] — 2026-07-20

First packaging of the harness as the `join-the-team` multi-harness plugin: one
canonical skill set and operating contract, thin per-harness adapters, drift-checked
in CI. Antigravity (Gemini) is a first-class, live-verified surface; Kimi Code,
Claude Code, and Codex adapters ship to spec.

### Added

**Operating model kernel**

- A released, immutable operating-manual 2.1.0 asset with a SHA-256-bound project profile.
- A safe, non-overwriting day-one initializer for new repositories.
- Thin `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` adapters carrying one protected contract.
- Deterministic offline validation for manual/profile binding, adapter drift, adoption
  state, checkpoints, and exact-candidate evidence manifests.
- A day-one adoption example, bootstrap guide, evidence manifest, and baseline skill map.

**Plugin packaging and distribution**

- `join-the-team` manifests for Kimi Code (`.kimi-plugin/`) and Claude Code
  (`.claude-plugin/` plus a marketplace entry), and a `gemini-extension.json` for
  Antigravity/Gemini surfaces.
- A session-start `using-the-harness` meta-skill that orients the assistant before any
  work; a Claude Code session-start hook that injects it (with an SDK-standard
  fallback for non-Claude runners); and `/join-the-team:bootstrap`,
  `/join-the-team:init`, and `/join-the-team:validate` slash commands.
- Antigravity capability layer: `references/antigravity-tools.md` tool mapping.
  Live `agy plugin install` verified on Antigravity 1.1.1 (17 skills + hook).
- Per-harness install docs (`docs/install/`) and a README plugin-install section.
- A plugin-packaging drift validator — manifest name/version sync, skill references,
  discovery alias, hook scripts — with regression tests wired into `make check`.

**Skills and team workflow**

- Cloud-expert family: `aws-expert`, `azure-expert`, and `alibaba-expert`, each pairing
  guardrails with official-source validation — documentation, live-docs MCP servers,
  and official GitHub foundations/agent-example repositories. `the-architect` routes
  cloud decisions to the matching vendor skill.
- `docs/WORKFLOW.md`: the skills dependency diagram (Mermaid), the requirement →
  ADR → ticket → evidence → status traceability chain, and the accountability model.
- A team-roster-and-escalation section in the profile template plus a
  `/join-the-team:init` command to capture named human owners and their channels.
- A live-documentation seam and a knowledge-base seam (SharePoint/Confluence/Google
  Drive) in `.agents/mcp_config.json`; the repo ADR stays the decision of record.

**Attribution and integrations**

- `NOTICE`: author attribution that derivative works must carry (Apache-2.0 §4(d)).
  The author section and `NOTICE` feature the forthcoming books (*Building the
  Agentic Enterprise on Google Cloud*, Packt; *Mastering Multi-Agent Systems on
  Google Cloud*, AVA Publishing).
- `INTEGRATIONS.md`: an evaluated companion-plugin map — reference never vendor,
  capability never authority, and a standalone guarantee.
- A companion-capabilities section in the project operating profile template.
- Narrow public-source attribution plus currency and usage caveats.

### Changed

- Relicensed from PolyForm dual source-available terms to Apache License 2.0 to
  remove adoption friction for teams and commercial use; attribution is preserved
  through the `NOTICE` file.
- Renamed `gcp-well-architected` to `gcp-expert`, aligning the cloud skills into one
  expert family; `gcp-expert` gained the same official-source validation section.
- Reframed the repository as a **team-project AI harness bootstrap**, not a production
  application starter kit.
- Clarified that the operating kernel is model-, vendor-, and IDE-agnostic while discovery
  and invocation adapters remain platform-specific.
- Made `seed` a usable, honest state for system design, delivery planning, and R0/R1 work;
  R2/R3 requires an active profile with applicable controls resolved.
- Ordered risk classification before authority confirmation so approval is scoped to the
  actual risk.
- Allowed namespaced local development/test services in isolated worktrees while keeping
  shared operational/production-like services under a designated canonical owner.
- Replaced unsupported or conflated adoption statistics with qualified, primary-source
  links and labelled the 10/90 split as a heuristic.

### Fixed

- Added candidate identity to durable checkpoints and a matching evidence manifest.
- Corrected attribution: the anti-rationalisation table format was adopted after review of
  Addy Osmani's MIT-licensed `agent-skills`; JP's claimed contribution is the Adversarial
  Gate name and “how would I break this?” framing.
- Removed ambiguity between a universal manual and project-specific adoption metadata.
- Consistency sweep: install-doc skill counts and slash-command lists, and harmonised
  manifest descriptions across the four harness adapters.

### Known limitations

- The initializer cannot discover missing business/domain facts; the team and assistant
  must ground and own them in the profile.
- Local checks cannot authenticate reviewer identity or enforce remote repository policy.
- Skill auto-discovery and invocation differ by assistant and IDE.
- The initializer and validator require Python 3.10 or newer.
- Live plugin installs are verified on Antigravity (agy 1.1.1) only; Kimi Code, Claude
  Code, and Codex install paths are built to spec and pending live verification.
- Team-roster escalation and GH-issue traceability are documented conventions, not yet
  tool-enforced.
- The repository contains no usage telemetry; the licence cannot identify silent use.
