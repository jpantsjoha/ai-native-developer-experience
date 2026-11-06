# Release contract and structural preflight

Use the existing project profile and approved release ADR as the authority record.
The following check detects structural contradictions and missing local evidence; it
is not an approval service or a replacement for independent review.

## Declare the mode

Use exactly one of each field in `docs/operating-model/PROJECT-OPERATING-PROFILE.md`:

```markdown
**Release mode:** tag-ci
**Build trigger:** tag
**Build executor:** ci
**Promotion trigger:** separate-approval
**Release owner:** release owner
**Release decision:** architecture/decisions/ADR-release.md
```

| Field | Accepted values / meaning |
| --- | --- |
| Release mode | `tag-ci` or `approved-alternative`; explicit approval is needed for either |
| Build trigger | `tag`, `manual`, `pipeline` |
| Build executor | `ci`, `controlled-runner`; the ADR identifies the actual executor |
| Promotion trigger | `separate-approval`, `tag`; tag mode still requires a protected approval stage |
| Release owner | Named accountable owner from the authority record |
| Release decision | Nonempty project-relative ADR file; human checks approval and adequacy |

`tag-ci` requires `tag` and `ci`. An alternative may use, for example, `manual` and
`controlled-runner`, but carries the same evidence obligations. Tag promotion requires
a tag build; all other combinations must use separate promotion approval. These are
supported structural combinations, not proof that the effective workflow obeys them.
The operator must reconcile any contradiction between ADR, profile and live pipeline.

Existing profiles remain valid for ordinary operating-model checks. Before adopting
release preflight, resolve these fields, approve the mode, prepare retained evidence,
and wire the command into the project's release gate. The plugin does not alter
adopters, remote rules or installed hooks automatically.

## Prepare evidence after building, before promotion

Authorise the build/tag separately. For tag-triggered pipelines, place preflight and
the release-owner approval boundary after the build and before publication/deployment.
Retain one JSON record alongside the existing release evidence; no new evidence store
is needed. Copy the profile's values exactly, using the JSON keys shown here:

```json
{
  "schema_version": 1,
  "policy": {
    "mode": "tag-ci",
    "build_trigger": "tag",
    "build_executor": "ci",
    "promotion_trigger": "separate-approval",
    "release_owner": "release owner",
    "release_decision": "architecture/decisions/ADR-release.md"
  },
  "decision_sha256": "<64 lowercase hexadecimal characters>",
  "candidate": "<full commit SHA or tree digest>",
  "artifact_sha256": "<64 lowercase hexadecimal characters>",
  "review_candidate": "<same candidate>",
  "review_verdict": "PASS",
  "receipts": {
    "approval": "release/owner-approval.md",
    "build": "release/build-provenance.json",
    "validation": "release/validation.json",
    "review": "release/independent-review.md",
    "rollback": "release/rollback-proof.md",
    "observation_plan": "release/observation-plan.md"
  }
}
```

Replace placeholders with measured identities. Obtain `decision_sha256` by hashing
the exact ADR bytes, e.g. `shasum -a 256 architecture/decisions/ADR-release.md`.
The expected candidate must come from the release owner or trusted pipeline, not from
copying an unverified record's own value. Approved alternatives change the policy
values, not the required receipt set. Unknown/duplicate JSON keys are rejected.

```bash
python3 .agents/skills/operating-model-bootstrap/scripts/validate_operating_model.py \
  --target . --release-evidence release/preflight.json --candidate "$RELEASE_CANDIDATE"
```

The profile must be active. Exit 0 establishes only matched declarations, a current
ADR digest, matching declared candidate/review identities, a well-formed artifact
digest, a literal unconditional PASS and nonempty in-project files. Exit 1 means a
validation failure; exit 2 means invalid CLI usage. Files outside the project,
including symlink escapes, fail. Export external receipts into retained local files;
the validator makes no network requests and executes no referenced command.

## Human and runtime gates remain

A self-written receipt can pass these checks. No file's presence authenticates its
contents, reviewer, approval, artifact digest or test execution. The release owner
must independently check these, verify zero unresolved conditions, confirm rollback
was exercised and obtain the appropriate go/no-go decision. The `observation_plan`
is a pre-promotion plan, not proof that delivery was observed. After authorised
promotion, verify deployed artifact identity and retain the observation result before
marking delivery complete. Green structure alone never authorises a tag, release,
deployment or exemption. No alternative lowers a project's existing quality floor.
