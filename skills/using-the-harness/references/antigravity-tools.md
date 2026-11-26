# Antigravity (Gemini) Tool Mapping

Verified on 2026-11-25 against the Antigravity 2.0 desktop app declared tool schemas;
check them against your installed version if you run another Antigravity surface.

Skills in this harness speak in actions ("dispatch a subagent", "track tasks", "read a
file"). On Antigravity — IDE, Agent Manager, and `agy` CLI — those actions resolve to
the tools below. Skill bodies never name tools; this mapping is the per-harness
translation layer. Do not edit canonical skills to fit Antigravity.

| Action the skills request | Antigravity equivalent |
|---|---|
| Invoke a skill | Read the skill's `SKILL.md` from the discovered plugin path (`skills/` or `.agents/skills/`) before executing its procedure |
| Dispatch a subagent (implementer, reviewer) | `invoke_subagent` with a built-in `TypeName` — `self` for full-capability work, `research` for read-only review/exploration; `run_workflow` for multi-agent fan-out |
| Track tasks ("create a todo", "mark complete") | `update_steps` for a live ordered checklist and `update_focus` for phase status; use a markdown artifact via `write_file` (with `ArtifactMetadata`) for persistent reports/plans. **Not** `manage_task` (that manages background processes) |
| Read / write / edit files | Native file tools (`read_file`, `write_file`, `edit_file`) |
| Search file contents / find files | Native workspace search tools where exposed, or read-only shell commands via `run_command` (`grep`, `find`, `git`, or `rg` if installed) |
| Ask clarifying multiple-choice questions | `ask_question` |
| Run commands, tests, validators | `run_command` — the operating-model scripts are stdlib Python 3.9+, no other dependency |

## Task tracking and artifacts

Use `update_steps` for live checklist tracking during multi-step work, and `write_file`
with `ArtifactMetadata` in the conversation's artifact directory for durable reports,
audits, or reviewable plans.

## The harness primitives on this surface

- **Rules** → `GEMINI.md` (declared as `contextFileName` in `gemini-extension.json`;
  loaded as always-on context).
- **Skills** → `skills/` (Agent Plugins fixed location) with `.agents/skills/` as alias.
- **MCP data seams** → `.agents/mcp_config.json` (governed tool access; see the file
  for the pattern).
- **Agent Manager** — the same contract governs background/delegated lanes; one
  mutating lane per worktree, integration owner assembles. Lane discipline is the
  operating model's, not the surface's.
