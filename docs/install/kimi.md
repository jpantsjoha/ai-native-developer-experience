# Install — Kimi Code

Install directly from the repository:

```text
/plugins install https://github.com/jpantsjoha/ai-native-developer-experience
```

What gets wired (via `.kimi-plugin/plugin.json`):

- **Skills** — the manifest points `skills` at `./.agents/skills/`, Kimi Code's native
  project-skill location.
- **Session start** — the manifest's `sessionStart` field loads `using-the-harness`
  from the first message.
- **Tool mapping** — the manifest's `skillInstructions` translate the skills' action
  vocabulary (ask the user, todos, subagent dispatch, skill invocation) to Kimi Code's
  native tools.

## Verify

1. `/plugins` should list `join-the-team` as installed.
2. A fresh session should show the harness orientation; ask "which skills are
   available?" to see the 21 skills.

## Standards

The portable entry point is the root `plugin.json`, which follows
[Agent Plugins 1.0.0](https://agent-plugins.org/specification); the skills follow
[Agent Skills](https://agentskills.io/specification). `.kimi-plugin/plugin.json` is the Kimi
**projection** of that manifest, declared in the root manifest's `extensions` block under
`ai.moonshot.kimi`. The Kimi manifest carries fields the portable schema does not define —
`sessionStart`, `skillInstructions`, `interface` — which is exactly why it stays a separate
projection rather than being folded into the root.

## Update

Reinstall with the same command.
