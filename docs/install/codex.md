# Install — Codex (CLI and App)

Codex discovers project skills natively from `.agents/skills/` — a symlinked alias
this repository keeps pointing at the canonical `skills/` directory — and reads
`AGENTS.md` as its always-on adapter. No plugin manifest is required for the skill layer.

> **Note on `codex plugin add`.** Codex's install cache flattens the package and drops
> symlinks. Installing this plugin through the marketplace therefore yields
> `.agents/skills/` as a real directory and no `skills/` at all. Codex works fine — it
> discovers `.agents/skills/` natively — but do not rely on `skills/` existing in a
> Codex-installed copy.

## Option 1: Repository checkout (project-local)

Clone or vendor this repository's `.agents/skills/` into your project and keep the
generated `AGENTS.md` adapter at the project root. Codex picks both up on the next
session.

## Option 2: Plugin marketplace

When listed, install `join-the-team` from the Codex plugin marketplace (`/plugins`
in the CLI, or the Plugins sidebar in the Codex app).

## Verify

1. Ask "which skills are available?" — the 21 skills should be named.
2. `AGENTS.md` should appear in Codex's loaded context files.

## Standards

The skills follow [Agent Skills](https://agentskills.io/specification), which is what lets
Codex discover them from `.agents/skills/` with no manifest at all. The root `plugin.json`
follows [Agent Plugins 1.0.0](https://agent-plugins.org/specification) and is the portable
entry point for clients that do want a manifest. Codex has no declared `extensions`
namespace here, because it needs none — native discovery plus `AGENTS.md` is the whole
integration.

## Notes

- Session-start injection on Codex uses `.codex/hooks.json` in the *target* project;
  that is the project's own file to adopt, and this plugin never writes to a user's
  personal config. The always-on `AGENTS.md` adapter is the baseline integration and
  is sufficient.
