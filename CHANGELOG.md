# Changelog

Material changes to the public harness are recorded here. Public-source attribution is
included only where a change directly adopts or discusses an external pattern.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project
does not infer a repository release number from the internal version of one document or
operating-manual asset; from 0.1.0 the changelog tracks the `join-the-team` plugin
packaging version declared in the harness manifests.

## [0.2.3] — 2026-08-07

Independent cross-model review of `v0.1.7..v0.2.2` found three defects in the conformance
gate itself. Every one passed the gate before the review — the validator that was supposed
to stop bad packaging was letting them through.

### Fixed

- **MCP transport fields were presence-checked, not type-checked.** `{"type":"stdio",
  "command":null}` and `{"type":"streamable-http","url":null}` both passed: the required-key
  check saw the key, then `isinstance` guards silently skipped every subsequent check. All
  transport fields are now type-validated — `command`, `url`, `args`, `env`, `headers`, `cwd`.
- **`cwd` accepted traversal outside the plugin root.** The published schema anchors only the
  *prefix* and defers containment to the client, so `./../outside` and
  `${PLUGIN_ROOT}/../outside` were accepted. The suffix is now normalised and any component
  that climbs above its declared root is rejected. `${PLUGIN_ROOT}/a/../b` still passes — it
  never leaves.
- **A malformed version shipped silently.** `version` is optional in the standard and SemVer
  only *recommended*, so `"banana"` repeated across all six manifests passed both gates. A
  **local** SemVer rule now applies, marked as stricter than the standard.

### Changed

- Negative fixtures 22 → 46. Every finding above has a test that fails without its fix.

### Fixed (second review round, before merge)

A second independent pass on the *fix itself* found two bypasses in the new checks:

- **`cwd` traversal missed Windows separators.** `./..\\outside` escapes on a Windows
  client but looked like one innocent component to a slash-only split. Both separators are
  now normalised before the depth check.
- **The SemVer rule accepted Unicode digits and a trailing newline.** Python's `\d` matches
  `٢`, and `$` permits `1.2.3\n`. Now ASCII `[0-9]` throughout, applied with `fullmatch()`.

### Fixed (third review round, before merge)

- **Explicit `null` passed on every optional MCP field.** `args`, `env`, `cwd` and `headers`
  set to `null` were treated as absent, because `.get(k) is not None` cannot distinguish a
  missing key from a present null. Now checked by key membership. Omitting the field still
  passes — the fixture asserts both.

### Fixed (fourth review round, before merge)

- **A lexical `..` check could not see an in-root symlink pointing outside.**
  `${PLUGIN_ROOT}/escape/work`, where `escape` symlinks to `/tmp/outside`, counted as two
  ordinary components and passed while landing outside the package. Root-relative `cwd`
  values are now resolved on disk and checked for containment after symlink resolution.
  `${PLUGIN_DATA}` is client-managed and cannot be resolved at validation time, so it is
  exempt; an ordinary in-root directory still passes.

### Fixed (fifth review round, before merge)

- **A broken symlink slipped through containment.** `escape -> /not-yet-created` reports
  `exists() == False`, so the climb-to-nearest-ancestor loop walked straight past it to the
  root and accepted the path — which would escape the moment the client created the target.
  The loop now uses `os.path.lexists`, which sees the link itself.

### Fixed (sixth review round, before merge)

- **A doubled separator false-rejected a valid path.** `.//workdir` left `/workdir` after
  prefix stripping, and `root / "/workdir"` discards the root and yields an absolute path —
  so the validator reported an in-root directory as an escape. Leading separators are now
  stripped.
- **Unresolvable paths are treated as outside.** `Path.resolve()` can raise `RuntimeError`
  on symlink loops for some platforms and versions; only `OSError`/`ValueError` were caught.
  Hardening only — the crash was **not** reproduced on macOS/CPython here, where the loop
  resolved without raising.

### Fixed (seventh review round, before merge)

- **A POSIX validator accepted Windows-absolute symlink targets.** A symlink to `C:\out` or
  `\\server\share` reads as an innocent relative name on Linux/macOS, while the Windows
  client consuming the package treats it as absolute and starts the server outside the root.
  Symlink targets are now judged as text, covering drive-qualified, rooted and UNC forms.
  An ordinary relative symlink to a sibling directory still passes.

### Fixed (eighth review round, before merge)

- **`${PLUGIN_DATA}` traversal was accepted unverified.** That directory is client-managed
  and cannot be resolved at validation time, so `link/../work` survived the lexical
  depth check while escaping if the client made `link` a symlink. `..` is now refused for
  `${PLUGIN_DATA}` paths; plain paths under it still pass.

## [0.2.2] — 2026-08-07

### Fixed

- **Three README links returned 404 on GitHub.** Inverting the skill layout in 0.2.1 made
  `.agents/skills/` a symlink, and GitHub's web UI does not traverse symlinked directories.
  Links to the skills library, `plugin-submission`, and `operating-model-bootstrap` all
  broke. They now point at the real `skills/` directory. Same fix applied in
  `DEVELOPER_EXPERIENCE.md`.
- **Install instructions told users to copy a symlink.** `README.md`, `BOOTSTRAP.md`, and
  `docs/install/codex.md` said to copy or vendor `.agents/skills/`; the canonical directory
  is `skills/`.
- **`docs/install/claude.md` described the pre-inversion symlink direction**, claiming
  `skills/` was the alias pointing at `.agents/skills/`. Reversed to match reality.

### Added

- **README now documents installation, configuration, usage examples, and troubleshooting**
  — the four things the Claude Plugin Hub creator guide asks for, and the two it scored this
  plugin as missing. New `Usage` (intent-to-skill routing table plus a worked risk-tiered
  example), `Configuration` (the three seams), `Troubleshooting` (six real failure modes with
  causes), and a `Verify the install` subsection.
- **Compliance with Agent Plugins 1.0.0 stated precisely**, citing the
  [Google announcement](https://developers.googleblog.com/agent-plugins-package-your-skills-tools-and-more/)
  and the standard's Technical Steering Committee. The conformance table now separates
  spec-required rules from local hygiene: the standard defines exactly two component types
  (skills, MCP), so commands and hooks are explicitly outside v1 (§7) and are declared as
  manifest extensions (§8.1). The package does **not** claim `.claude-plugin/` as a §8.2
  directory extension — those must be named after the namespace.

## [0.2.1] — 2026-08-07

Fixes two installability defects that only a live install into each client could surface.
0.2.0 reached `main` but was never tagged or released; 0.2.1 supersedes it.

### Fixed

- **Regression from 0.2.0: Antigravity stopped receiving its session-start hook.** Adding a
  root `plugin.json` switches `agy` into Agent Plugins mode, where it reads the hook manifest
  from `hooks.json` at the **package root** only; without a root manifest it uses legacy
  discovery and finds `hooks/hooks.json`. So the conformance work in 0.2.0 silently disabled
  a hook that worked in 0.1.7. Confirmed by a single-variable test: adding only
  `plugin.json` to an otherwise untouched v0.1.7 tree flips `hooks: 1 processed` to
  `hooks: skipped (not found)`. Both manifests now ship, and the validator requires them
  byte-identical.
- **A conformant client could install the plugin and find zero skills.** `skills/` was a
  symlink to `.agents/skills/`; Codex's install cache drops symlinks, so the standard's
  fixed discovery location vanished on install. The layout is inverted: **`skills/` is now
  the real directory** and `.agents/skills/` the relative alias for runners that discover
  there natively. The validator now fails if `skills/` is ever a symlink again.
- **The session-start hook no longer depends on a single discovery path.** It reads
  `skills/` first and falls back to `.agents/skills/`, so it survives whichever alias an
  installer drops.

### Changed

- Canonical skills moved from `.agents/skills/` to `skills/`. Existing `.agents/skills/...`
  paths keep working through the alias, so no adopter reference breaks.
- `.kimi-plugin/plugin.json` points `skills` at `./skills/`.

### Known limitations

- Installing via `codex plugin add` yields no `.agents/skills/` alias — Codex's install cache
  flattens the package and drops symlinks. All 21 skills are present at `skills/`, the
  standard's fixed location, which is exactly why the real directory now lives there. Use
  `.agents/skills/` only for a repository checkout.

## [0.2.0] — 2026-08-07

> Merged to `main` but never tagged or released; superseded by 0.2.1.

### Added

- **Agent Plugins 1.0.0 conformance.** The plugin now ships a root `plugin.json` — the
  portable entry point required by
  [Agent Plugins 1.0.0](https://agent-plugins.org/specification) — and its skills are
  checked against [Agent Skills](https://agentskills.io/specification). The four vendor
  manifests (`.claude-plugin/`, `.claude-plugin/marketplace.json`, `.kimi-plugin/`,
  `gemini-extension.json`) stay as client projections and are now *declared* through the
  standard's `extensions` block under `com.anthropic.claude-code`,
  `com.google.gemini-cli`, and `ai.moonshot.kimi`, instead of being left for a client to
  discover by convention.
- **A conformance gate, not a conformance claim.** `make spec-conformance` runs
  `scripts/validate_plugin.py --spec-only` — standard-library Python, offline, reporting
  as its own CI job. It validates the root manifest shape, skill frontmatter (name
  pattern, directory match, description limits), path safety on the `skills/` fixed
  location, and MCP configuration should a root `mcp.json` ever be added. Backed by 22
  negative fixtures, because a validator that only ever passes is decoration.
- **[ADR-002](architecture/decisions/ADR-002-agent-plugins-spec-conformance.md)** recording
  the four decisions and their costs: keep `.agents/skills/` canonical behind the `skills/`
  symlink, ship no root `mcp.json`, keep vendor directories unrenamed, and accept the
  obligation to re-read the published schemas on any specification version bump.

### Changed

- **Skill validation now covers the whole Agent Skills contract.** The previous check read
  only the frontmatter `name`; `description` presence and the 1024-character limit went
  unverified.
- **`.agents/mcp_config.json` corrected to spec shape.** Added `$schema` and an explicit
  `"type": "stdio"` per server, and moved the inline `_about` / `_note` / `_exposedTools`
  annotations into `DEVELOPER_EXPERIENCE.md`. Agent Plugins sets
  `additionalProperties: false` on server objects, so those keys would have made any copied
  file invalid. The file remains a template, never live configuration.
- **Author URL now points at <https://jpantsjoha.com>** across all manifests. The spec's
  `author` object permits exactly one `url`; an owned domain outlasts a platform profile.

### Known limitations

- The `skills/` alias is a relative symlink. A Windows checkout without symlink support
  (`core.symlinks=false`) replaces it with a plain text file holding the target path;
  enable developer mode or clone from an elevated shell. `git archive` in tar and zip
  form, and POSIX clones, preserve it — both verified.
- The conformance checker mirrors the published JSON schemas in Python rather than
  fetching them, so the validator runs offline. A specification version bump therefore
  requires re-reading the source schemas, not only editing the validator.

## [0.1.7] — 2026-07-23

### Added

- **Existing-repo requirement backfill.** Adopting into a repo that already has code no
  longer starts from a blank seven-area form. A read-only inspection pass
  (`inspect_repo.py`) reads manifests, tool configs, CI, `CODEOWNERS`, and docs and emits
  **inferred** findings — each a machine guess with an evidence pointer and a ready-to-paste
  `inferred — source: <evidence>; confirm: <role>` marker. It is strictly read-only,
  vendor-neutral, and **never infers authority** (roles/accountability stay human-owned).
  `init` now runs it for existing repos and confirms each field one at a time.
- **Provenance-aware operating profiles.** Profile fields can carry an `inferred` state
  alongside `verified` facts and `unknown` placeholders. The validator recognises it — a
  `seed` warns on unconfirmed inference, and promotion to `active` is **blocked** until a
  human confirms every inferred field. This is the gate that keeps machine-backfilled
  values from ever masquerading as owned facts.

## [0.1.6] — 2026-07-23

### Added

- A README **"What it looks like"** section with a live session screenshot.

### Changed

- `the-architect` and `operating-model-bootstrap` now teach a single, coherent ADR
  convention for adopting teams: ADRs live in `ADR/`, with a decision's lifecycle visible
  in both the filename postfix (`-DRAFT` / `-approved`) and an in-file `status:` field.
  This replaces the prior `architecture/decisions/` + inline-Status guidance.

## [0.1.5] — 2026-07-23

### Added

- `governance-guardrail`: checks proposed stack, data flows, and cloud choices against
  declared enterprise policies, compliance frameworks, and security controls. Never
  invents a policy position — surfaces gaps as explicitly owned unknowns. Triggered by
  `delivery-orchestrator` at R2/R3 classification; feeds into `adversarial-gate`.
- `release-manager`: governs the SemVer release process — versioning discipline,
  tag-based GitHub releases, changelog hygiene, and the ADR that confirms the release
  strategy is agreed. Distinct from `release-readiness` (deployment gate) and
  `github-manager` (CI infrastructure). Owned by `delivery-orchestrator`.

### Changed

- `operating-model-bootstrap`: added a **Project awareness** section formalising the
  seven areas that must be established or explicitly owned at init time (product vision,
  team roster, technical stack, tooling, cloud/governance, automation, delivery controls).
  Required areas block `seed` → `active` promotion. The bootstrap workflow now records
  init decisions as a baseline ADR (`architecture/decisions/ADR-0000-baseline-structure.md`)
  and a first `docs/STATUS.md` entry, alongside the initializer-seeded `docs/VISION.md`
  and `docs/ROADMAP.md`.
- `delivery-orchestrator`: routing table extended with `release-manager`,
  `governance-guardrail`, and `github-manager`; delivery controls (area 7) explicitly
  owned here.
- `using-the-harness`: routing table extended with `release-manager` and
  `governance-guardrail`.
- Skill count updated to 21 across README, install guides, and skills library index.

## [0.1.4] — 2026-07-23

### Added

- `github-manager`: a new skill for cost-effective, consistent GitHub operations —
  CI trigger rightsizing, Actions billing guardrails, issue and label discipline,
  branch-protection policy, and release-workflow governance. Brings the skill count
  to 19.

## [0.1.3] — 2026-07-21

### Added

- Added a public privacy policy describing the plugin's local behavior, optional external
  connections, data handling, and user controls for marketplace and directory review.
- Extended the operating-model initializer with project-neutral vision, delivery
  workflow, roadmap, status, and changelog seeds. Existing project planning records are
  preserved, while conflicting operating contracts and surface adapters still block the
  installation before writes begin.

## [0.1.2] — 2026-07-20

### Changed

- Normalised `LICENSE` to the canonical Apache License 2.0 text so GitHub and directory
  tooling can reliably detect the project's Apache-2.0 licence.

## [0.1.1] — 2026-07-20

### Added

- `plugin-submission`: a cross-harness gate for policy-backed plugin and skill-directory
  submissions, artifact eligibility, exact final confirmation, and durable receipts.

## [0.1.0] — 2026-07-20

First packaging of the harness as the `join-the-team` multi-harness plugin: one
canonical skill set and operating contract, thin per-harness adapters, drift-checked
in CI. Antigravity (Gemini) is a first-class, live-verified surface; Kimi Code,
Claude Code, and Codex adapters ship to spec.

### Added

**Operating model kernel**

- A released, immutable operating-manual 2.1.0 asset with a SHA-256-bound project profile.
- A safe, non-overwriting day-one initializer for new repositories.
- Thin `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` adapters carrying one protected contract.
- Deterministic offline validation for manual/profile binding, adapter drift, adoption
  state, checkpoints, and exact-candidate evidence manifests.
- A day-one adoption example, bootstrap guide, evidence manifest, and baseline skill map.

**Plugin packaging and distribution**

- `join-the-team` manifests for Kimi Code (`.kimi-plugin/`) and Claude Code
  (`.claude-plugin/` plus a marketplace entry), and a `gemini-extension.json` for
  Antigravity/Gemini surfaces.
- A session-start `using-the-harness` meta-skill that orients the assistant before any
  work; a Claude Code session-start hook that injects it (with an SDK-standard
  fallback for non-Claude runners); and `/join-the-team:bootstrap`,
  `/join-the-team:init`, and `/join-the-team:validate` slash commands.
- Antigravity capability layer: `references/antigravity-tools.md` tool mapping.
  Live `agy plugin install` verified on Antigravity 1.1.1 (17 skills + hook).
- Per-harness install docs (`docs/install/`) and a README plugin-install section.
- A plugin-packaging drift validator — manifest name/version sync, skill references,
  discovery alias, hook scripts — with regression tests wired into `make check`.

**Skills and team workflow**

- Cloud-expert family: `aws-expert`, `azure-expert`, and `alibaba-expert`, each pairing
  guardrails with official-source validation — documentation, live-docs MCP servers,
  and official GitHub foundations/agent-example repositories. `the-architect` routes
  cloud decisions to the matching vendor skill.
- `docs/WORKFLOW.md`: the skills dependency diagram (Mermaid), the requirement →
  ADR → ticket → evidence → status traceability chain, and the accountability model.
- A team-roster-and-escalation section in the profile template plus a
  `/join-the-team:init` command to capture named human owners and their channels.
- A live-documentation seam and a knowledge-base seam (SharePoint/Confluence/Google
  Drive) in `.agents/mcp_config.json`; the repo ADR stays the decision of record.

**Attribution and integrations**

- `NOTICE`: author attribution that derivative works must carry (Apache-2.0 §4(d)).
  The author section and `NOTICE` feature the forthcoming books (*Building the
  Agentic Enterprise on Google Cloud*, Packt; *Mastering Multi-Agent Systems on
  Google Cloud*, AVA Publishing).
- `INTEGRATIONS.md`: an evaluated companion-plugin map — reference never vendor,
  capability never authority, and a standalone guarantee.
- A companion-capabilities section in the project operating profile template.
- Narrow public-source attribution plus currency and usage caveats.

### Changed

- Relicensed from PolyForm dual source-available terms to Apache License 2.0 to
  remove adoption friction for teams and commercial use; attribution is preserved
  through the `NOTICE` file.
- Renamed `gcp-well-architected` to `gcp-expert`, aligning the cloud skills into one
  expert family; `gcp-expert` gained the same official-source validation section.
- Reframed the repository as a **team-project AI harness bootstrap**, not a production
  application starter kit.
- Clarified that the operating kernel is model-, vendor-, and IDE-agnostic while discovery
  and invocation adapters remain platform-specific.
- Made `seed` a usable, honest state for system design, delivery planning, and R0/R1 work;
  R2/R3 requires an active profile with applicable controls resolved.
- Ordered risk classification before authority confirmation so approval is scoped to the
  actual risk.
- Allowed namespaced local development/test services in isolated worktrees while keeping
  shared operational/production-like services under a designated canonical owner.
- Replaced unsupported or conflated adoption statistics with qualified, primary-source
  links and labelled the 10/90 split as a heuristic.

### Fixed

- Added candidate identity to durable checkpoints and a matching evidence manifest.
- Corrected attribution: the anti-rationalisation table format was adopted after review of
  Addy Osmani's MIT-licensed `agent-skills`; JP's claimed contribution is the Adversarial
  Gate name and “how would I break this?” framing.
- Removed ambiguity between a universal manual and project-specific adoption metadata.
- Consistency sweep: install-doc skill counts and slash-command lists, and harmonised
  manifest descriptions across the four harness adapters.

### Known limitations

- The initializer cannot discover missing business/domain facts; the team and assistant
  must ground and own them in the profile.
- Local checks cannot authenticate reviewer identity or enforce remote repository policy.
- Skill auto-discovery and invocation differ by assistant and IDE.
- The initializer and validator require Python 3.10 or newer.
- Live plugin installs are verified on Antigravity (agy 1.1.1) only; Kimi Code, Claude
  Code, and Codex install paths are built to spec and pending live verification.
- Team-roster escalation and GH-issue traceability are documented conventions, not yet
  tool-enforced.
- The repository contains no usage telemetry; the licence cannot identify silent use.
