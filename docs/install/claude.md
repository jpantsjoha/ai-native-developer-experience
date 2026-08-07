# Install — Claude Code

Install from the repository as a marketplace plugin:

```bash
/plugin marketplace add jpantsjoha/ai-native-developer-experience
/plugin install join-the-team@join-the-team-marketplace
```

What gets wired:

- **Skills** — the 21 `.agents/skills/` capabilities, discovered via the plugin's
  `skills/` alias. The `skills/` alias is a symlink at the repo root pointing to
  `.agents/skills/` — this lets Claude Code's plugin path resolve `skills/` while
  Codex discovers the same canonical bodies at `.agents/skills/` natively. One skill
  set, zero copies.
- **Session-start hook** — injects the `using-the-harness` orientation skill at
  startup, after `/clear`, and after compaction. Requires `bash` on PATH; without it
  the plugin degrades to skill discovery without injection.
- **Slash commands** — `/join-the-team:bootstrap`, `/join-the-team:init`, and
  `/join-the-team:validate`.

## Verify

1. In a fresh session, ask "which skills are available?" — `using-the-harness` and the
   baseline skills should be named.
2. Run `/join-the-team:validate` in a repository that has been bootstrapped; expect
   `PASS operating-model validation` (a `seed` profile may pass with warnings).

## Standards

The portable entry point is the root `plugin.json`, which follows
[Agent Plugins 1.0.0](https://agent-plugins.org/specification); the skills follow
[Agent Skills](https://agentskills.io/specification). `.claude-plugin/plugin.json` is the
Claude Code **projection** of that manifest, declared in the root manifest's `extensions`
block under `com.anthropic.claude-code` alongside `commands/` and `hooks/hooks.json`. Both
manifests must agree on name and version or CI fails.

## Update

Reinstall with the same two commands. The packaging drift validator
(`python3 scripts/validate_plugin.py --root .`) and the conformance gate
(`--spec-only`, wired as `make spec-conformance`) both run in this repository's own CI.
