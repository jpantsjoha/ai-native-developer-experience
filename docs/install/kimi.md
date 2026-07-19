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
   available?" to see the 17 skills.

## Update

Reinstall with the same command.
