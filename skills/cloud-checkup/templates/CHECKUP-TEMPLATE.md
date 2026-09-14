# Cloud checkup · {{DATE}} · {{PROJECT}}

**Run:** {{STAMP}} · branch `{{BRANCH}}` @ `{{HEAD}}` · deployed image `{{IMAGE}}` · probes: `{{PROBES}}` · manifest: `{{MANIFEST_PATH}}` · window: {{LOG_DAYS}} days · mode: {{MODE}} (weekly schedule / on-demand skill / headless)

**Legend:** 🟢 LIVE = serving and healthy, no errors in the window · 🟡 WARNING = serving, but errors in the window, degraded, paused, stale or drifted · 🔴 RED = errors right now, down, or halted · ⚪ INCONCLUSIVE = could not be read from this seat (say what would be needed)

**Seat:** pinned account `{{ACCOUNT}}` · token identity {{TOKEN_IDENTITY}}. A permission error is INCONCLUSIVE, never zero.

## Feature status

| # | Feature | Capability / requirement | Check | Status | Evidence | Errors {{LOG_DAYS}}d / now |
|--:|---|---|---|:--:|---|---|
| 1 | Public routes | Every unauthenticated route in `edge_routes[]` returns its expected status | edge probe | | | |
| 2 | Sign-in | The sign-in entry and its auth-callback path both serve; no auth-path errors in the window | edge probe + log review | | | |
| 3 | Service serving | *(one row per entry in `services[]`)* latest ready revision at 100% traffic, health endpoint 200 | describe + curl | | | 5xx: |
| 4 | Security headers | Every header in `security_header_expectations` present and enforcing; CORS pinned to the expected origin | header probe | | | |
| 5 | Deploy currency | Commits on the branch ahead of the deployed image, and which of them are user-reachable | git + describe | | | |
| 6 | Error logs | `severity>=ERROR` count over the window and the last hour, with top messages | log review | | | |
| 7 | Scheduler | Jobs ENABLED rather than PAUSED; last attempt succeeded; target audience matches the service URL | scheduler list | | | |
| 8 | Alerting + monitoring | Alert policies > 0 and uptime checks > 0, and their infrastructure-as-code state applied rather than merely declared | monitoring list | | | |
| 9 | Secrets + IAM | Latest secret versions enabled and inside their age limit; no `allUsers` invoker on a private service; runtime service accounts not editor or owner | secrets + IAM | | | |
| 10 | Data store: connectivity | *(one row per entry in `data_stores[]`)* reachable, authenticated, correct database | store module | | | |
| 11 | Data store: stats | Size, document or row counts, index count and growth against the last checkup | store module | | | |
| 12 | Data store: freshness | Every collection in `freshness[]` inside its `max_age_hours` | store module | | | |
| 13 | Data store: tenant stamping | No documents missing `tenant_key` in tenant-scoped collections; writes stamp it and reads filter on it | store module | | | |
| 14 | Data store: backup | Backup policy in force and a recent snapshot; a restore demonstrated at least once | store module | | | |
| 15 | Cost | Month-to-date spend, or the instance-hours and request volume behind it, against the expected run rate | billing / metrics | | | |
| 16 | Local jobs | Every entry in `local_jobs[]` loaded, with last exit 0, and writing what it exists to write | launchctl / systemctl | | | |
<!-- markdownlint-disable MD055 MD056 -->
{{EXTRA_ROWS}}
<!-- markdownlint-enable MD055 MD056 -->

Rows 3 and 10 to 14 repeat per service and per data store. Keep the numbering contiguous
and the order fixed, so two reports diff cleanly.

## LIVE vs WORKING

| | Value |
|---|---|
| LIVE (deployed) | revision · image digest · deployed at |
| WORKING (branch) | HEAD · commits ahead of the deployed image · which of them a user would notice |

A gap here is not automatically a finding. Name the user-reachable commits, because those
are the ones whose absence a user can feel.

## Findings, by severity

| Sev | Feature | Finding | Evidence | Ticket |
|---|---|---|---|---|

Severity is HIGH when something a user depends on is already broken or will break on a
known date, MED when a control that would catch the next failure is missing, LOW when it is
hygiene. Evidence is the command or the value, never an assertion.

## Could not check

| Feature | Why | What would be needed |
|---|---|---|

Every INCONCLUSIVE row appears here with the specific grant, credential or console that
would close it.

## Changed since the last checkup

- (compare against the previous report in the report directory; name what moved, in both
  directions, and say "first run, baseline" when there is nothing to compare)

## Operator actions

| Action | Feature | Ticket |
|---|---|---|

Each action is one thing a person can do, in one sitting, with the command to do it.

OVERALL: {{HEALTHY|DEGRADED|UNHEALTHY}} — {{one sentence naming the binding constraint}}
