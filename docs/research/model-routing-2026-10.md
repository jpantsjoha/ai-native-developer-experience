# Model-routing benchmark: lower estimated cost did not preserve quality

Study date: 13 October 2026; public summary prepared 14 October 2026. Operator-generated
research, independently reviewed. Source: private JevModelRouter research checkpoint
`4d9fda0`, crossrepo-v1. This summary omits private repository names, code, prompts, paths,
issue identifiers and raw logs. Full source is not publicly reproducible from this note.

Three real historical single-file patches across Python and JavaScript were replayed:
A/report retention, B/file-access guards, C/CI evidence caching. Each had pinned original
and fixed versions plus historical regressions; original code failed and historical fixes
passed. Two requested Codex configurations (Luna and Sol), medium effort, two equal-fact
prompt presentations and two repetitions yielded **24 generated patches**. Six actual
JEV classifications preceded generation. Tests were withheld from generation.

| Historical case | Luna accepted | Sol accepted | Declared checks per patch |
|---|---:|---:|---:|
| A: Python report retention | 4/4 | 4/4 | 11 |
| B: Python file-access guards | 2/4 | 4/4 | 38 |
| C: JavaScript CI evidence caching | 3/4 | 4/4 | 26 |

Across 24 artifacts, 595/600 checks passed, but only **21/24 complete artifacts** passed.
Two Luna patches removed existing filename protections; another cached transient empty
job evidence. A high check-pass percentage must not conceal defective artifacts.

| Paired selection policy | Accepted / assigned | Estimated cost | Versus fixed Sol |
|---|---:|---:|---|
| Fixed Sol medium | 12/12 | $0.47537120 | Reference |
| Fixed Luna medium | 9/12 | $0.03608148 | Lower cost, quality gate failed |
| Experimental rules | 11/12 | $0.12775958 | 73.12% lower cost, quality gate failed |
| JEV-assisted selection | 11/12 | $0.12827450 | Same decisions as rules; 0.403% more cost |

These policies select from the same paired captures; they are not four independently
executed delivery arms. JEV fees are charged per selection: six measured classification
fees are charged twice for the 12-assignment comparison. All 24 workers cost $0.51145268;
six actual classifications cost $0.00025746, totalling $0.51171014. No retry occurred.
Prices are recorded API-equivalent estimates, not observed subscription bills. Requested
worker identities/efforts were recorded; resolved server identities were not attested.

The rules preserved a security floor for case B and selected Luna for A and C. JEV matched
all six case/presentation decisions. The cheaper routing therefore failed the preregistered
unchanged-quality gate. **This is not a demonstrated quality-preserving saving or evidence
that the harness causes better delivery.** Worker tokens fell only about 1.96% for rules
versus fixed Sol; model price and caching account for most of the estimated cost difference.
Uncached sensitivity remained cheaper ($0.24937750 rules versus $0.760888 fixed Sol), but
cannot remedy the additional quality failure.

Phoenix replay reproduced 21/24 acceptance; live evidence verification passed integrity
while the all-artifacts-accepted claim failed. Fresh independent review reconciled all
usage/selection arithmetic, replayed all 16 B/C candidates and inspected A receipts/diffs.
This is operator evidence, not external audit or production certification. In-process
graders are not malicious-forgery-proof. The Python file-guard suite used a disclosed
stdlib adaptation of historical tests.

Both presentations contained the same detailed facts and source context. Flat accepted
10/12 and checklist 11/12: too little evidence for a planning/formatting effect. One task
per repository, with repeated generations, cannot establish framework-wide or project
maturity effects. Parent planning, review, repair and full-delivery latency were not costed.
Medium is the only effort evaluated here; higher Luna effort remains untested.

The transferable foundation is disciplined scope, executable acceptance, complete failure
accounting, conservative floors and reversible adoption. See the [guarded pilot](../MODEL-ROUTING.md).
