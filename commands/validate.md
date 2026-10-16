---
description: Validate the operating-model seed — manual binding, adapter drift, adoption state, checkpoint/evidence
---

Run from the consumer project root. Claude resolves `${CLAUDE_PLUGIN_ROOT}` in this
command’s content to the installed package; keep that path quoted. Do not change the
working directory to the package or copy its maintainer adapters into the project.
If the host has not resolved the path, load `operating-model-bootstrap` and locate its
scripts beside the discovered skill file before running anything.

Validate this repository's operating model:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/operating-model-bootstrap/scripts/validate_operating_model.py" --target .
```

- A `seed` profile may PASS with warnings about unresolved project facts — that supports discovery, architecture, ADRs, backlog formation, and R0/R1 work only.
- Before R2/R3 work, the profile must be `active` with applicable placeholders resolved; re-run with `--require-active` plus the task `--checkpoint` and `--evidence` paths.
- Report every finding verbatim. A failing validation blocks consequential work; do not route around it.
