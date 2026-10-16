# Install — Codex (CLI and App)

Choose one source of the skills for each working context. Use the Codex Plugins
interface when `join-the-team` is available, or install the skills using native discovery.
Host interfaces vary; this guide does not prescribe a universal plugin CLI command.

## Project or user skills

| Scope | Location | Use |
| --- | --- | --- |
| Project | `<project>/.agents/skills/<skill-name>/` | Track the chosen skills with a team repository |
| User | `~/.agents/skills/<skill-name>/` | Make the skills available across your projects |

Copy each complete directory from this repository’s `skills/`, retaining its references,
assets and scripts. Preserve existing skills; resolve name collisions instead of replacing
them or keeping competing versions. A user installation applies to your account, not
every teammate. Record the selected source/version with the team’s project controls.

Codex discovers the skills and supplies their locations to the assistant. Invoke
`operating-model-bootstrap` from the consumer project and follow [BOOTSTRAP](../../BOOTSTRAP.md).
The skill resolves scripts beside its own file; it does not require a local copy when
installed globally. Bootstrap generates project-specific adapters and operating records.
Preserve existing adapters and resolve conflicts rather than copying maintainer settings.

## Plugin installation

Use the host’s Plugins interface and verify that the skills are available in the intended
project. Installed packages contain the real `skills/` directory; a cache may omit the
repository’s `.agents/skills` symlink. Skills, commands and hooks are host capabilities,
so do not assume every host exposes Claude-style slash commands or session-start hooks.
Ask the bootstrap skill to perform the adoption sequence when commands are unavailable.

## Verify

1. In a fresh session, ask which skills are available; the 25 skills should be named
   when the full library is installed. Inspect the source path/version. Resolve duplicate installations before making changes.
2. From a disposable project, run bootstrap’s dry-run, then initialise and validate.
   Expect a seed PASS with unresolved project decisions clearly reported.
3. Confirm the generated `AGENTS.md` and project profile are loaded for that project.
   Global skill discovery alone does not create project authority or release readiness.

The [official skill locations](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)
were checked on 16 October 2026. The full repository checkout retains its own maintainer
adapters; it is distinct from adopting the skills in another project.
