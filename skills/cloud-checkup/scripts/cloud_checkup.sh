#!/bin/bash
# cloud_checkup.sh — read-only SRE checkup for one GCP project.
#
# Three layers, so the routine keeps its value when the later ones are unavailable:
#   1. Deterministic probes (curl, gcloud, launchctl/systemctl) -> the probes file.
#   2. Headless read-only inspection (claude -p) fills the report template from the probes
#      plus the data stores. Skipped with CC_SKIP_AI=1, which is what the in-session skill
#      does because the session itself is layer 2.
#   3. One notification line carrying the OVERALL verdict and the report path.
#
# Everything project-specific comes from the manifest (see manifest.example.yaml).
#
# Read-only by construction. It never deploys, never mutates cloud state, never restarts
# or unpauses anything, and never runs `gcloud config set`.
#
# Env:
#   CC_MANIFEST   path to the manifest        (default ./.cloud-checkup.yaml)
#   CC_SKIP_AI=1  probes only
#   CC_NO_NOTIFY=1 suppress layer 3
#   CC_MODEL      model for layer 2           (default claude-opus-5)
#   CC_OUT        report path                 (default <report_dir>/<date>-checkup.md)
#   CC_PROBES     probes path                 (default <state>/probes-<project>-<date>.md)
#   CC_STATE_DIR  logs and probes             (default ~/.local/state/cloud-checkup)
#
# `set -e` is deliberately absent: one denied probe must not abort the sweep. Every probe
# captures its own stderr and reports INCONCLUSIVE rather than silence.
set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="${CC_MANIFEST:-.cloud-checkup.yaml}"
if [ ! -f "$MANIFEST" ]; then
  echo "[cloud-checkup] no manifest at ${MANIFEST}" >&2
  echo "[cloud-checkup] copy ${SKILL_DIR}/manifest.example.yaml and set CC_MANIFEST" >&2
  exit 2
fi
MANIFEST="$(cd "$(dirname "$MANIFEST")" && pwd)/$(basename "$MANIFEST")"

# ── manifest -> shell ──────────────────────────────────────────────────────
# yq when present, PyYAML next, a restricted built-in parser last. The built-in parser
# handles top-level scalars, top-level string lists and one nested level of scalars, which
# is everything this script reads. Layer 2 reads the manifest file itself.
_manifest_env() {
python3 - "$1" <<'PY'
import json, shlex, shutil, subprocess, sys

path = sys.argv[1]
data = None

if shutil.which("yq"):
    for args in (["yq", "-o=json", ".", path], ["yq", ".", path]):
        try:
            out = subprocess.run(args, capture_output=True, text=True, timeout=20)
            if out.returncode == 0 and out.stdout.strip():
                data = json.loads(out.stdout)
                break
        except Exception:
            data = None

if data is None:
    try:
        import yaml
        with open(path) as handle:
            data = yaml.safe_load(handle)
    except Exception:
        data = None


def _scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def mini_parse(text):
    """Restricted YAML: top-level scalars, top-level string lists, one nested map level.

    A list of mappings keeps its LENGTH (each item becomes None) but not its content, so
    a count stays honest while the probe layer stays simple. Anything nested deeper is
    ignored: the inspection layer reads the manifest file itself.
    """
    root, key, list_indent = {}, None, -1
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        line, stripped = raw.rstrip(), raw.strip()
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            key, list_indent = None, -1
            if stripped.endswith(":"):
                key = stripped[:-1].strip()
                root[key] = None
            elif ":" in stripped:
                name, value = stripped.split(":", 1)
                root[name.strip()] = _scalar(value)
        elif key:
            if stripped.startswith("- "):
                if not isinstance(root.get(key), list):
                    root[key], list_indent = [], indent
                if indent != list_indent:
                    continue  # a list nested inside a mapping item
                item = _scalar(stripped[2:])
                mapping = ":" in item and not item.startswith(("http", "/"))
                root[key].append(None if mapping else item)
            elif ":" in stripped and not isinstance(root.get(key), list):
                name, value = stripped.split(":", 1)
                value = _scalar(value)
                if not isinstance(root.get(key), dict):
                    root[key] = {}
                if value:
                    root[key][name.strip()] = value
    return root


if data is None:
    with open(path) as handle:
        data = mini_parse(handle.read())
if not isinstance(data, dict):
    data = {}


def emit(name, value):
    print("%s=%s" % (name, shlex.quote("" if value is None else str(value))))


def emit_list(name, value):
    items = value if isinstance(value, list) else []
    print("%s=(%s)" % (name, " ".join(shlex.quote(str(i)) for i in items if i)))


def nested(section, field):
    block = data.get(section)
    return block.get(field, "") if isinstance(block, dict) else ""


for key, out in (
    ("project", "CC_PROJECT"),
    ("region", "CC_REGION"),
    ("account", "CC_ACCOUNT"),
    ("public_url", "CC_PUBLIC_URL"),
    ("log_review_days", "CC_LOG_DAYS"),
    ("report_dir", "CC_REPORT_DIR"),
    ("repo", "CC_REPO"),
):
    emit(out, data.get(key, ""))

emit_list("CC_SERVICES", data.get("services"))
emit_list("CC_ROUTES", data.get("edge_routes"))
emit_list("CC_JOBS", data.get("local_jobs"))
emit("CC_WEBHOOK_ENV", nested("slack", "webhook_env"))
emit("CC_NOTIFY_CMD", nested("slack", "command"))
emit("CC_SCHED_WEEKDAY", nested("schedule", "weekday"))
emit("CC_SCHED_HOUR", nested("schedule", "hour"))
stores = data.get("data_stores")
emit("CC_STORE_COUNT", len(stores) if isinstance(stores, list) else 0)
PY
}

eval "$(_manifest_env "$MANIFEST")" || { echo "[cloud-checkup] manifest parse failed" >&2; exit 2; }
[ -n "${CC_PROJECT:-}" ] || { echo "[cloud-checkup] manifest has no 'project'" >&2; exit 2; }

PROJECT="$CC_PROJECT"
REGION="${CC_REGION:-}"
ACCOUNT="${CC_ACCOUNT:-}"
PUBLIC_URL="${CC_PUBLIC_URL:-}"
LOG_DAYS="${CC_LOG_DAYS:-7}"
REPO="${CC_REPO:-}"
SERVICES=("${CC_SERVICES[@]:-}")
ROUTES=("${CC_ROUTES[@]:-}")
JOBS=("${CC_JOBS[@]:-}")

STATE_DIR="${CC_STATE_DIR:-$HOME/.local/state/cloud-checkup}"   # never /tmp: macOS purges it
DATE="$(date +%F)"
STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
REPORT_DIR="${CC_REPORT_DIR:-audits}"
OUT="${CC_OUT:-${REPORT_DIR}/${DATE}-checkup.md}"
PROBES="${CC_PROBES:-${STATE_DIR}/probes-${PROJECT}-${DATE}.md}"
AI_LOG="${STATE_DIR}/ai-${PROJECT}-${DATE}.log"
WORK="${STATE_DIR}/work-${PROJECT}-${DATE}"
MODEL="${CC_MODEL:-claude-opus-5}"
mkdir -p "$STATE_DIR" "$WORK" "$(dirname "$OUT")" 2>/dev/null

echo "[cloud-checkup] ${STAMP} start — project=${PROJECT} region=${REGION} out=${OUT}"

# ── helpers ────────────────────────────────────────────────────────────────
gc() { gcloud --account "$ACCOUNT" "$@"; }        # pinned per call; never `config set`

# A permission or API error means the seat could not read, which is INCONCLUSIVE. It is
# never zero: a denied `logging read` returns no rows, and scoring that as "no errors"
# turns a blind seat into a green light.
denied() { grep -qiE 'PERMISSION_DENIED|does not have|not authorized|ERROR: \(gcloud' "$1" 2>/dev/null; }
why() { head -c 200 "$1" 2>/dev/null | tr '\n' ' '; }

cutoff() {  # cutoff <hours ago> -> ISO-8601 prefix, portable (BSD date has no -d)
  python3 -c "import datetime,sys;print((datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(hours=float(sys.argv[1]))).strftime('%Y-%m-%dT%H:%M:%S'))" "$1"
}

log_errors() {  # log_errors <service>
  local s="$1" n_all n24 n1 ok=1
  gc logging read \
    "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${s}\" AND severity>=ERROR" \
    --project "$PROJECT" --freshness="${LOG_DAYS}d" --limit=500 \
    --format='value(timestamp,textPayload,jsonPayload.message)' \
    > "$WORK/err-${s}.txt" 2> "$WORK/err-${s}.stderr" || ok=0
  if [ "$ok" = 0 ] || denied "$WORK/err-${s}.stderr"; then
    echo "- ${s}: INCONCLUSIVE — $(why "$WORK/err-${s}.stderr")"
    return
  fi
  n_all="$(grep -c . "$WORK/err-${s}.txt")"
  n24="$(awk -v cut="$(cutoff 24)" '$1 > cut' "$WORK/err-${s}.txt" | grep -c .)"
  n1="$(awk -v cut="$(cutoff 1)" '$1 > cut' "$WORK/err-${s}.txt" | grep -c .)"
  echo "- ${s}: ERROR entries ${LOG_DAYS}d=${n_all} · 24h=${n24} · last 60 min=${n1} (cap 500)"
  if [ "${n_all}" -gt 0 ]; then
    echo "  top messages:"
    cut -f2- "$WORK/err-${s}.txt" \
      | sed -E 's/[0-9a-f]{8,}/#/g; s/[0-9]{2,}/N/g' | cut -c1-110 \
      | sort | uniq -c | sort -rn | head -5 | sed 's/^/    /'
  fi
}

# ── layer 1: deterministic probes ──────────────────────────────────────────
{
  echo "# Cloud checkup — deterministic probes — ${STAMP}"
  echo
  echo "Project \`${PROJECT}\` · region \`${REGION}\` · manifest \`${MANIFEST}\` · window ${LOG_DAYS}d"
  echo

  echo "## Identity"
  echo "- pinned account (every gcloud call): ${ACCOUNT}"
  echo "- observed gcloud default (not changed): $(gcloud config get-value account 2>/dev/null | tail -1)"
  # A stored credential can mint a token for a different principal than the one asked for,
  # so verify the token, not the config. Token goes over stdin: never argv, never the file.
  TOKEN="$(gc auth print-access-token 2>"$WORK/token.stderr")"
  if [ -n "$TOKEN" ]; then
    TOKEN_EMAIL="$(printf 'access_token=%s' "$TOKEN" \
      | curl -s --max-time 20 -X POST --data-binary @- https://oauth2.googleapis.com/tokeninfo 2>/dev/null \
      | python3 -c 'import json,sys;print(json.load(sys.stdin).get("email",""))' 2>/dev/null)"
    unset TOKEN
    if [ -z "$TOKEN_EMAIL" ]; then
      echo "- token identity: INCONCLUSIVE — tokeninfo returned no email"
    elif [ "$TOKEN_EMAIL" = "$ACCOUNT" ]; then
      echo "- token identity: ${TOKEN_EMAIL} (matches the pinned account)"
    else
      echo "- token identity: **${TOKEN_EMAIL} != pinned ${ACCOUNT}** — every cloud read below was made as somebody else; treat the whole cloud plane as INCONCLUSIVE"
    fi
  else
    echo "- token identity: INCONCLUSIVE — could not mint a token ($(why "$WORK/token.stderr"))"
  fi
  echo

  if [ -n "$PUBLIC_URL" ] && [ "${#ROUTES[@]}" -gt 0 ]; then
    echo "## Edge (${PUBLIC_URL})"
    for p in "${ROUTES[@]}"; do
      [ -n "$p" ] || continue
      echo "- ${p} → $(curl -s -o /dev/null -w '%{http_code} ttfb=%{time_starttransfer}s' --max-time 20 "${PUBLIC_URL}${p}" 2>&1)"
    done
    echo
    echo "## Security headers (${ROUTES[0]})"
    curl -sI --max-time 20 "${PUBLIC_URL}${ROUTES[0]}" 2>/dev/null \
      | grep -iE '^(strict-transport-security|content-security-policy|content-security-policy-report-only|x-frame-options|x-content-type-options|referrer-policy|permissions-policy|access-control-allow-origin)' \
      > "$WORK/headers.txt"
    if [ -s "$WORK/headers.txt" ]; then sed 's/^/- /' "$WORK/headers.txt"; else echo "- (none of the expected headers were returned)"; fi
    echo "- (compare against security_header_expectations in the manifest; report-only CSP is not enforcing)"
    echo
  fi

  echo "## Cloud Run (${PROJECT}/${REGION})"
  for s in "${SERVICES[@]}"; do
    [ -n "$s" ] || continue
    if gc run services describe "$s" --project "$PROJECT" --region "$REGION" \
         --format='value(status.latestReadyRevisionName,status.traffic[0].percent,spec.template.spec.containers[0].image,status.conditions[0].lastTransitionTime)' \
         > "$WORK/svc-${s}.txt" 2> "$WORK/svc-${s}.stderr"; then
      echo "- ${s}: $(cat "$WORK/svc-${s}.txt")"
      url="$(gc run services describe "$s" --project "$PROJECT" --region "$REGION" --format='value(status.url)' 2>/dev/null)"
      [ -n "$url" ] && echo "- ${s} /health → $(curl -s -o /dev/null -w '%{http_code} ttfb=%{time_starttransfer}s' --max-time 25 "${url}/health" 2>&1)"
    else
      echo "- ${s}: INCONCLUSIVE — $(why "$WORK/svc-${s}.stderr")"
    fi
  done
  echo

  echo "## Cloud Run errors, last ${LOG_DAYS} days (severity>=ERROR)"
  for s in "${SERVICES[@]}"; do [ -n "$s" ] && log_errors "$s"; done
  echo

  echo "## Cloud Run 5xx by service, last ${LOG_DAYS} days (cap 1000)"
  if gc logging read 'resource.type="cloud_run_revision" AND httpRequest.status>=500' \
       --project "$PROJECT" --freshness="${LOG_DAYS}d" --limit=1000 \
       --format='value(resource.labels.service_name)' >"$WORK/5xx.txt" 2>"$WORK/5xx.stderr" \
     && ! denied "$WORK/5xx.stderr"; then
    if [ -s "$WORK/5xx.txt" ]; then sort "$WORK/5xx.txt" | uniq -c | sed 's/^/- /'
    else echo "- none in the window"; fi
  else
    echo "- INCONCLUSIVE — $(why "$WORK/5xx.stderr")"
  fi
  echo

  echo "## Cloud Scheduler"
  if gc scheduler jobs list --project "$PROJECT" --location "$REGION" \
       --format='value(name.basename(),state,lastAttemptTime,status.code)' \
       >"$WORK/sched.txt" 2>"$WORK/sched.stderr"; then
    if [ -s "$WORK/sched.txt" ]; then sed 's/^/- /' "$WORK/sched.txt"
    else echo "- none in this location"; fi
  else
    echo "- INCONCLUSIVE — $(why "$WORK/sched.stderr")"
  fi
  echo

  echo "## Alert policies / uptime checks"
  pol_ok=1
  gc monitoring policies list --project "$PROJECT" --format='value(name)' >"$WORK/pol.txt" 2>"$WORK/pol.stderr" || pol_ok=0
  # Only fall back to the alpha surface when the stable one does not EXIST; a credential
  # or permission failure must stay INCONCLUSIVE rather than be retried into a new error.
  if [ "$pol_ok" = 0 ] && grep -qiE 'Invalid choice|unrecognized|Unknown command|not a valid' "$WORK/pol.stderr"; then
    pol_ok=1
    gc alpha monitoring policies list --project "$PROJECT" --format='value(name)' >"$WORK/pol.txt" 2>"$WORK/pol.stderr" || pol_ok=0
  fi
  if [ "$pol_ok" = 1 ]; then echo "- alert policies: $(grep -c . "$WORK/pol.txt")"
  else echo "- alert policies: INCONCLUSIVE — $(why "$WORK/pol.stderr")"; fi
  if gc monitoring uptime list-configs --project "$PROJECT" --format='value(name)' >"$WORK/up.txt" 2>"$WORK/up.stderr"; then
    echo "- uptime checks: $(grep -c . "$WORK/up.txt")"
  else
    echo "- uptime checks: INCONCLUSIVE — $(why "$WORK/up.stderr")"
  fi
  echo

  echo "## Secrets, service accounts and IAM"
  for s in "${SERVICES[@]}"; do
    [ -n "$s" ] || continue
    if gc run services describe "$s" --project "$PROJECT" --region "$REGION" \
         --format='value(spec.template.spec.serviceAccountName)' >"$WORK/sa-${s}.txt" 2>"$WORK/sa-${s}.stderr"; then
      echo "- ${s} runtime service account: $(cat "$WORK/sa-${s}.txt")"
    else
      echo "- ${s} runtime service account: INCONCLUSIVE — $(why "$WORK/sa-${s}.stderr")"
    fi
    # A denied get-iam-policy prints nothing, and `grep -c allUsers` on nothing is 0.
    # Reporting that 0 would turn a blind seat into "no public invoker". Gate on exit status.
    if gc run services get-iam-policy "$s" --project "$PROJECT" --region "$REGION" \
         --format=json >"$WORK/iam-${s}.json" 2>"$WORK/iam-${s}.stderr"; then
      echo "- ${s} allUsers invoker bindings: $(grep -c allUsers "$WORK/iam-${s}.json")"
    else
      echo "- ${s} allUsers invoker bindings: INCONCLUSIVE — $(why "$WORK/iam-${s}.stderr")"
    fi
  done
  if gc secrets list --project "$PROJECT" --format='value(name,createTime)' >"$WORK/sec.txt" 2>"$WORK/sec.stderr"; then
    if [ -s "$WORK/sec.txt" ]; then sed 's/^/- secret: /' "$WORK/sec.txt"; else echo "- secrets: none in this project"; fi
  else
    echo "- secrets: INCONCLUSIVE — $(why "$WORK/sec.stderr")"
  fi
  echo

  if [ "${#JOBS[@]}" -gt 0 ]; then
    echo "## Local scheduled jobs (label · pid · last exit)"
    for j in "${JOBS[@]}"; do
      [ -n "$j" ] || continue
      if command -v launchctl >/dev/null 2>&1; then
        row="$(launchctl list | awk -v l="$j" '$3==l {print "pid="$1"  last_exit="$2}')"
        echo "- ${j}: ${row:-not loaded}"
      elif command -v systemctl >/dev/null 2>&1; then
        echo "- ${j}: $(systemctl --user show "$j" -p ActiveState -p ExecMainPID -p ExecMainStatus --value 2>/dev/null | tr '\n' ' ')"
      else
        echo "- ${j}: INCONCLUSIVE — no launchctl or systemctl on this machine"
      fi
    done
    echo
  fi

  if [ -n "$REPO" ] && [ -d "$REPO/.git" ]; then
    echo "## Repo HEAD (deploy currency)"
    echo "- $(git -C "$REPO" log -1 --format='%h %ci %s' 2>/dev/null)"
    echo "- branch: $(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null)"
    echo
  fi

  echo "## Data stores declared in the manifest: ${CC_STORE_COUNT:-0}"
  echo "- probed by the inspection layer, per modules/<type>.md; no credentials are read here"
} > "$PROBES"
echo "[cloud-checkup] probes written: ${PROBES}"

# ── layer 2: read-only inspection ──────────────────────────────────────────
# The tool grant is a POSITIVE allowlist of exact read-only subcommands. A denylist is a
# guess about what a future release will name its mutating verbs; an allowlist fails closed
# when that guess is wrong. The short denylist below is defence in depth, not the mechanism.
AI_ALLOW=(
  "Bash(gcloud run services describe:*)" "Bash(gcloud run services list:*)"
  "Bash(gcloud run revisions list:*)" "Bash(gcloud run revisions describe:*)"
  "Bash(gcloud run services get-iam-policy:*)"
  "Bash(gcloud logging read:*)"
  "Bash(gcloud scheduler jobs list:*)" "Bash(gcloud scheduler jobs describe:*)"
  "Bash(gcloud monitoring policies list:*)" "Bash(gcloud alpha monitoring policies list:*)"
  "Bash(gcloud monitoring uptime list-configs:*)"
  "Bash(gcloud secrets list:*)" "Bash(gcloud secrets versions list:*)"
  "Bash(gcloud projects get-iam-policy:*)" "Bash(gcloud app versions list:*)"
  "Bash(gcloud container clusters describe:*)"
  "Bash(curl -sI:*)" "Bash(curl -s -o /dev/null:*)"
  "Bash(git log:*)" "Bash(git status:*)" "Bash(git rev-parse:*)" "Bash(git diff --stat:*)"
  "Bash(launchctl list:*)" "Bash(systemctl --user show:*)" "Bash(systemctl --user status:*)"
  "Bash(cat:*)" "Bash(head:*)" "Bash(tail:*)" "Bash(grep:*)" "Bash(wc:*)" "Bash(ls:*)" "Bash(date:*)"
  # Write is the one grant that can change the working tree. It is bounded by the prompt
  # (one report path) rather than by the grant, so run the checkup on a clean tree.
  "Read" "Glob" "Grep" "Write"
  # MongoDB MCP: read tools only, named — a wildcard would admit insert/update/delete/drop.
  # Launch the server with --readOnly as well; the allowlist is the gate, the flag is the belt.
  "mcp__mongodb__find" "mcp__mongodb__aggregate" "mcp__mongodb__count" "mcp__mongodb__explain"
  "mcp__mongodb__list-databases" "mcp__mongodb__list-collections" "mcp__mongodb__collection-indexes"
  "mcp__mongodb__collection-schema" "mcp__mongodb__collection-storage-size" "mcp__mongodb__db-stats"
)
AI_DENY=(
  "Bash(gcloud config:*)" "Bash(gcloud auth login:*)" "Bash(gcloud run deploy:*)"
  "Bash(gcloud run services update:*)" "Bash(gcloud builds:*)" "Bash(gcloud scheduler jobs run:*)"
  "Bash(gcloud scheduler jobs resume:*)" "Bash(gcloud secrets versions add:*)"
  "Bash(terraform:*)" "Bash(git push:*)" "Bash(git commit:*)" "Bash(git checkout:*)" "Bash(git reset:*)"
  "Bash(launchctl kickstart:*)" "Bash(launchctl load:*)" "Bash(launchctl unload:*)" "Bash(systemctl:*)"
)

if [ "${CC_SKIP_AI:-0}" != "1" ] && command -v claude >/dev/null 2>&1; then
  PROMPT="$(CC_DATE="$DATE" CC_STAMP="$STAMP" CC_OUT="$OUT" CC_PROBES="$PROBES" \
            CC_PROJECT="$PROJECT" CC_REGION="$REGION" CC_ACCOUNT="$ACCOUNT" CC_PUBLIC_URL="$PUBLIC_URL" \
            CC_MANIFEST_PATH="$MANIFEST" CC_TEMPLATE="${SKILL_DIR}/templates/CHECKUP-TEMPLATE.md" \
            CC_MODULES="${SKILL_DIR}/modules" CC_REPORT_DIR="$REPORT_DIR" \
            CC_SERVICE_LIST="${SERVICES[*]}" CC_LOG_DAYS="$LOG_DAYS" \
            python3 - "${SKILL_DIR}/templates/checkup_prompt.md" <<'PY'
import os, sys
text = open(sys.argv[1]).read()
for key, value in os.environ.items():
    if key.startswith("CC_"):
        text = text.replace("{{%s}}" % key[3:], value)
print(text)
PY
)"
  echo "[cloud-checkup] claude -p (${MODEL}) → ${AI_LOG}"
  claude -p "$PROMPT" --model "$MODEL" --no-session-persistence --output-format text \
    --allowedTools "${AI_ALLOW[@]}" --disallowedTools "${AI_DENY[@]}" > "$AI_LOG" 2>&1
  echo "[cloud-checkup] claude exit $?"
else
  echo "[cloud-checkup] inspection layer skipped (CC_SKIP_AI=${CC_SKIP_AI:-0}, claude=$(command -v claude || echo missing))"
fi

# ── layer 3: fallback report and one notification ──────────────────────────
if [ ! -s "$OUT" ]; then
  {
    echo "# Cloud checkup — ${DATE} — ${PROJECT} (probes only; the inspection layer produced no report)"
    echo
    cat "$PROBES"
    echo
    echo "OVERALL: INCONCLUSIVE — deterministic probes only; see ${AI_LOG}"
  } > "$OUT"
fi
VERDICT="$(grep -m1 -E '^OVERALL:' "$OUT" 2>/dev/null || echo 'OVERALL: INCONCLUSIVE — no OVERALL line in the report')"
echo "[cloud-checkup] ${VERDICT}"
echo "[cloud-checkup] report: ${OUT}"

if [ "${CC_NO_NOTIFY:-0}" != "1" ]; then
  case "$(printf '%s' "$VERDICT" | tr '[:lower:]' '[:upper:]')" in
    *UNHEALTHY*) LEVEL=RED ;;
    *HEALTHY*)   LEVEL=GREEN ;;
    *)           LEVEL=AMBER ;;
  esac
  CC_WEBHOOK_ENV="${CC_WEBHOOK_ENV:-}" CC_NOTIFY_CMD="${CC_NOTIFY_CMD:-}" \
    "${SKILL_DIR}/scripts/notify.sh" "$LEVEL" "Cloud checkup — ${PROJECT}" \
      "$VERDICT" "report: ${OUT}" || echo "[cloud-checkup] notification skipped or failed"
fi
echo "[cloud-checkup] $(date -u +%Y-%m-%dT%H:%M:%SZ) done"
