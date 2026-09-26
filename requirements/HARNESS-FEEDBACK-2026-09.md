# Harness feedback — September 2026

**ID:** HFE-001 · **Owner:** jpantsjoha · **Date:** 2026-09-26

## Authority and scope

The operator requested a parallel, source-backed workflow audit of mac-control,
FeedEval and gcp-exam-prep, and a separate enhancement branch in this repository.
This authorises local audit, documentation and reversible plugin improvements.
It does not authorise merging, tagging, publishing, changing remote protection or
deploying an adopter. Those remain separate delivery decisions.

This is an implementation slice of accepted DPS-001, not a replacement constitution.
Risk: R2 for the multi-file slice; review-control changes receive R3 scrutiny.
The immutable operating manual and adopter authority remain unchanged.

Audit sources are `/Users/jp/local/mac-control`,
`/Users/jp/local/ChromeExt-FeedEval`, `/Users/jp/local/gcp-exam-prep`, and the
original `ai-native-developer-experience` checkout under the operator's iCloud
Documents/workspaces directory. Integration is isolated at
`/Users/jp/local/ai-native-developer-experience-audit`; durable review receipts go
under `/Users/jp/local/ai-native-developer-experience-audit-evidence/` outside its
tree. Original checkout untracked/dirty content is evidence only, never staged.

## Outcome and acceptance

| ID | Requirement | Evidence |
| --- | --- | --- |
| HFE-1 | Compare declared, implemented, enforced and observed controls in four repositories | Source-backed audit with SHAs, dirty-state caveats and remote read receipts |
| HFE-2 | Connect vision, objectives, requirements, decisions, tasks, tests, review, release and observations | Portable workflow guide and owned record matrix |
| HFE-3 | Match task complexity and risk to model effort without hard-coding machine aliases as capabilities | Council routing procedure, bounded lane contract and explicit availability/fallback rules |
| HFE-4 | Define maturity exits and release promotion without equating tags with readiness | MVP/beta/production evidence table and test/CI/promotion contract |
| HFE-5 | Correct the local review gate's result propagation and unsafe success paths | Offline stub tests reproduce the base defect and prove refusal on missing/failed/ambiguous review |
| HFE-6 | Reconcile this repository's status, roadmap, README and pending delivery work | Honest branch status, ordered backlog with issue-ready acceptance criteria, Unreleased entry |
| HFE-7 | Inspect additional recently updated local projects for material portable improvements | Follow-up comparison records source identities, dirty caveats, evidence limits and prioritised acceptance cases; guidance extends existing skills |

## Design and boundaries

Extend existing skills with concise routing pointers and portable reference procedures.
Keep detailed lifecycle guidance in one document. Keep project-specific model aliases,
CLI restrictions and permissions in profiles/adapters. Add no new model dependency.
Fix the existing review helper; do not build a second council service or claim that a
local receipt authenticates reviewer identity. No hosted enforcement is changed.
Gate acceptance includes: only one exact PASS from a successful lane may succeed;
CONCERNS, missing CLI, malformed output, timeout and non-zero lane exit refuse;
failed diff acquisition and oversized inputs refuse rather than reviewing truncated
input; unique per-run artifacts under the current worktree git directory prevent
same-second collisions. PR review defaults to no comment; posting needs explicit
`--comment`. Record full base/head or staged tree plus diff digest; bind the result
to those inputs and reject changed inputs after review. Async mode remains advisory.
An async pre-commit worker reviews the saved immutable snapshot; completing the
commit must not invalidate that historical review. Mapping it to a later commit or
merge decision requires a separate current-identity check. Synchronous blocking
review still rejects a changed live candidate.
CLI invocation retains supported noninteractive arguments with a conservative input
size cap; no unverified stdin transport or automatic command-capability assumption.
An issue-ready local backlog is the task contract until external issue creation is
authorised; it must be labelled unfiled, not presented as GitHub tracking.

## Work and validation plan

1. Read-only audits: FeedEval and exam-prep in parallel; parent audits mac-control
   and this repository. Each returns paths, evidence, uncertainty and reusable lessons.
2. Independent council challenges this plan before review-control implementation.
3. One isolated gate implementation lane owns only `scripts/review-gate.sh` and its
   regression tests. Parent owns documentation and skill integration in this worktree.
4. Run baseline reproduction, focused regressions, then `make check` after integration.
5. Fresh independent reviewer checks the exact assembled tree and open conditions.
6. Record evidence outside the reviewed tree, commit the reviewed tree, and leave the
   feature branch ready for the operator's next delivery decision.

Budget: maximum four active agents, one integration owner; audits eight minutes each,
implementation twenty minutes, council ten minutes per bounded question. At most one
retry after narrowing a failed review; no purchased capacity or unbounded loops.
Usage/cost unavailable from a lane must remain unknown, never zero.

## Failure modes and rollback

- Polished guidance could masquerade as implemented automation: every finding and
  backlog item carries its evidence level; pending validators remain pending.
- A reviewer may be unavailable or review the wrong tree: absence, failure, stale
  identity and conditions block review completion; retain exact tree identity.
- A local helper may be mistaken for remote enforcement: document its trust boundary
  and record branch-protection evidence separately.
- Existing untracked files in the original iCloud checkout may be user work: leave
  them untouched; work in an isolated local worktree from base `164946c`.

Rollback is to discard/revert this branch's changes. No adopter state, installed
plugin cache, remote policy or live environment is mutated by this slice.

## Plan challenge — 2026-09-26

Gemini `agy` returned BLOCK. Its useful conditions were explicit source/receipt
paths, refusing missing/failed review, input size bounds and unique run IDs; these
are now acceptance criteria above. Two diagnoses require qualification: the current
script already uses per-worktree git directories, and its subshell loses VERDICT
under `set -u` (so observed failure is not simply every error passing). Do not copy
the suggested CONCERNS-success branch or unverified stdin CLI syntax. Independent
re-review must check the revised plan before implementation dispatch.
