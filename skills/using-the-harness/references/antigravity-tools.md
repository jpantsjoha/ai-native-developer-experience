# Antigravity (Gemini) Tool Mapping

Skills in this harness speak in actions ("dispatch a subagent", "track tasks", "read a
file"). On Antigravity — IDE, Agent Manager, and `agy` CLI — those actions resolve to
the tools below. Skill bodies never name tools; this mapping is the per-harness
translation layer. Do not edit canonical skills to fit Antigravity.

| Action the skills request | Antigravity equivalent |
|---|---|
| Invoke a skill | The skill's trigger conditions fire from the loaded `SKILL.md`; skills live in `.agents/skills/` and are discovered natively |
| Dispatch a subagent (implementer, reviewer) | `invoke_subagent` with a built-in `TypeName` — `self` for full-capability work, `research` for read-only review/exploration |
| Track tasks ("create a todo", "mark complete") | A **task artifact** — `write_to_file` with `IsArtifact: true` and `ArtifactMetadata.ArtifactType: "task"`. **Not** `manage_task` (that manages background processes, not checklists) |
| Read / write / edit files | Native file tools (`read_file`, `write_to_file`, `replace_file_content`, `multi_replace_file_content`) |
| Search file contents / find files | Native search tools (`grep_search`, `find_by_name`) |
| Run commands, tests, validators | `run_command` — the operating-model scripts are stdlib Python 3.10+, no other dependency |

## Task artifacts

Antigravity has no todo tool. When a skill asks for a task list, create a markdown
checklist as a task artifact at the start of multi-step work, mark items done as you
go, and re-read it after long stretches — it is the durable record of what remains.

## The harness primitives on this surface

- **Rules** → `GEMINI.md` (declared as `contextFileName` in `gemini-extension.json`;
  loaded as always-on context).
- **Skills** → `.agents/skills/` (native discovery).
- **MCP data seams** → `.agents/mcp_config.json` (governed tool access; see the file
  for the pattern).
- **Agent Manager** — the same contract governs background/delegated lanes; one
  mutating lane per worktree, integration owner assembles. Lane discipline is the
  operating model's, not the surface's.
