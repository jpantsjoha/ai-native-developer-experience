#!/bin/bash
# perf-guardrail.sh — measure, attribute, clean up and verify developer-machine performance contention (macOS).
# Portable across Claude Code, Codex and Gemini/Antigravity: plain bash 3.2, no sudo,
# no third-party tools. Every subcommand is read-only except `cleanup` and `icloud`.
#
#   perf-guardrail.sh snapshot [--save FILE]   load, memory, swap, top consumers with their parent chain,
#                                        cloud-sync daemons, indexer, AI tool fleets, automation browsers
#   perf-guardrail.sh hangs [DAYS]             app hang/spin reports with the frames that explain them
#   perf-guardrail.sh fleet                    MCP / npm exec / node server processes grouped by the session that owns them
#   perf-guardrail.sh orphans                  automation browsers and drivers (Playwright, Selenium, Puppeteer,
#                                        harness Chrome, chromedriver) and whether their parent is gone
#   perf-guardrail.sh cleanup [--all]          kill orphaned automation browsers/drivers (--all: every automation
#                                        browser, never the user's own Chrome)
#   perf-guardrail.sh icloud {status|throttle|restore}   delegate to the sync throttle controller if installed
#   perf-guardrail.sh verify BEFORE.snap       before/after table against a saved snapshot
#   perf-guardrail.sh record "one-line lesson" append a dated entry to the lessons file
#
# Environment (all optional):
#   ICLOUD_CONTROL   path to icloud-control.sh   (default ~/local/icloud-system/icloud-control.sh)
#   PERF_LESSONS     lessons file                (default ~/local/system-health/LESSONS-LEARNED.md)
#   PERF_TOP         rows in top-N tables        (default 8)
set -uo pipefail
G=/usr/bin/grep   # `grep` may be a recursive ugrep function in the operator's shell
ICLOUD_CONTROL="${ICLOUD_CONTROL:-}"
PERF_LESSONS="${PERF_LESSONS:-$HOME/.perf-guardrail/LESSONS-LEARNED.md}"
TOP="${PERF_TOP:-8}"
NCPU=$(sysctl -n hw.ncpu 2>/dev/null || echo 1)
EXCLUDE_RE='Visual Studio Code|Code Helper|Cursor Helper|Antigravity Helper'   # IDE helpers carry --test-type but are not automation browsers
AUTOMATION_RE='remote-debugging-port|--headless|chrome-headless-shell|chromedriver|geckodriver|msedgedriver|safaridriver|user-data-dir=[^ ]*(playwright|puppeteer|selenium|harness|tmp|Temp|pw-)|--test-type|mcp-selenium|@playwright/mcp|playwright.*(chromium|firefox|webkit)|ms-playwright'

root_of() {  # print "pid:comm" of the top-most non-launchd ancestor
  local p=$1 pp c
  while :; do pp=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' '); [ -z "$pp" ] || [ "$pp" -le 1 ] && break; p=$pp; done
  c=$(ps -o comm= -p "$p" 2>/dev/null | sed 's#.*/##'); echo "$p:${c:-?}"
}
chain_of() {  # print the ancestor chain "comm <- comm <- comm"
  local p=$1 out="" c pp; while :; do c=$(ps -o comm= -p "$p" 2>/dev/null | sed 's#.*/##'); [ -z "$c" ] && break; out="${out:+$out <- }$c"; pp=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' '); [ -z "$pp" ] || [ "$pp" -le 1 ] && break; p=$pp; done; echo "$out"
}
mem_free_pct() { memory_pressure 2>/dev/null | $G -oE 'free percentage: [0-9]+' | $G -oE '[0-9]+' || echo "?"; }
load1() { sysctl -n vm.loadavg 2>/dev/null | awk '{print $2}'; }
count_re() { ps -axo args= | $G -cE "$1"; }
chrome_rss_mb() { ps -axo rss=,comm= | awk '/Google Chrome|Chromium|Microsoft Edge|chrome-headless-shell/{s+=$1} END{printf "%d", s/1024}'; }

snapshot() {
  local save=""; [ "${1:-}" = "--save" ] && save="${2:-}"
  local l1 mf sw ch npm mcp auto ai; l1=$(load1); mf=$(mem_free_pct); sw=$(sysctl -n vm.swapusage 2>/dev/null | awk '{print $6}'); ch=$(chrome_rss_mb)
  npm=$(count_re '^npm exec|^npx '); mcp=$(count_re '^node .*(mcp|toolbox|server\.js)|^uv(x)? .*(mcp|server\.py)'); auto=$(ps -axo args= | $G -E "$AUTOMATION_RE" | $G -vE "$EXCLUDE_RE" | $G -vc "$G")
  ai=$(ps -axo comm= | $G -cE '(^|/)(claude|codex|agy|gemini|kimi)$')
  echo "== snapshot $(date '+%Y-%m-%d %H:%M:%S') =="
  printf '  load(1m) %s on %s cores | mem free %s%% | swap used %s | Chrome family RSS %s MB\n' "$l1" "$NCPU" "$mf" "$sw" "$ch"
  printf '  npm/npx exec %s | node/uv MCP servers %s | automation browsers+drivers %s | AI CLI sessions %s\n' "$npm" "$mcp" "$auto" "$ai"
  echo "  -- cloud sync / indexer:"; ps -axo pid=,stat=,%cpu=,rss=,comm= | $G -E '/(bird|cloudd|fileproviderd|mds_stores|mds|OneDrive|Dropbox|Google Drive)$' | while read pid st cpu rss comm; do mb=$((rss/1024)); flag=""; case "$st" in T*) flag="  <-- STOPPED: run icloud restore";; esac; printf '     %-14s pid %-6s stat %-4s cpu %5s%% rss %5d MB%s
' "$(basename "$comm")" "$pid" "$st" "$cpu" "$mb" "$flag"; done
  echo "  -- top CPU (lifetime avg) with owner:"; ps -axo %cpu=,pid=,etime=,comm= | sort -rn | head -"$TOP" | while read cpu pid et comm; do printf '     %5s%% %-6s %10s %-28s <- %s\n' "$cpu" "$pid" "$et" "$(echo "$comm" | sed 's#.*/##' | cut -c1-28)" "$(root_of "$pid")"; done
  echo "  -- top RSS:"; ps -axo rss=,pid=,comm= | sort -rn | head -"$TOP" | awk '{c=$3; sub(/.*\//,"",c); printf "     %6.0f MB %-6s %s\n", $1/1024, $2, c}'
  if [ -n "$save" ]; then printf 'load=%s\nmemfree=%s\nswap=%s\nchrome_mb=%s\nnpm=%s\nmcp=%s\nauto=%s\nai=%s\n' "$l1" "$mf" "$sw" "$ch" "$npm" "$mcp" "$auto" "$ai" > "$save"; echo "  saved -> $save"; fi
}

hangs() {
  local days="${1:-7}" f app dt dur cd ub top
  echo "== app hang / spin reports, last $days days =="
  for f in /Library/Logs/DiagnosticReports/*.hang /Library/Logs/DiagnosticReports/*.spin ~/Library/Logs/DiagnosticReports/*.hang; do
    [ -f "$f" ] || continue; [ $(( ($(date +%s) - $(stat -f %m "$f")) / 86400 )) -le "$days" ] || continue
    app=$(basename "$f" | sed -E 's/_[0-9]{4}-.*//'); dt=$($G -m1 'Date/Time' "$f" | awk '{print $2, substr($3,1,5)}'); dur=$($G -m1 '^Duration:' "$f" | awk '{print $2}')
    cd=$($G -c 'CloudDocs' "$f"); ub=$($G -c 'ubiquityIdentityToken' "$f")
    top=$(awk '/com.apple.main-thread/{f=1} f&&/^$/{exit} f' "$f" | $G -m1 -oE '(CloudDocs|FileProvider|NSSavePanel|NSOpenPanel|CoreData|sqlite|mach_msg2_trap|__psynch_cvwait|semaphore_wait|read|write)[A-Za-z_]*' | head -1)
    printf '  %-22s %s  %8s  CloudDocs=%-4s ubiquityToken=%-3s main-thread: %s%s\n' "$app" "$dt" "$dur" "$cd" "$ub" "${top:-?}" "$( [ "$ub" -gt 0 ] && echo '  <-- iCloud daemon not answering (stopped or wedged)')"
  done | sort -k2 | tail -30
  echo "  Rule: ubiquityIdentityToken/CloudDocs on the main thread = bird stopped or wedged, not memory. Fix with icloud restore / killall bird, then re-check."
}

fleet() {
  echo "== MCP / npm exec / node server processes by owning session =="
  ps -axo pid=,ppid=,etime=,rss=,args= | $G -E ' (npm exec|npx |node [^ ]*(mcp|toolbox|server\.js)|uvx? .*(mcp|server\.py))' | $G -v "$G" | while read pid ppid et rss rest; do mb=$((rss/1024)); printf '  %-6s %10s %6d MB  %-70s  owner: %s\n' "$pid" "$et" "$mb" "$(echo "$rest" | cut -c1-70)" "$(root_of "$pid")"; done | sort -t: -k2 | head -60
  echo "  Rule: an AI CLI run that spawns >5 servers is a config problem (npx @latest re-resolves every start). Count per run, then remove what is unused."
}

orphans() {
  echo "== automation browsers and drivers =="
  local any=0
  ps -axo pid=,ppid=,etime=,rss=,args= | $G -E "$AUTOMATION_RE" | $G -vE "$EXCLUDE_RE" | $G -v "$G" | while read pid ppid et rss rest; do
    any=1; mb=$((rss/1024)); if [ "$ppid" -gt 1 ] && ps -p "$ppid" >/dev/null 2>&1; then alive="parent $ppid alive ($(ps -o comm= -p "$ppid" | sed 's#.*/##'))"; else alive="ORPHAN (parent gone)"; fi
    printf '  %-6s %10s %6d MB  %-60s  %s\n' "$pid" "$et" "$mb" "$(echo "$rest" | sed 's#/Applications/##' | cut -c1-60)" "$alive"
  done | head -40
  echo "  (the operator's own Chrome carries none of these flags and is never listed)"
}

cleanup() {
  local all=0; [ "${1:-}" = "--all" ] && all=1; local n=0
  echo "== cleanup automation browsers/drivers ($( [ $all = 1 ] && echo all || echo orphans only)) =="
  for pid in $(ps -axo pid=,args= | $G -E "$AUTOMATION_RE" | $G -vE "$EXCLUDE_RE" | $G -v "$G" | awk '{print $1}'); do
    ppid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' '); [ -z "$ppid" ] && continue
    if [ $all = 1 ] || [ "$ppid" -le 1 ] || ! ps -p "$ppid" >/dev/null 2>&1; then
      kill "$pid" 2>/dev/null && n=$((n+1)) && echo "  TERM $pid $(ps -o comm= -p "$pid" 2>/dev/null | sed 's#.*/##')"
    fi
  done
  sleep 3; for pid in $(ps -axo pid=,args= | $G -E "$AUTOMATION_RE" | $G -vE "$EXCLUDE_RE" | $G -v "$G" | awk '{print $1}'); do ppid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' '); if [ $all = 1 ] || [ -z "$ppid" ] || [ "$ppid" -le 1 ]; then kill -9 "$pid" 2>/dev/null && echo "  KILL $pid (did not exit on TERM)"; fi; done
  echo "  killed: $n process(es). Re-run 'orphans' to confirm."
}

icloud() {
  case "${1:-status}" in
    status)  if [ -x "$ICLOUD_CONTROL" ]; then "$ICLOUD_CONTROL" status; else echo "no throttle controller at $ICLOUD_CONTROL"; ps -axo pid=,stat=,%cpu=,comm= | $G -E '/(bird|cloudd|fileproviderd)$' | sed -E 's#/[^ ]*/##'; fi ;;
    throttle) [ -x "$ICLOUD_CONTROL" ] && "$ICLOUD_CONTROL" pause || echo "no controller: nothing done (never SIGSTOP bird by hand)";;
    restore)  if [ -x "$ICLOUD_CONTROL" ]; then "$ICLOUD_CONTROL" resume; else for p in $(pgrep -x bird) $(pgrep -u "$(id -u)" -x cloudd); do ps -o stat= -p "$p" | $G -q '^T' && kill -CONT "$p" && echo "SIGCONT $p"; done; fi ;;
    *) echo "usage: icloud {status|throttle|restore}"; return 1;;
  esac
}

verify() {
  local before="${1:-}"; [ -f "$before" ] || { echo "usage: verify BEFORE.snap (from: snapshot --save FILE)"; return 1; }
  local tmp; tmp=$(mktemp); snapshot --save "$tmp" >/dev/null
  echo "== before -> after =="; printf '  %-12s %10s  %10s\n' metric before after
  for k in load memfree swap chrome_mb npm mcp auto ai; do printf '  %-12s %10s  %10s\n' "$k" "$($G "^$k=" "$before" | cut -d= -f2)" "$($G "^$k=" "$tmp" | cut -d= -f2)"; done; rm -f "$tmp"
}

record() {
  local msg="${1:-}"; [ -n "$msg" ] || { echo "usage: record \"one-line lesson\""; return 1; }
  mkdir -p "$(dirname "$PERF_LESSONS")"; [ -f "$PERF_LESSONS" ] || printf '# Lessons learned — system performance\n\n' > "$PERF_LESSONS"
  printf '\n- %s — %s\n' "$(date '+%Y-%m-%d %H:%M')" "$msg" >> "$PERF_LESSONS"; echo "recorded in $PERF_LESSONS"
}

case "${1:-}" in
  snapshot) shift; snapshot "$@";; hangs) shift; hangs "$@";; fleet) fleet;; orphans) orphans;; cleanup) shift; cleanup "$@";;
  icloud) shift; icloud "$@";; verify) shift; verify "$@";; record) shift; record "$@";;
  *) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 1;;
esac
