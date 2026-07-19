# Team Workflow — Skills, Dependencies, and the Accountability Chain

How the harness simulates a team's ways of working: intake to delivery, with the human
escalation loops that make accountability explicit. The diagram is the dependency map;
the sections below are the traceability and ownership model.

```mermaid
flowchart TD
    T["Ticket / epic / intent<br/>GH issue or written brief"] --> O[delivery-orchestrator]
    O --> SPEC[spec-first-delivery<br/>requirements + acceptance contract]
    O --> ARCH[the-architect<br/>ADR + cloud-vendor experts]
    ARCH --> GCP[gcp-expert]
    ARCH --> AWS[aws-expert]
    ARCH --> AZ[azure-expert]
    ARCH --> ALI[alibaba-expert]

    SPEC --> E{enough evidence<br/>to proceed?}
    ARCH --> E
    E -- "no" --> R["Team roster<br/>tag the accountable human:<br/>product owner · data owner · operator"]
    R -- "answer lands<br/>(ADR, requirement, fact)" --> E
    E -- "yes" --> L["Mutating lanes<br/>risk tier R0–R3 + scoped authority"]
    L --> DV[domain-validator]
    L --> AG[adversarial-gate]
    DV --> PR[pr-reviewer<br/>exact-candidate review]
    AG --> PR
    PR --> RR[release-readiness<br/>go / no-go + rollback]
    RR --> D["Authorised delivery<br/>+ observation window"]
    D --> SR[sitrep<br/>status, changelog, evidence reconciliation]

    CG[cost-guardrail] -. budgets .-> O
    CG -. spend .-> RR
```

## The traceability chain

Every deliverable answers five questions, in order, each with a named home:

| # | Question | Artefact | Home |
|---|---|---|---|
| 1 | What are we building and why? | Requirement / epic | GH issue (or brief) — ticket system of record |
| 2 | What does "correct" mean? | Acceptance contract | spec in repo (`spec-first-delivery`) |
| 3 | What did we decide? | ADR | `architecture/decisions/ADR-NNN-*.md` in repo (`the-architect`) |
| 4 | Who did what, and was it checked? | Checkpoint + evidence manifest | `docs/operating-model/` (exact-candidate bound) |
| 5 | Where is it now? | Status | `sitrep` output + changelog |

A requirement is not "matched" to an ADR by convention — the spec *references* the
ADRs it depends on, and the orchestrator will not route implementation while a
dependency ADR is unresolved. Broken reference = stop, not improvisation.

## The accountability model

Skills supply capability; **named humans supply authority**. The profile's team
roster records who owns what — product owner for requirements, data owner for data
classification and the ADRs that touch their data, integration owner for candidate
assembly, operator for R3 approvals.

The escalation rule is the value-delivery chain's spine:

- **Insufficient evidence is a stop, not a prompt to improvise.** When a ticket,
  spec, or ADR lacks the information a gate needs, the lane halts, the open question
  is recorded with an owner and a resolving trigger, and the roster role is tagged.
- **Silence never converts to permission.** An unanswered escalation blocks the lane;
  it does not lower the bar.
- **Delivery status is derived, not declared.** `sitrep` reads the artefacts above;
  it does not invent progress.

## Where decisions live (and MCP knowledge seams)

ADRs default to the repo — `architecture/decisions/` — so review, drift, and evidence
tooling applies uniformly. When the enterprise estate holds decisions or sources in
SharePoint, Confluence, or Google Drive, reach them through a **governed MCP seam**
(one server, one source, read-only, least-privilege — the `.agents/mcp_config.json`
pattern), never raw credentials, and mirror the decision of record into the repo ADR.
The repo stays the canonical decision log; external systems are sources, not truth.
