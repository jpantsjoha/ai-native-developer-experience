# Changelog

Material changes to the public harness are recorded here. Public-source attribution is
included only where a change directly adopts or discusses an external pattern.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project
does not infer a repository release number from the internal version of one document or
operating-manual asset.

## Unreleased

### Added

- A released, immutable operating-manual 2.1.0 asset with a SHA-256-bound project profile.
- A safe, non-overwriting day-one initializer for new repositories.
- Thin `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` adapters carrying one protected contract.
- Deterministic offline validation for manual/profile binding, adapter drift, adoption
  state, checkpoints, and exact-candidate evidence manifests.
- A day-one adoption example, bootstrap guide, evidence manifest, and baseline skill map.
- Narrow public-source attribution plus currency and usage caveats.
- Plugin packaging for Kimi Code and Claude Code: `join-the-team` manifests, a
  marketplace entry, and a session-start `using-the-harness` meta-skill that orients
  the assistant before any work.
- `INTEGRATIONS.md`: an evaluated companion-plugin map — reference never vendor,
  capability never authority, and a standalone guarantee.
- A companion-capabilities section in the project operating profile template.
- `NOTICE`: author attribution to preserve across copies, adaptations, and any future
  licence change.
- Dual source-available terms: unlimited noncommercial use under PolyForm Noncommercial
  1.0.0 and a short commercial evaluation under PolyForm Free Trial 1.0.0. Ongoing
  commercial team adoption requires separate written permission.

### Changed

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

### Known limitations

- The initializer cannot discover missing business/domain facts; the team and assistant
  must ground and own them in the profile.
- Local checks cannot authenticate reviewer identity or enforce remote repository policy.
- Skill auto-discovery and invocation differ by assistant and IDE.
- The initializer and validator require Python 3.10 or newer.
- Licensing creates a permission boundary but cannot provide telemetry or identify silent
  repository use.
