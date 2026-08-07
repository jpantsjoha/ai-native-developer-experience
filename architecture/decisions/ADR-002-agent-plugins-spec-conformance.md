# ADR-002: Conform to Agent Plugins 1.0.0 Without Reshaping the Repository

## Status

Accepted — 2026-08-07

## Context

[Agent Plugins 1.0.0](https://agent-plugins.org/specification) defines a cross-client
packaging standard: one root `plugin.json`, fixed component locations (`skills/`,
`mcp.json`), a closed manifest schema, reverse-domain client extensions, and path-safety
rules. Skills within it follow [Agent Skills](https://agentskills.io/specification).

Before this decision the plugin shipped four vendor manifests — `.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`, `.kimi-plugin/plugin.json`, `gemini-extension.json` — and
**no root manifest**, which is the standard's single hard requirement. Every other gap was
downstream of that: no `$schema` anywhere, no declared client extensions, and no gate
asserting that the 21 skills satisfy the Agent Skills frontmatter contract.

The credibility argument is sharper than the technical one. This plugin's entire pitch is a
shared, drift-checked contract that stops teams forking their rules per tool. Shipping it as
a vendor-forked package with no portable entry point undercuts the claim it sells.

The tension: the repository's own architecture puts canonical skills in `.agents/skills/`
(stated in GEMINI.md, encoded in the Makefile, the Kimi manifest, the validator, and every
install guide), while the standard fixes discovery at `skills/`.

## Options considered

### Option A — Reshape the repository to the standard's literal layout

Move the 21 skill directories to `skills/`, promote `.agents/mcp_config.json` to a root
`mcp.json`, and rename vendor directories to reverse-domain namespaces.

Maximally literal, and wrong on three counts. Renaming `.claude-plugin/` breaks Claude Code
discovery outright. Promoting the MCP template makes conformant clients spawn
`@example/mcp-data-server`, which fails for every user. Moving the skills rewrites 21
directories' history and contradicts a documented architecture for no conformance gain — the
standard accepts a symlink at the fixed location.

### Option B — Declare conformance in documentation

Add the root manifest and a README claim, and stop there.

Rejected on the harness's own *receipts, not polish* rule. An unverified conformance claim is
exactly the "confident but wrong" output this repository exists to prevent, and it rots
silently the first time a file moves.

### Option C — Add the portable surface, keep the internal shape, gate both

Add the root `plugin.json` as the portable entry point. Keep `.agents/skills/` canonical
behind the existing relative `skills/` symlink. Ship no root `mcp.json`. Keep vendor
directories under their current names and *declare* them via `extensions`. Enforce all of it
with a validator gate wired into CI.

## Decision

**Option C.** Specifically:

1. **Root `plugin.json` is the portable entry point.** It carries only the ten
   schema-permitted keys. The four vendor manifests remain as client-specific projections and
   join the existing name/version drift check, so the package cannot ship six manifests
   claiming different versions.

2. **`.agents/skills/` stays canonical; `skills/` stays a relative symlink.** This is
   spec-legal — the standard requires only that the fixed location resolve inside the plugin
   root after symlink resolution. The validator now enforces exactly that: the link must be
   relative, must resolve in-root, and must expose the same skill set.

3. **No root `mcp.json` is shipped.** The file is optional in the standard.
   `.agents/mcp_config.json` remains a template, corrected to spec shape — `$schema` present,
   `"type": "stdio"` on every server, and the former `_about` / `_note` / `_exposedTools`
   annotations moved to prose because `additionalProperties: false` would make a copied file
   invalid. The validator still checks `mcp.json` *if one ever appears*, so the day a real one
   lands it lands conformant.

4. **Vendor directories keep their names and are declared, not relocated.** The standard
   treats unknown top-level directories as non-errors. `extensions` declares
   `com.anthropic.claude-code`, `com.google.gemini-cli`, and `ai.moonshot.kimi`, and every
   declared plugin-relative path is resolved on disk by the validator.

5. **Conformance is a gate, not a claim.** `scripts/validate_plugin.py --spec-only` runs as
   `make spec-conformance` and as its own named CI job, backed by 22 negative fixtures.

The conformance checker is hand-rolled and standard-library only, because the validator must
run offline in CI with no third-party dependency. **The cost is explicit: a specification
version bump obliges a re-read of the published schemas, not merely an edit to the
validator.** That obligation is this ADR's, and it binds.

## Consequences

### Easier

- The plugin loads under any conformant client from one portable manifest.
- Skill frontmatter is now machine-checked against Agent Skills, not assumed. The previous
  check read only `name`; `description` presence and the 1024-character limit went unverified.
- A moved `commands/` or `hooks/hooks.json` now fails CI instead of shipping a lying manifest.
- The MCP template teaches a shape that stays valid when copied.

### Harder

- Six locations now carry the version string. Mitigated by the drift check, not by discipline.
- Two schemas are mirrored in Python and can drift from the published originals. Mitigated by
  asserting the exact `$schema` const and by the obligation recorded above.
- The `skills/` symlink does not survive `git archive`, zip packaging, or Windows checkouts
  without developer mode. Accepted, and documented in the README as a known packaging
  constraint of this choice.

### Foreclosed

- Renaming vendor directories to reverse-domain namespaces while Claude Code, Gemini CLI, and
  Kimi discover them by their current fixed names.
- Shipping a root `mcp.json` that names servers the project does not control.
- Declaring conformance on documentation alone.

## Adversarial Gate

**Verdict:** PASS — 22 negative fixtures, each mapped to a check the gate claims to make.

| Failure mode | Mitigation / ownership |
| --- | --- |
| The gate always passes and is therefore decoration | Every check has a negative fixture in `tests/test_plugin_packaging.py::SpecConformanceTests` that must fail it. The suite proves the gate bites; a check without a failing fixture is not considered implemented. |
| Hand-rolled validation silently diverges from the published schemas | The exact `$schema` const is asserted, so a spec bump breaks loudly rather than passing under stale rules. This ADR records that a version bump requires re-reading the published schema. |
| The `skills/` symlink is lost in packaging or on Windows | Documented as a known constraint in the README and here. The validator enforces the properties that make the link survivable — relative target, in-root resolution, matching skill set. |
| Six manifests drift on version or name | The root manifest joins the pre-existing coherence check rather than relying on release discipline. |
| Declared `extensions` paths rot as files move | Every plugin-relative extension path is resolved on disk and must exist and stay in-root, matching how the validator already treats `contextFileName` and the hook script. |
| The MCP template is copied and fails validation | The template is corrected to spec shape; the narrative that would have invalidated it moved to prose. Non-spec `${VAR}` placeholders are documented as passed through literally. |
| Conformance is claimed for skills that were never checked | Skill frontmatter is validated against Agent Skills — name pattern, 64-character cap, directory-name match, non-empty description, 1024-character cap. |

### Conditions carried into implementation

- A conformance check without a failing negative fixture is not implemented.
- A specification version bump requires re-reading the published schemas before editing the
  validator.
- The root manifest never carries a key outside the ten the schema permits, whatever a client
  would find convenient.
- If a real root `mcp.json` is ever added, it names servers this project controls.
