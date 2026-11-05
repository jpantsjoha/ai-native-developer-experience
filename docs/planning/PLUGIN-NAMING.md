# Plugin naming shortlist

Decision proposal only. The plugin and repository identifiers remain unchanged.

## Positioning

The plugin establishes shared delivery practices for human–AI teams: accepted intent,
scoped work, authority, verification and learning. DevDash makes the resulting state
and evidence visible. A new name should communicate that foundation, remain useful
without DevDash, and avoid implying guaranteed outcomes or autonomous authority.

| Name | Meaning and positioning | Trade-off |
| --- | --- | --- |
| DevAccord | Shared agreement on how humans and agents deliver; best match to the operating contract | Needs a descriptor to convey execution and verification |
| DevCharter | Purpose, responsibilities and acceptance established before work begins | Strong clarity; may sound more like documentation than action |
| DevTenet | Durable engineering principles carried into every project | Short and foundational; less immediately descriptive |
| DevMandate | Purpose-led work within explicit authority and scope | Strong intent; may feel overly hierarchical |
| DevBearing | Direction and alignment throughout delivery; a natural companion to DevDash | More abstract; explain what it does in the tagline |

Recommendation: **DevAccord — the delivery harness for human–AI teams.**
Pairing: **DevAccord establishes the working agreement. DevDash shows the evidence.**
Alternative when project intent is the emphasis: DevCharter.

These are creative candidates, not availability or ownership claims. Preliminary web
screening found direct adjacent uses for DevKeel and DevSteward, and software uses for
DevPact/DevGround, so they were excluded from the shortlist. Before selecting a name,
check exact/similar marketplace identifiers, package registries, repository names,
domains and relevant trademarks; search silence is not clearance. No domain purchase,
reservation or legal conclusion is part of this task.

## Rebrand work package, only after selection

1. Record chosen name, purpose, target audience and compatibility policy in an ADR.
2. Inventory root/vendor/marketplace manifests, commands, skill references, setup docs,
   README links, update paths, caches and adopting projects. Do not assume renaming the
   GitHub repository or slug is required for the public display-name change.
3. Prefer a staged display-name transition first. Verify host support for any proposed
   aliases; do not promise redirects or dual loading without actual tests. Preserve
   existing installations and explicit project authority.
4. Test fresh install, old installation upgrade, mixed-version discovery, no duplicated
   hooks/skills, repository links and rollback on supported hosts. Run `make check`,
   packaging conformance and fresh independent review of the exact release candidate.
5. Publish a migration guide and deprecation window only with an approved release;
   changing the name is neither a benchmark treatment nor evidence of improved delivery.

Rebranding does not rename DevDash, alter its architecture or change the plugin's
licence. No manifests, remote URLs, installed skills or marketplace listings change
on this planning branch.
