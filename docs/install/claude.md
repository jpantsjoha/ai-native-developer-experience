# Install — Claude Code

Choose an installation scope from your shell:

```bash
claude plugin marketplace add jpantsjoha/ai-native-developer-experience
claude plugin install join-the-team@join-the-team-marketplace --scope user
```

Use `--scope project` instead to record enablement in the repository’s shared Claude
settings, or `--scope local` for yourself in this repository only. Each teammate still
installs the plugin on their machine. Preserve existing settings and keep credentials
out of shared configuration. Follow the host’s reload/install result.

Open the consumer project and run `/join-the-team:bootstrap`, then `:init` and `:validate`.
These commands use scripts from the installed package; no project-local skills copy is
needed. Bootstrap creates the project contract, not a global authority policy.

What gets wired:

- **Skills** — the 25 `skills/` capabilities. `skills/` is a real directory at the
  Agent Plugins fixed discovery location, so it survives installers that flatten
  symlinks; `.agents/skills/` is a relative symlink alias kept for Codex and Kimi,
  which discover there natively. One skill set, zero copies.
- **Session-start hook** — injects a short adoption pointer for unadopted projects, or the
  compact orientation pointer; full `using-the-harness` content is opt-in with
  `JOIN_THE_TEAM_ORIENTATION=full`. Requires `bash` on PATH; without it
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

Use the host’s plugin update flow for your selected scope. The packaging drift validator
(`python3 scripts/validate_plugin.py --root .`) and the conformance gate
(`--spec-only`, wired as `make spec-conformance`) both run in this repository's own CI.

Scope and package-path behaviour checked against the official
[installation documentation](https://code.claude.com/docs/en/discover-plugins#choose-an-install-scope)
and [plugin variables](https://code.claude.com/docs/en/plugins-reference#environment-variables)
on 16 October 2026. Local regression tests simulate package-path substitution; they do
not attest every live host version.
