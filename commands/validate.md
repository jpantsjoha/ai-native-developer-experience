---
description: Validate the operating-model seed — manual binding, adapter drift, adoption state, checkpoint/evidence
---

Validate this repository's operating model:

```bash
python3 .agents/skills/operating-model-bootstrap/scripts/validate_operating_model.py --target .
```

- A `seed` profile may PASS with warnings about unresolved project facts — that supports discovery, architecture, ADRs, backlog formation, and R0/R1 work only.
- Before R2/R3 work, the profile must be `active` with applicable placeholders resolved; re-run with `--require-active` plus the task `--checkpoint` and `--evidence` paths.
- Report every finding verbatim. A failing validation blocks consequential work; do not route around it.
