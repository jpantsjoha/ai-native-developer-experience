# Delivery roadmap

Public milestones for DevEx Charter, in order. Each milestone is published here only once
it is accepted; detailed plans and experiments are maintained outside this repository.

| Order | Milestone | Exit evidence | State |
| --- | --- | --- | --- |
| 1 | DevEx Charter rename (#34) | Aligned manifests, migration guide, local checks and independent review | Released in v0.5.0 |
| 2 | Verified migration to DevEx Charter | Fresh install, upgrade, duplicate-discovery and rollback results on each supported host; directory listings updated | Open |
| 3 | Demonstrated delivery value | Independently accepted deliverables compared with and without the harness, with uncertainty and regressions reported | Open |
| 4 | Delivery planning validator ([DPS-001](../requirements/DELIVERY-PLANNING-SYSTEM.md)) | Offline structural gate shipped (`make planning`); remaining DPS scope accepted | In progress |
| 5 | Adoption modes and the human-in-the-loop queue ([AMH-001](../requirements/ADOPTION-MODES-HITL.md), [ADR-006](../architecture/decisions/ADR-006-adoption-modes-and-hitl-queue.md)) | Solo and team modes in the operating profile; a local, uncommitted queue at `HITL/OPERATOR/`; escalation, skill maintainer and outside-context rules; validated by structural checks, worked behavioural scenarios and independent review. Value outcomes (a declared success metric) need their own specification first | In progress. Built: delivery asks enter through `delivery-orchestrator` (FR-6), released in [v0.7.0](https://github.com/jpantsjoha/ai-native-developer-experience/releases/tag/v0.7.0). Not built: the adoption modes and the queue (FR-1 to FR-5, FR-7, FR-8) |

Earlier milestones are recorded in the [changelog](../CHANGELOG.md).
