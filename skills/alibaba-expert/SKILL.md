---
name: alibaba-expert
description: Alibaba Cloud expert guardrails — RAM least-privilege, data boundaries, residency (mainland/international split), cost, and official-source validation. Trigger when designing or reviewing any Alibaba Cloud workload, especially agents or LLMs (Model Studio/Bailian, Qwen, AgentScope).
---

# Alibaba Cloud Expert

> **Same discipline, different control plane: RAM and ActionTrail are the guardrails; Model Studio and AgentScope are the agent surface. The mainland/international split is a design input, not an afterthought.**

This skill enforces the discipline that makes Alibaba Cloud workloads production-safe: identity, data boundaries, cost controls, and residency. It is not a feature tour — it is a checklist of the things that cause incidents and compliance failures when skipped.

## When to use

- Designing any Alibaba Cloud infrastructure (new or modified)
- Before deploying agents or LLM workloads (Model Studio / Bailian, DashScope, PAI, AgentScope)
- When reviewing a Terraform plan or architecture for an Alibaba Cloud workload
- When a system touches regulated data or spans mainland-China and international regions

## Procedure

1. **Identity and RAM** — verify least-privilege for every principal:
   - RAM roles with STS temporary credentials over long-lived AccessKey pairs. No AccessKeys in code or config.
   - Policies scoped to the specific function; resource groups used to bound blast radius.
   - ActionTrail enabled on all account activity and shipped to a central audit store.

2. **Data boundaries** — for every data store:
   - Classification recorded (public / internal / confidential / regulated — note PIPL and Data Security Law categories where in scope).
   - OSS bucket policies explicit; public access blocked; KMS CMK where required.
   - Cross-account sharing explicit and documented.

3. **Data residency** — for each resource:
   - **Mainland-China vs international accounts are separate control planes** — decide which side the workload and its data live on; regulated mainland data stays in mainland regions.
   - For Model Studio / DashScope calls: confirm the endpoint region matches the residency requirement.

4. **Cost controls** — for every LLM, compute, or storage resource:
   - Budget alerts configured (User Center budgets) at staged thresholds.
   - DashScope token quotas and rate limits set; unbounded agent loops are unbounded spend.
   - Auto-scaling maximums bounded.

5. **Network and egress** — confirm:
   - PrivateLink / PrivateZone used where public endpoints are avoidable.
   - Security groups default-deny; egress costed for cross-border traffic (cross-border egress is materially expensive).

6. **Observability** — confirm:
   - CloudMonitor dashboards and alerts on error rate, latency, and cost.
   - SLS (Log Service) retention configured for audit — evidence before go-live.

7. **Run the Adversarial Gate** — common Alibaba Cloud failure modes: long-lived AccessKeys, public OSS buckets, mainland/international residency confusion, uncapped DashScope spend, missing ActionTrail.

## Official sources — validate before you assert

- Documentation: `alibabacloud.com/help` (international) · `help.aliyun.com` (mainland)
- Live docs via MCP: official MCP coverage is thinner here than the other vendors — verify what exists before pinning; spring-ai-alibaba ships MCP integrations (`github.com/alibaba/spring-ai-alibaba`).
- GitHub, foundations: `github.com/aliyun` (incl. `terraform-provider-alicloud` and landing-zone modules)
- GitHub, agent examples: `github.com/modelscope/agentscope` · `github.com/alibaba/spring-ai-alibaba` · `github.com/QwenLM`
- Rule: every service/API claim cites an official doc. Service names, quotas, and model IDs are dated facts — stale until re-verified against the source.

## Outputs

- Alibaba Cloud guardrail checklist (pass/fail per item)
- RAM matrix: principal | role | scope | justification
- Data classification and boundary map (incl. residency side)
- Budget alert confirmation
- Open findings for human review

## Guardrails

- **No long-lived AccessKeys in workloads.** STS or nothing.
- **Residency is a constraint, not a preference.** The mainland/international split is decided in design, recorded in the ADR.
- **Budget alerts are not optional.** An unmonitored LLM workload will produce a surprise invoice.
- **ActionTrail is evidence.** Enable it before go-live, not after an incident.
