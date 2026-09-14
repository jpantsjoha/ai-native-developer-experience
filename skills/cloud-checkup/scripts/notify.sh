#!/bin/bash
# notify.sh <GREEN|AMBER|RED> <title> <line>...
#
# One line out of the whole checkup: the OVERALL verdict and where to read the rest.
# Pluggable. The default sink is a Slack incoming webhook whose URL is read from the env
# var NAMED by the manifest (slack.webhook_env), so no URL is ever written to a file.
# Set slack.command in the manifest to replace the sink with any command that takes the
# same argv: <level> <title> <line>...
#
# Exits 0 when there is nothing to post to, so a missing webhook never fails the checkup.
set -uo pipefail

LEVEL="${1:-AMBER}"; shift || true
TITLE="${1:-Cloud checkup}"; shift || true
LINES=("$@")

if [ -n "${CC_NOTIFY_CMD:-}" ]; then
  exec ${CC_NOTIFY_CMD} "$LEVEL" "$TITLE" "${LINES[@]}"
fi

WEBHOOK_ENV="${CC_WEBHOOK_ENV:-CLOUD_CHECKUP_WEBHOOK_URL}"
WEBHOOK="${!WEBHOOK_ENV:-}"
if [ -z "$WEBHOOK" ]; then
  echo "[notify] no webhook in \$${WEBHOOK_ENV}; verdict not posted: ${LEVEL} ${TITLE}"
  exit 0
fi

case "$LEVEL" in
  RED)   ICON=":red_circle:" ;;
  GREEN) ICON=":large_green_circle:" ;;
  *)     ICON=":large_yellow_circle:" ;;
esac

PAYLOAD="$(LEVEL="$LEVEL" TITLE="$TITLE" ICON="$ICON" python3 - "${LINES[@]}" <<'PY'
import json, os, sys
text = "%s *%s* (%s)\n%s" % (
    os.environ["ICON"], os.environ["TITLE"], os.environ["LEVEL"], "\n".join(sys.argv[1:])
)
print(json.dumps({"text": text}))
PY
)"

printf '%s' "$PAYLOAD" \
  | curl -s --max-time 20 -X POST -H 'Content-Type: application/json' --data-binary @- "$WEBHOOK" \
  >/dev/null && echo "[notify] posted ${LEVEL}" || echo "[notify] post failed"
