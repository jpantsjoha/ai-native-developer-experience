---
name: azure-expert
description: Azure expert guardrails — Entra ID least-privilege, policy-first governance, data boundaries, cost, residency, and official-source validation. Trigger when designing or reviewing any Azure workload, especially agents, LLMs (Foundry/OpenAI), or landing-zone systems.
---

# Azure Expert

> **Azure is policy-first: Entra ID and Azure Policy are the guardrails; the Foundry is the agent surface. If it is not enforced by policy, it is a wish.**

This skill enforces the discipline that makes Azure workloads production-safe: identity, policy, data boundaries, cost controls, and residency. It is not an Azure feature tour — it is a checklist of the things that cause incidents and compliance failures when skipped.

## When to use

- Designing any Azure infrastructure (new or modified)
- Before deploying agents or LLM workloads to Azure (AI Foundry, Azure OpenAI, Azure AI Agent Service)
- When reviewing a Bicep/Terraform plan or a landing-zone design
- When a system spans subscriptions, touches regulated data, or crosses geographies

## Procedure

1. **Identity and access** — verify least-privilege for every identity:
   - Managed identities over service principals with secrets; no client secrets in code or config.
   - Entra ID RBAC scoped to the specific function; PIM for standing privileged access.
   - Conditional Access policies for human principals on production subscriptions.

2. **Policy and landing zones** — confirm governance is mechanical:
   - Azure Policy assignments enforce allowed locations, required encryption, and denied public endpoints.
   - Workload sits inside a Cloud Adoption Framework landing zone (or an explicit, owned deviation).

3. **Data boundaries** — for every data store:
   - Classification recorded (Purview where in scope); CMK where required.
   - Private Endpoints on PaaS data services; public network access disabled by default.
   - Cross-tenant or cross-subscription sharing explicit and documented.

4. **Data residency** — for each resource:
   - Allowed-locations policy constrains deployment geography (e.g. EU Data Boundary where required).
   - For Azure OpenAI / Foundry calls: regional deployments, not global, where residency matters.

5. **Cost controls** — for every LLM, compute, or storage resource:
   - Cost Management budgets with alerts at 50%, 75%, 90%, 100%.
   - Foundry model quotas and rate limits set; autoscale maximums bounded.

6. **Network and egress** — confirm:
   - Private Link over public endpoints; NSGs default-deny.
   - Egress costed for cross-region and internet-bound traffic.

7. **Observability** — confirm:
   - Azure Monitor / Log Analytics dashboards and alerts on error rate, latency, and cost.
   - Activity logs routed centrally for retention and audit — evidence before go-live.

8. **Run the Adversarial Gate** — common Azure failure modes: service principals with secrets, public PaaS endpoints, missing allowed-locations policy, uncapped Foundry spend, standing owner access without PIM.

## Official sources — validate before you assert

- Documentation: `learn.microsoft.com/azure` · Well-Architected: `learn.microsoft.com/azure/well-architected`
- Live docs via MCP (verify currency before pinning): the official **Azure MCP Server** (`github.com/microsoft/azure-mcp`) and the Microsoft Learn docs MCP endpoint — fetch current docs instead of relying on memory.
- GitHub, foundations: `github.com/Azure/Enterprise-Scale` (CAF landing zones) · `github.com/Azure/bicep` · `github.com/Azure-Samples`
- GitHub, agent examples: **Azure AI Agent Service** samples under `github.com/Azure-Samples` · AutoGen (`github.com/microsoft/autogen`) · Semantic Kernel (`github.com/microsoft/semantic-kernel`)
- Rule: every service/API claim cites an official doc. Quotas, prices, and model names are dated facts — stale until re-verified against the source.

## Outputs

- Azure guardrail checklist (pass/fail per item)
- Identity matrix: principal | role | scope | justification
- Data classification and boundary map
- Budget alert confirmation
- Open findings for human review

## Guardrails

- **No client secrets in code or config.** Managed identity or nothing.
- **Policy, not promises.** If a guardrail is not an Azure Policy assignment, it does not exist.
- **Residency is a constraint, not a preference.** Enforce with allowed-locations policy.
- **Budget alerts are not optional.** An unmonitored LLM workload will produce a surprise invoice.
