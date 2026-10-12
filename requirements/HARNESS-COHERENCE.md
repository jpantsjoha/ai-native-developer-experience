# Portable review and delivery coherence

**Owner:** harness maintainer. **Date:** 2026-10-12. **Risk:** R3 governance guidance.
**Authority:** operator requested consolidation of the agreed provider-neutral review
and adoption insights into PR #28, with independent review before merge.
**Vision:** [consistent evidence-bound delivery](../docs/VISION.md).

## Accepted scope and design

Keep the plugin independent of models, subscriptions and hosts. The shared contract
defines review independence, evidence and escalation; the host implements invocation;
the project profile selects permitted capabilities and budgets. Discovery grants no
authority. No model preferences or private meeting material enter the public package.

Reuse the prepared fail-closed review helper and its offline tests. Add an explicit
executable-adapter seam so other hosts can supply their own invocation without editing
the contract. Native fresh-context review remains valid without this optional helper.
No automatic provider fallback, new skills, installed-hook changes or release occurs.

Improve existing planning guidance: trace conversation-derived proposals to accepted
requirements; plan applicable operational handover prerequisites early; assign skill
maintenance ownership; measure optional guidance against a fixed quality floor.
Reuse existing records rather than create a parallel tracker. Record follow-up work
honestly; earlier audits and proposed gates are not all delivered by this slice.

## Acceptance

1. Review guidance allows a fresh independent context on any permitted host, without
   requiring a named model or provider. Model diversity is optional, not independence.
2. A bounded review loop preserves findings across candidate and reviewer changes.
   Exhaustion leads to diagnosis/replanning; an authorised alternate perspective cannot
   erase blockers, grant approval or reset history. No autonomous subscription switching.
3. The helper refuses missing lanes, failed processes, conditional or absent verdicts,
   empty analysis, truncated/oversized input, timeouts and changing candidates. Offline
   adapters prove complete input delivery and no fallback without provider calls.
4. Planning identifies human acceptance and applicable receiving-owner dependencies;
   templates distinguish owned skills from human accountability and preserve authority.
5. Run `make check` plus independent exact-candidate Council review. Update PR #28 and
   its description; merge only if applicable checks and review pass. Tags, releases,
   installation and adopter remediation require separate scope.

## Adversarial check and rollback

How would I break this? Accept a PASS hidden in an error response; review only a
truncated diff; change provider to lose findings; treat transcript repetition as human
approval; make a service-ready claim from a runbook's existence. Mechanical fixtures
reject transport/input defects; reviewer and accountable humans check meaning and
authority. Local receipts do not authenticate identity or prove remote enforcement.

Rollback uses a normal revert of this slice, retaining failed evidence and the existing
quality floor. No savings, operational adoption or provider compatibility beyond the
tested adapter protocol is claimed.
