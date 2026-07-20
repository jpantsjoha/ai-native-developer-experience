---
description: Bootstrap the day-one operating-model seed in the current repository (dry-run first, never overwrites)
---

Bootstrap this repository with the team operating model:

1. Ask the user for the project name if not given.
2. Run the preflight dry-run:

   ```bash
   python3 .agents/skills/operating-model-bootstrap/scripts/bootstrap_operating_model.py --dry-run --project-name "<project name>" .
   ```

3. If the dry-run is clean, run the real initializer (same command without `--dry-run`). It refuses to overwrite any different existing file — report any refusal to the user instead of forcing it.
4. Ground the resulting `docs/operating-model/PROJECT-OPERATING-PROFILE.md`: resolve the day-one minimum from tracked evidence. Never invent project facts; record unknowns with an owner and the trigger that resolves them.
5. Run `/join-the-team:validate` and report the result. Keep the profile at `seed`; only R0/R1 and design work may proceed until the team resolves `active` controls.
