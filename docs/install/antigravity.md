# Install — Antigravity (Gemini)

Antigravity is this harness's home surface — the skills, rules, and MCP seams in this
repository were built and battle-tested on Google Cloud's agent stack (IDE, Agent
Manager, and `agy` CLI) before anywhere else.

Install as a plugin from the repository:

```bash
agy plugin install https://github.com/jpantsjoha/ai-native-developer-experience
```

Reinstall with the same command to update.

## What gets wired

- **`gemini-extension.json`** — declares the extension and points `contextFileName`
  at `GEMINI.md`, the always-on Rules primitive carrying the operating contract
  (design-before-generate, the Adversarial Gate, receipts-not-polish).
- **Session start** — the plugin's session-start hook injects the `using-the-harness`
  orientation skill; on non-Claude runners it emits the SDK-standard
  `additionalContext` shape Antigravity consumes.
- **Skills** — the 19 `.agents/skills/` capabilities, discovered natively.
- **MCP data seams** → `.agents/mcp_config.json` — the governed tool-access pattern;
  see the file before adding servers.
- **Tool mapping** — `using-the-harness/references/antigravity-tools.md` translates
  the skills' action vocabulary (subagent dispatch, task artifacts, file/search
  actions) to Antigravity's native tools. The meta-skill points to it; canonical
  skill bodies never change per harness.
- **Agent Manager lanes** — the operating model's lane discipline applies to
  delegated/background work: one mutating lane per worktree, one integration owner.

## Verify

1. Start a session: the harness contract should be active from the first message.
2. Ask "which skills are available?" — the 19 skills should be named, including
   `gcp-expert` and `adk-expert`.
3. Ask the agent to track a small multi-step task — it should create a **task
   artifact**, not reach for a todo tool.

## Notes

- The `GEMINI.md` adapter and the generated `AGENTS.md`/`CLAUDE.md` adapters carry an
  identical protected contract block; the operating-model validator fails on semantic
  drift between them.
- Live `agy plugin install` verification is performed on a real Antigravity install
  before each listing update; everything else in this package is covered by
  `make check`.
