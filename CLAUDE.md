# CLAUDE.md

This repo's rules live in **[GEMINI.md](GEMINI.md)** — read it first. It is the always-on harness: design-before-generate, the Adversarial Gate ("how would I break this?"), receipts-not-polish, file standards, and where skills and MCP config live. Those rules apply here unchanged.

## Claude Code specifics

- Skills are the same `.agents/skills/` SKILL.md workflows GEMINI.md points to — reuse them, don't reinvent.
- Run the quality gates before you claim done: `make lint && make typecheck && make test && make spec-conformance`, then the Adversarial Gate.
- Packaging is standards-bound: the root `plugin.json` follows [Agent Plugins 1.0.0](https://agent-plugins.org/specification) and `.claude-plugin/` is a declared client projection of it. Change one manifest, change them all — `make spec-conformance` and the drift check will tell you.
- The deep mechanics live in [DEVELOPER_EXPERIENCE.md](DEVELOPER_EXPERIENCE.md) (DX-001).

Borrow the patterns, your mileage may vary.
