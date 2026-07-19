---
name: gcp-expert
description: GCP expert guardrails — IAM least-privilege, data boundaries, cost controls, residency, and official-source validation. Trigger when designing or reviewing any Google Cloud workload, especially agents, LLMs (Vertex AI/Gemini), or multi-tenant systems.
---

# GCP Expert

> **Gemini Enterprise is the governed execution foundation — identity, tenancy, and compliance are the design constraints, not context window size.**

This skill enforces the discipline that makes GCP workloads production-safe: identity, data boundaries, cost controls, and regional residency. It is not a GCP feature tour — it is a checklist of the things that cause incidents and compliance failures when skipped.

## When to use

- Designing any GCP infrastructure (new or modified)
- Before deploying agents or LLM workloads to GCP
- When reviewing a Terraform plan or architecture diagram for a GCP workload
- When a system touches multiple tenants, regulated data, or crosses regional boundaries

## Procedure

1. **Identity and IAM** — verify least-privilege for every service account and human role:
   - Service accounts have only the roles required for their specific function. No `roles/editor` or `roles/owner` on service accounts.
   - Workload Identity Federation preferred over service account keys for GKE / Cloud Run workloads.
   - VPC Service Controls applied to sensitive APIs (Vertex AI, BigQuery, Cloud Storage with regulated data).
   - Audit logging enabled on all IAM changes and data-plane operations.

2. **Data boundaries** — for every data store in the design:
   - What data classification does it hold (public / internal / confidential / regulated)?
   - Is encryption at rest enabled with a customer-managed key (CMEK) where required?
   - Are tenant boundaries enforced at the data layer, not just the application layer?
   - Does data cross a project or organisation boundary? If yes, is there an explicit data-sharing agreement?

3. **Data residency** — for each resource:
   - Is the region constrained to the required geography (e.g. `europe-west2` for UK data)?
   - Are Organisation Policies in place to prevent accidental multi-region or global resource creation?
   - For LLM / Vertex AI calls: is the endpoint regional, not global, where residency matters?

4. **Cost controls** — for every LLM, compute, or storage resource:
   - Is there a budget alert configured (at 50%, 75%, 90%, 100%)?
   - Are autoscaling upper bounds set? Unbounded autoscaling is unbounded spend.
   - Are Vertex AI / LLM call volumes capped or rate-limited?
   - Are committed-use discounts or Spot/Preemptible instances evaluated where appropriate?

5. **Network and egress** — confirm:
   - Private Service Connect or VPC peering used where public endpoints are avoidable.
   - Egress costs estimated for cross-region or internet-bound traffic.
   - Firewall rules follow default-deny with explicit allow rules.

6. **Observability** — confirm:
   - Cloud Monitoring dashboards exist for the workload.
   - Alerting policies fire on error rate, latency, and cost thresholds.
   - Log sinks route to a central logging project for retention and audit.

7. **Run the Adversarial Gate** — common GCP failure modes: overly-permissive service accounts, no VPC-SC on Vertex AI, uncapped autoscaling, global endpoints used for residency-sensitive data, missing budget alerts.

## Official sources — validate before you assert

- Documentation: `cloud.google.com/docs` · Architecture Center (incl. the Well-Architected Framework): `cloud.google.com/architecture`
- Live docs via MCP (verify currency before pinning): Google Cloud offers managed MCP servers for a growing service list (BigQuery, Spanner, and more) — fetch current docs instead of relying on memory.
- GitHub, foundations: `github.com/GoogleCloudPlatform/cloud-foundation-fabric` · `github.com/terraform-google-modules`
- GitHub, agent examples: `github.com/google/adk-python` · `github.com/google/adk-samples` · `github.com/GoogleCloudPlatform/generative-ai`
- Rule: every service/API claim cites an official doc. Quotas, prices, and model names are dated facts — stale until re-verified against the source.

## Outputs

- GCP guardrail checklist (signed with pass/fail per item)
- IAM role matrix: principal | role | scope | justification
- Data classification and boundary map
- Budget alert confirmation
- Open findings for human review

## Guardrails

- **No `roles/editor` or `roles/owner` on service accounts.** Ever.
- **Residency is a constraint, not a preference.** If the data has a residency requirement, enforce it with Organisation Policy, not convention.
- **Budget alerts are not optional.** An unmonitored LLM workload will produce a surprise invoice.
- **Audit logs are evidence.** Enable them before go-live, not after an incident.
