# Deterministic quality gates

Run `make check` at the repository root before handing off a candidate. It runs
Markdown lint, Python compilation and shell syntax checks, regression tests,
operating-model/package validation, delivery-record validation and spec conformance.
`make typecheck` is a historical target name: compilation is syntax validation,
not a semantic type checker. No provider or hook is executed by the syntax gate.

The existing GitHub workflow runs `make typecheck` and `make test`; the latter invokes
`make planning`. Its separate jobs run Markdown lint and packaging conformance.
This establishes local/YAML wiring, not proof that a remote run passed or that branch
protection requires every check. No remote protection was changed by this slice.

## Delivery-record gate

```bash
make planning
python3 scripts/validate_delivery.py --root . --json
python3 /path/to/plugin/scripts/validate_delivery.py --root /path/to/adopter --policy .delivery.json
```

The validator uses Python's standard library, no network, credentials or model.
It reads without rewriting records or executing their commands. Exit 0 means the
declared structural checks passed; 1 means findings; 2 means a harness/I/O failure.
Both nonzero exits block the gate. JSON includes scope, checked counts and stable
finding codes. An unreadable file is never a successful empty scan.

`.delivery.json` is a reviewed inventory, not a second task tracker:

- `version`: integer `1`.
- `documents`: nonempty role→relative-file mapping, including `vision`, `roadmap`,
  `status`, `changelog`. Extra project-owned roles are allowed.
- `records`: nonempty kind→relative-directory mapping. Kinds are `spec`, `decision`,
  `epic`, `task`. Each configured root must contain Markdown records; new `*.md`
  records are discovered recursively. Omit epic/task roots when the project has no
  local work-item mirror. This repository retains GitHub/unfiled follow-ups separately.

Missing/empty files or roots, duplicate JSON keys, unknown policy fields, wrong types,
overlapping record roots and unsafe paths fail. Nested symlinked record directories
are unsupported; a configured root alias and file symlinks must resolve within the
repository, and resolved records cannot overlap. Files are bounded to 1 MB.
An inventory change is a scope change for review; this local file is not tamper-proof.
Do not remove required inputs to make a failure green.

## Record grammar

Specs, epics and tasks use one visible, single-line bold field per value:

```markdown
**Task ID:** TASK-001
**Status:** Ready
**Parent:** EP-001
**Depends on:** REQ-001, ADR-001
```

Use `Spec ID` or `Epic ID` for those kinds. IDs are unique uppercase segments ending
in a numeric suffix. A task requires an existing epic parent; a standalone spec does
not require an epic. Dependencies are comma-separated existing record IDs. Duplicate
metadata, invalid IDs/states, missing relationships and dependency cycles fail.

ADRs retain the repository's existing `# ADR-001: Title` and `## Status` section.
The status occupies the next nonblank line, optionally followed by ` — ` and a dated
annotation. A bold `Status` field is also supported, but using both is ambiguous.

| Kind | Allowed states |
| --- | --- |
| spec | Draft, Accepted, In progress, In review, Done, Blocked, Superseded |
| epic | Draft, Accepted, Ready, In progress, In review, Done, Blocked, Parked, Superseded |
| task | Proposed, Ready, In progress, In review, Done, Blocked, Parked, Superseded |
| decision | Proposed, Accepted, Rejected, Superseded |

`Superseded` requires `**Superseded by:** ID` pointing forward to a different record
of the same kind. Missing successors, self-links and cycles fail. That field on a
non-superseded record fails too. `Done` requires `**Evidence:**` with inline local
Markdown links to nonempty regular files. Evidence paths must stay within the root.
This checks receipt presence, not its contents, authenticity or candidate freshness.

Fenced blocks (backticks/tilde), four-space/tab code examples, HTML comments and exact
single-line inline backtick code are masked before extracting fields and links.
Multiline/unmatched inline backticks fail with `GRAMMAR`: use a fenced example,
keep the span on one line, or escape a literal backtick. This intentional restriction
avoids inferring CommonMark block boundaries and silently hiding visible metadata.
Metadata must be plain
visible fields, not tables, blockquotes, wrapped values or code-formatted IDs.
The link checker supports inline links/images, balanced parentheses, angle destinations,
and defined full/collapsed/shortcut references. Explicit unresolved references fail;
bare brackets with no definition are prose. Local targets must exist. External schemes
are not fetched; heading fragments and remote URLs are not validated. This is a bounded
Markdown grammar, not a general CommonMark semantic validator.

## What a green gate does and does not establish

This gate establishes structural coherence for the declared inventory. It does not
infer contradictions in prose, inspect live issue state, verify acceptance-test
execution, authenticate a reviewer or authorise merge/release. Existing review-gate
fixtures and operating-model validation cover their own narrower contracts.
Independent review and actual outcome evidence remain necessary.

`tests/test_delivery_validation.py` plants missing records, invalid metadata, cycles,
broken links, empty evidence and path escapes against the actual CLI. The fixtures
run offline under the existing test target; they do not call paid providers. Extend
them when a defect escapes. Do not add another skill to compensate for a missing gate.

Remaining work in [ROADMAP](ROADMAP.md): semantic/current-fact reconciliation,
requirement→executed-test coverage, authenticated review enforcement, context freshness
and release provenance. This slice completes a bounded structural FR-8 gate, not all
of DPS-001 or all delivery controls.
