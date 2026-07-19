# Install — Antigravity (Gemini)

Install as a plugin from the repository:

```bash
agy plugin install https://github.com/jpantsjoha/ai-native-developer-experience
```

Reinstall with the same command to update.

What gets wired:

- **`gemini-extension.json`** — declares the extension and points `contextFileName`
  at this repository's `GEMINI.md`, the always-on adapter carrying the operating
  contract.
- **Skills** — the `.agents/skills/` library, the same canonical set every harness
  loads.

## Verify

1. Start a session: the harness contract should be active from the first message.
2. Ask "which skills are available?" — the 14 skills should be named.

## Notes

- The `GEMINI.md` adapter and the generated `AGENTS.md`/`CLAUDE.md` adapters carry an
  identical protected contract block; the operating-model validator fails on semantic
  drift between them.
