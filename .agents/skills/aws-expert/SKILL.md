---
name: aws-expert
description: AWS expert guardrails — IAM least-privilege, data boundaries, cost controls, residency, and official-source validation. Trigger when designing or reviewing any AWS workload, especially agents, LLMs (Bedrock), or multi-account systems.
---

# AWS Expert

> **The Well-Architected pillars are the floor, not the ceiling. On AWS, IAM and cost are where agent workloads blow up first.**

This skill enforces the discipline that makes AWS workloads production-safe: identity, data boundaries, cost controls, and regional residency. It is not an AWS feature tour — it is a checklist of the things that cause incidents and compliance failures when skipped.

## When to use

- Designing any AWS infrastructure (new or modified)
- Before deploying agents or LLM workloads to AWS (Bedrock, AgentCore, Strands)
- When reviewing a CloudFormation/CDK/Terraform plan for an AWS workload
- When a system spans multiple accounts, touches regulated data, or crosses regions

## Procedure

1. **Identity and IAM** — verify least-privilege for every role and human principal:
   - No wildcard `Action: "*"` with `Resource: "*"` on any role. Managed policies scoped to the specific function.
   - Roles over IAM users; IRSA for EKS, instance profiles for EC2. No long-lived access keys in workloads.
   - SCPs at the OU level deny sensitive services by default; permission boundaries on delegated admin.
   - CloudTrail enabled on all management and data-plane events, shipped to a log-archive account.

2. **Data boundaries** — for every data store in the design:
   - What data classification does it hold (public / internal / confidential / regulated)?
   - S3 Block Public Access at account level; bucket policies explicit; KMS CMK where required.
   - Cross-account sharing only via explicit resource policy with external ID.
   - Tenant boundaries enforced at the data layer, not just the application layer.

3. **Data residency** — for each resource:
   - Region allow-list enforced by SCP, not convention.
   - For Bedrock / LLM calls: regional endpoints; check cross-region inference profiles where residency matters.

4. **Cost controls** — for every LLM, compute, or storage resource:
   - AWS Budgets alerts at 50%, 75%, 90%, 100%.
   - Bedrock invocation quotas/caps and rate limits set; unbounded agent loops are unbounded spend.
   - Autoscaling maximums set; Savings Plans / Spot evaluated where appropriate.

5. **Network and egress** — confirm:
   - PrivateLink / VPC endpoints used where public endpoints are avoidable.
   - Security groups default-deny with explicit allow rules; egress costed for cross-region and internet traffic.

6. **Observability** — confirm:
   - CloudWatch dashboards and alarms on error rate, latency, and cost thresholds.
   - X-Ray tracing on agent/LLM call paths.
   - CloudTrail as audit evidence — enabled before go-live, not after an incident.

7. **Run the Adversarial Gate** — common AWS failure modes: wildcard IAM, public S3, uncapped Bedrock spend, missing CloudTrail data events, global endpoints on residency-sensitive data.

## Official sources — validate before you assert

- Documentation: `docs.aws.amazon.com` · Well-Architected: `docs.aws.amazon.com/wellarchitected`
- Live docs via MCP (verify currency before pinning): the official `awslabs/mcp` monorepo includes the **AWS Documentation MCP Server** — fetch current docs instead of relying on memory.
- GitHub, foundations: `github.com/awslabs` · `github.com/aws-ia` · `github.com/aws-samples`
- GitHub, agent examples: `github.com/strands-agents/sdk-python` · Bedrock agent samples under `github.com/aws-samples`
- Rule: every service/API claim cites an official doc. Quotas, prices, and model IDs are dated facts — stale until re-verified against the source.

## Outputs

- AWS guardrail checklist (pass/fail per item)
- IAM matrix: principal | role | scope | justification
- Data classification and boundary map
- Budget alert confirmation
- Open findings for human review

## Guardrails

- **No wildcard actions on wildcard resources.** Ever.
- **Residency is a constraint, not a preference.** Enforce with SCPs, not conventions.
- **Budget alerts are not optional.** An unmonitored LLM workload will produce a surprise invoice.
- **CloudTrail is evidence.** Enable it before go-live, not after an incident.
