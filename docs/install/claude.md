# Install — Claude Code

Install from the repository as a marketplace plugin:

```bash
/plugin marketplace add jpantsjoha/ai-native-developer-experience
/plugin install join-the-team@join-the-team-marketplace
```

What gets wired:

- **Skills** — the 14 `.agents/skills/` capabilities, discovered via the plugin's
  `skills/` alias.
- **Session-start hook** — injects the `using-the-harness` orientation skill at
  startup, after `/clear`, and after compaction. Requires `bash` on PATH; without it
  the plugin degrades to skill discovery without injection.
- **Slash commands** — `/join-the-team:bootstrap` and `/join-the-team:validate`.

## Verify

1. In a fresh session, ask "which skills are available?" — `using-the-harness` and the
   baseline skills should be named.
2. Run `/join-the-team:validate` in a repository that has been bootstrapped; expect
   `PASS operating-model validation` (a `seed` profile may pass with warnings).

## Update

Reinstall with the same two commands. The packaging drift validator
(`python3 scripts/validate_plugin.py --root .`) runs in this repository's own CI gate.
