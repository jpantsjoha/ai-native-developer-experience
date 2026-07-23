# Install — Codex (CLI and App)

Codex discovers project skills natively from `.agents/skills/` — the canonical
location this repository already uses — and reads `AGENTS.md` as its always-on
adapter. No plugin manifest is required for the skill layer.

## Option 1: Repository checkout (project-local)

Clone or vendor this repository's `.agents/skills/` into your project and keep the
generated `AGENTS.md` adapter at the project root. Codex picks both up on the next
session.

## Option 2: Plugin marketplace

When listed, install `join-the-team` from the Codex plugin marketplace (`/plugins`
in the CLI, or the Plugins sidebar in the Codex app).

## Verify

1. Ask "which skills are available?" — the 19 skills should be named.
2. `AGENTS.md` should appear in Codex's loaded context files.

## Notes

- Session-start injection on Codex uses `.codex/hooks.json` in the *target* project;
  that is the project's own file to adopt, and this plugin never writes to a user's
  personal config. The always-on `AGENTS.md` adapter is the baseline integration and
  is sufficient.
