# cloud-checkup

A read-only weekly SRE checkup for a GCP project. Deterministic probes of the edge, Cloud
Run, error logs, scheduler, alerting, secrets and IAM, the data stores and the machine's own
scheduled jobs, audited into one fixed status table with evidence, findings, what could not
be checked, and a single `OVERALL:` line sent as one notification. It never deploys,
mutates or restarts anything.

## Quick start

```bash
SKILL=<path-to-this-skill-directory>   # e.g. skills/cloud-checkup in the plugin checkout
cp "$SKILL/manifest.example.yaml" .cloud-checkup.yaml   # then edit it
CC_MANIFEST=.cloud-checkup.yaml "$SKILL/scripts/cloud_checkup.sh"
```

Add `CC_SKIP_AI=1 CC_NO_NOTIFY=1` for probes only. Schedule it from
`templates/launchd.plist.tmpl` (macOS) or `templates/cron.example` (elsewhere).

## What a project must supply

A manifest, a `gcloud` identity with read access on the project, `gcloud` / `curl` /
`python3` on PATH, an env var holding the notification webhook, and one connection env var
per data store. `claude` on PATH is optional: without it the report is the probes plus
`OVERALL: INCONCLUSIVE`.
