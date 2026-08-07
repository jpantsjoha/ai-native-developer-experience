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

Add the root `plugin.json` as the portable entry point. Put the real skill directory at the
standard's fixed `skills/` location and keep `.agents/skills/` as a relative symlink alias.
Ship no root `mcp.json`. Keep vendor directories under their current names and *declare* them
via `extensions`. Enforce all of it with a validator gate wired into CI, and prove the result
by installing into every supported client.

## Decision

**Option C.** Specifically:

1. **Root `plugin.json` is the portable entry point.** It carries only the ten
   schema-permitted keys. The four vendor manifests remain as client-specific projections and
   join the existing name/version drift check, so the package cannot ship six manifests
   claiming different versions.

2. **`skills/` is canonical and a real directory; `.agents/skills/` is the relative
   symlink alias.** *(Revised 2026-08-07 after live install testing — see "Revision" below.)*
   The standard's fixed discovery location holds the real files, so no installer can flatten
   it away. The alias is kept because Codex and Kimi discover `.agents/skills/` natively. The
   validator enforces both halves: `skills/` must not be a symlink, and the alias must be
   relative, in-root, and expose the same skill set.

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
- Two hook manifests now exist (`hooks/hooks.json` and root `hooks.json`) because Claude Code
  and Antigravity read different locations. Duplication is drift surface; the validator
  requires them byte-identical.
- The `.agents/skills` alias can still be dropped by a flattening installer. That is now the
  tolerable direction of failure: the clients that lose it (Codex-style caches) are the ones
  that would look at `skills/` anyway, and `skills/` is real.

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
| A symlink at the fixed location is dropped by an installer, leaving zero skills | Observed for real in Codex's install cache. `skills/` is now a real directory and the validator **fails** if it is ever a symlink again. |
| Antigravity silently registers no session-start hook | Root `hooks.json` now ships beside `hooks/hooks.json`, and the validator requires both to exist and match byte-for-byte. |
| A developer's own upgraded install masks a defect | Verification must use a *clean* install. The stale root `hooks.json` from a July import hid a hook that had never worked in any release. |
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

## Revision — 2026-08-07: what live install testing changed

The original decision kept `.agents/skills/` canonical behind a `skills/` symlink, on the
reasoning that the standard permits a symlink at the fixed location. That reasoning was
correct about the specification and wrong about the world. Installing the package into four
real clients produced evidence the static gate could not:

| Client | Result |
| --- | --- |
| Claude Code | Installed 0.2.0; 21 skills + 3 commands; SessionStart hook registered; symlink preserved |
| Kimi Code | Updated to 0.2.0; skills confirmed at runtime by a live session |
| Antigravity (`agy`) | Installed; skills and commands loaded; **`hooks: skipped (not found)`** — a regression against 0.1.7, which processed the hook |
| Codex | Installed and enabled; **`skills/` symlink dropped by the install cache** |

Two findings forced changes:

1. **Codex's install cache drops symlinks.** Its marketplace clone had the link; the
   installed copy did not. Codex itself was unaffected — it discovers `.agents/skills/`
   natively — but any conformant client relying on the fixed location would have found zero
   skills. The layout is now inverted: `skills/` real, `.agents/skills/` the alias.
2. **The root manifest silently disabled Antigravity's session-start hook — a regression
   introduced by this ADR's own decision 1.** `agy` runs two discovery modes. With no root
   `plugin.json` it uses legacy discovery and finds `hooks/hooks.json`. With a root
   `plugin.json` present it switches to Agent Plugins mode and reads `hooks.json` at the
   package root *only*. Adding the conformance manifest therefore turned a working hook off.

   Proven by a single-variable experiment: an untouched v0.1.7 tree installs with
   `hooks: 1 processed`; copying in nothing but `plugin.json` flips the same tree to
   `hooks: skipped (not found)`. The fix is to ship both manifests.

### Corrections to the first draft of this revision

Two claims in the first draft were wrong, and are corrected here rather than quietly edited:

- **"Antigravity had never received a session-start hook; broken in every release from
  0.1.0."** False. It worked in 0.1.7. The defect was a regression introduced in 0.2.0 by the
  root manifest, as shown above. The first diagnosis mistook a self-inflicted regression for a
  long-standing bug, and built a supporting narrative around a stale artefact in the
  developer's own install.
- **"`agy plugin validate` rejects v0.1.7 and v0.1.3, so Antigravity's loader had been
  refusing every previously released version."** False. `agy plugin **install**` succeeds on
  v0.1.7 — 21 skills, hook processed. Only the stricter `validate` subcommand requires a root
  `plugin.json`. Conformance did not repair a pre-existing breakage; there was none.

The root manifest is still required — by the specification and by `agy plugin validate` — but
it must not be credited with fixing something that was never broken.

**The lessons carried forward:**

1. A schema gate proves a package is *well-formed*, never that it is *installable*. Both are
   required before a release, so the checklist now includes a live install into each supported
   client, verified against a **clean** install.
2. **Adding a manifest can change a client's mode, not merely add metadata.** Conformance work
   is a behavioural change and must be regression-tested against the clients that already
   worked — not only against the specification.
3. When a live test contradicts a hypothesis, isolate one variable before writing the
   conclusion down. Both false claims above came from reading two different subcommands
   (`validate` and `install`) as one signal.

## Revision — 2026-08-07: the gate had holes, found by cross-model review

Every PR from `v0.1.7` to `v0.2.2` was authored and self-merged by one model with
`reviews=0`. That breaks the project's own review doctrine — neither author both writes and
approves — and it cost something real.

An independent review of the cumulative diff by a second model (Codex) found **three defects
in the conformance gate itself**, each of which the gate passed:

| Defect | Why it passed |
| --- | --- |
| MCP transport fields presence-checked, not type-checked | The required-key check saw the key; `isinstance` guards then skipped every subsequent check, so `"command": null` validated |
| `cwd` accepted traversal outside the plugin root | The published schema anchors only the *prefix* and defers containment to the client; a prefix-only check accepts `./../outside` |
| A malformed `version` shipped silently | `version` is optional in the standard and SemVer only recommended, so `"banana"` across all six manifests passed both gates |

All three were reproduced before being accepted, and all three now have negative fixtures
(22 → 33). The `cwd` fix deliberately still accepts `${PLUGIN_ROOT}/a/../b`, which never
leaves the root — rejecting traversal is not the same as rejecting `..`.

**The lesson, which is the same one this ADR keeps learning in new clothes:** the gate that
checks the work needs checking too, and it cannot check itself. A validator author is the
worst reviewer of that validator. This project's doctrine already said so; the doctrine was
simply not followed. From here, conformance-gate changes get an independent cross-model
review before merge, not after release.
