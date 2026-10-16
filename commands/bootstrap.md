---
description: Bootstrap the operating model and minimal delivery-planning seed (dry-run first, never overwrites)
---

Run from the consumer project root. Claude resolves `${CLAUDE_PLUGIN_ROOT}` in this
command’s content to the installed package; keep that path quoted. Do not change the
working directory to the package or copy its maintainer adapters into the project.
If the host has not resolved the path, load `operating-model-bootstrap` and locate its
scripts beside the discovered skill file before running anything.

Bootstrap this repository with the team operating model:

1. Ask the user for the project name if not given.
2. Run the preflight dry-run:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/operating-model-bootstrap/scripts/bootstrap_operating_model.py" --dry-run --project-name "<project name>" .
   ```

3. If the dry-run is clean, run the real initializer (same command without `--dry-run`).
   It preserves existing vision, workflow, roadmap, status, and changelog files while
   seeding missing ones. A different operating contract or surface adapter is a blocking
   conflict—report it instead of forcing replacement.
4. Ground the resulting `docs/operating-model/PROJECT-OPERATING-PROFILE.md`,
   `docs/VISION.md`, and `docs/operating-model/DELIVERY-WORKFLOW.md` from tracked evidence.
   Keep the initial roadmap and status free of invented work or progress. Record unknowns
   with an owner and the trigger that resolves them.
5. Run `/join-the-team:validate` and report the result. Keep the profile at `seed`; only
   R0/R1 and design work may proceed until the team resolves `active` controls.
