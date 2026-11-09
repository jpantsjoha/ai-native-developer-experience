# Install — OpenCode (candidate host)

Status: candidate. OpenCode discovers the two things DevEx Charter already ships, skills
in `.agents/skills/` and project instructions in `AGENTS.md`, according to its
documentation (checked 9 November 2026). This repository has not yet verified it with a
live run; record the result in [host capabilities](../HOST-CAPABILITIES.md) when you do.

## Project setup

1. Copy the complete skill directories from this repository's `skills/` into
   `<project>/.agents/skills/` (or `~/.agents/skills/` for your user), keeping each skill's
   references, assets and scripts. OpenCode also reads `.claude/skills/` and
   `.opencode/skills/`; keep one source, because duplicate skill IDs resolve to the last
   one found.
2. Bootstrap the project from any supported host, or follow [BOOTSTRAP](../../BOOTSTRAP.md).
   It generates `AGENTS.md`, which OpenCode loads as project instructions.
3. Start OpenCode in the project and ask which skills are available; `using-the-harness`
   and `operating-model-bootstrap` should be listed.

## Known gaps

- OpenCode documents no session-start event, so orientation is not injected
  automatically. `AGENTS.md` carries the contract; invoke `using-the-harness` explicitly.
- The Claude-format `commands/` are not converted to `.opencode/commands/`; the skills
  carry the same procedures.
- A full adapter, a small plugin that injects the orientation through
  `session.hook.context`, is not built. It would add an npm distribution path.

Sources: [skills](https://opencode.ai/docs/skills/), [rules](https://docs.opencode.ai/docs/rules/),
[commands](https://opencode.ai/docs/commands/), [plugins](https://opencode.ai/docs/plugins/),
[repository](https://github.com/anomalyco/opencode).
