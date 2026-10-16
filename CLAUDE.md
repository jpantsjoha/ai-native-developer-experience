# Shared agent contract

AGENTS.md, CLAUDE.md and GEMINI.md carry the same portable instructions.

Before taking delivery work, read `docs/STATUS.md`, then the relevant slice of
`docs/ROADMAP.md`; inspect open issues, PRs and worktrees and coordinate with the
active owner before starting a competing lane.

Ground changed intent in `docs/VISION.md` and the relevant versioned requirement.
Use `skills/delivery-orchestrator/SKILL.md` to maintain the golden thread through
GitHub Issues, acceptance checks, review and release. Load only the role, skill and
artifact sections needed for the current task; do not preload the whole library.

For repository changes read `docs/REPOSITORY-CONTRACT.md`. Run `make check` and
fresh, read-only independent adversarial review of the exact candidate before merge.
Before delegation read `docs/MODEL-ROUTING.md`. Explicit user authority and project
controls govern external actions; skill installation grants no authority.

Reconcile affected requirements, decisions, status, roadmap and changelog as work
changes. After an authorised merge, verify integration and safely clean up only
this lane's merged branches and clean worktrees. Never overwrite another lane.

Canonical skills live in `skills/`; `.agents/skills/` is a discovery alias.
