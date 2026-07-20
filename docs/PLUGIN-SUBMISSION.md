# Plugin Submission Capability

## Intent

Provide one portable `plugin-submission` skill that governs how `join-the-team` and its
adopters are listed in plugin directories, skill registries, marketplaces, and curated
repositories.

## Scope and constraints

- The canonical skill lives under `.agents/skills/` and is discovered through the
  existing Claude, Codex, Kimi, and Antigravity adapters.
- It discovers current destination policy before action and distinguishes plugin,
  repository, and standalone-skill submissions.
- Every external send needs an immediately preceding human confirmation of its exact
  destination and public payload.
- Policies prohibiting AI-assisted submissions or requiring human authorship are hard
  stops. Credentials and personal contact details are never inferred.

## Acceptance criteria

- The skill produces a destination matrix with evidence, eligibility, payload, and
  receipt/rollback information.
- It prevents a whole plugin from being submitted to a single-skill-only registry.
- It treats public licence metadata mismatches as blockers until resolved.
- The plugin packaging validator accepts the canonical skill and all published skill
  counts name it correctly.

## Failure and rollback

The likely failure is an inaccurate or unauthorised public listing. The controls are
primary-source policy review, validation before staging, and final confirmation. A
repository contribution can be closed; a directory listing follows that directory's
removal path. The capability has no runtime service, data store, or usage cost.
