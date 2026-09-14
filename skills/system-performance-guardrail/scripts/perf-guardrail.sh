#!/bin/bash
# perf-guardrail.sh — measure, attribute, clean up and verify developer-machine performance
# contention (macOS). Plain bash 3.2, no sudo, no third-party tools; portable across Claude Code,
# Codex and Gemini/Antigravity skill roots.
#
# Read-only: snapshot, hangs, fleet, orphans, verify, cleanup without --yes.
# Writes:    cleanup --yes (kills processes), icloud throttle|restore (signals daemons),
#            record (appends to the lessons file).
#
#   perf-guardrail.sh snapshot [--save FILE]   load, memory, swap, top consumers with the session that owns them,
#                                              cloud-sync daemons (a stopped one is flagged), indexer, MCP fleets,
#                                              disposable automation browsers
#   perf-guardrail.sh hangs [DAYS]             app hang/spin reports with the frames that explain them
#   perf-guardrail.sh fleet                    MCP / npm exec / node server processes grouped by owning session
#   perf-guardrail.sh orphans                  automation browsers and drivers: disposable or not, parent alive or not
#   perf-guardrail.sh cleanup [--all] [--yes]  list (default) or kill (--yes) DISPOSABLE automation browsers/drivers whose
#                                              launcher is gone; --all: every disposable one. A browser on a normal profile
#                                              is never a candidate, whatever flags it carries.
#   perf-guardrail.sh icloud {status|throttle|restore}   delegate to a sync throttle controller if one is configured
#   perf-guardrail.sh verify BEFORE.snap       before/after table against a saved snapshot
#   perf-guardrail.sh record "one-line lesson" append a dated entry to the lessons file
#
# Environment (all optional):
#   ICLOUD_CONTROL       path to a throttle controller script accepting status|pause|resume (default: none)
#   PERF_LESSONS         lessons file (default ~/.perf-guardrail/LESSONS-LEARNED.md)
#   PERF_DISPOSABLE_RE   extra regex marking a browser profile path as disposable (e.g. your harness profile dir)
#   PERF_KEEP_RE         regex of command lines that must never be listed or killed
#   PERF_TOP             rows in top-N tables (default 8)
set -uo pipefail
G=/usr/bin/grep   # `grep` may be a recursive ugrep function in the operator's shell
ICLOUD_CONTROL="${ICLOUD_CONTROL:-}"
PERF_LESSONS="${PERF_LESSONS:-$HOME/.perf-guardrail/LESSONS-LEARNED.md}"
TOP="${PERF_TOP:-8}"
NCPU=$(sysctl -n hw.ncpu 2>/dev/null || echo 1)

# A process is an automation browser only when it is a browser BINARY carrying an automation MARKER,
# or a WebDriver binary. It is DISPOSABLE only when it runs headless or on a throwaway profile; a
# browser on the user's normal profile is never disposable, even with --remote-debugging-port
# (that is a developer's DevTools session). IDE helpers never match BROWSER_RE.
BROWSER_RE='(Google Chrome|Chromium|Chrome for Testing|chrome-headless-shell|Microsoft Edge|Brave Browser|Firefox|Nightly|WebKit|Playwright)(\.app/Contents/MacOS/[^ ]*|[^ ]*) '
MARKER_RE='--remote-debugging-port|--remote-debugging-pipe|--headless|--user-data-dir='
DRIVER_RE='(^|/)(chromedriver|geckodriver|msedgedriver|safaridriver|operadriver)( |$)'
DISPOSABLE_RE="--headless|chrome-headless-shell|--user-data-dir=[^ ]*(/tmp/|/var/folders/|/T/|playwright|puppeteer|selenium|harness|pw-|ms-playwright)|ms-playwright/${PERF_DISPOSABLE_RE:+|$PERF_DISPOSABLE_RE}"
KEEP_RE="${PERF_KEEP_RE:-__never_matches__}"

root_of() {  # "pid:comm" of the top-most non-launchd ancestor
  local p=$1 pp c
  while :; do pp=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' '); [ -z "$pp" ] || [ "$pp" -le 1 ] && break; p=$pp; done
  c=$(ps -o comm= -p "$p" 2>/dev/null | sed 's#.*/##'); echo "$p:${c:-?}"
}
mem_free_pct() { memory_pressure 2>/dev/null | $G -oE 'free percentage: [0-9]+' | $G -oE '[0-9]+' || echo "?"; }
load1() { sysctl -n vm.loadavg 2>/dev/null | awk '{print $2}'; }
count_re() { ps -axo args= | $G -cE -e "$1"; }
chrome_rss_mb() { ps -axo rss=,comm= | awk '/Google Chrome|Chromium|Microsoft Edge|chrome-headless-shell|Brave/{s+=$1} END{printf "%d", s/1024}'; }

# Emit one line per automation browser/driver: pid ppid etime rss disposable(yes/no) parent(alive/gone) args
automation_rows() {
  ps -axo pid=,ppid=,etime=,rss=,args= | while read pid ppid et rss rest; do
    echo "$rest" | $G -qE -e "$KEEP_RE" && continue
    if echo "$rest" | $G -qE -e "$DRIVER_RE"; then disp=yes
    elif echo "$rest" | $G -qE -e "$BROWSER_RE" && echo "$rest" | $G -qE -e "$MARKER_RE"; then
      if echo "$rest" | $G -qE -e "$DISPOSABLE_RE"; then disp=yes; else disp=no; fi
    else continue; fi
    if [ "$ppid" -gt 1 ] && ps -p "$ppid" >/dev/null 2>&1; then par="alive:$ppid"; else par="gone"; fi   # ppid 1 = launchd: launcher exited, or app started from Finder
    echo "$pid $ppid $et $rss $disp $par $rest"
  done
}

snapshot() {
  local save=""; [ "${1:-}" = "--save" ] && save="${2:-}"
  local l1 mf sw ch npm mcp auto ai; l1=$(load1); mf=$(mem_free_pct); sw=$(sysctl -n vm.swapusage 2>/dev/null | awk '{print $6}'); ch=$(chrome_rss_mb)
  npm=$(count_re '^npm exec|^npx '); mcp=$(count_re '^node .*(mcp|toolbox|server\.js)|^uv(x)? .*(mcp|server\.py)'); auto=$(automation_rows | awk '$5=="yes"' | wc -l | tr -d ' ')
  ai=$(ps -axo comm= | $G -cE '(^|/)(claude|codex|agy|gemini|kimi)$')
  echo "== snapshot $(date '+%Y-%m-%d %H:%M:%S') =="
  printf '  load(1m) %s on %s cores | mem free %s%% | swap used %s | browser family RSS %s MB\n' "$l1" "$NCPU" "$mf" "$sw" "$ch"
  printf '  npm/npx exec %s | node/uv MCP servers %s | disposable automation browsers+drivers %s | AI CLI sessions %s\n' "$npm" "$mcp" "$auto" "$ai"
  echo "  -- cloud sync / indexer:"; ps -axo pid=,stat=,%cpu=,rss=,comm= | $G -E '/(bird|cloudd|fileproviderd|mds_stores|mds|OneDrive|Dropbox|Google Drive)$' | while read pid st cpu rss comm; do mb=$((rss/1024)); flag=""; case "$st" in T*) flag="  <-- STOPPED: run icloud restore";; esac; printf '     %-14s pid %-6s stat %-4s cpu %5s%% rss %5d MB%s\n' "$(basename "$comm")" "$pid" "$st" "$cpu" "$mb" "$flag"; done
  echo "  -- top CPU (lifetime avg) with owner:"; ps -axo %cpu=,pid=,etime=,comm= | sort -rn | head -"$TOP" | while read cpu pid et comm; do printf '     %5s%% %-6s %10s %-28s <- %s\n' "$cpu" "$pid" "$et" "$(echo "$comm" | sed 's#.*/##' | cut -c1-28)" "$(root_of "$pid")"; done
  echo "  -- top RSS:"; ps -axo rss=,pid=,comm= | sort -rn | head -"$TOP" | awk '{c=$3; sub(/.*\//,"",c); printf "     %6.0f MB %-6s %s\n", $1/1024, $2, c}'
  if [ -n "$save" ]; then
    if printf 'load=%s\nmemfree=%s\nswap=%s\nchrome_mb=%s\nnpm=%s\nmcp=%s\nauto=%s\nai=%s\n' "$l1" "$mf" "$sw" "$ch" "$npm" "$mcp" "$auto" "$ai" > "$save" 2>/dev/null; then echo "  saved -> $save"; else echo "  ERROR: cannot write $save" >&2; return 1; fi
  fi
}

hangs() {
  local days="${1:-7}" f app dt dur cd ub top
  echo "== app hang / spin reports, last $days days =="
  for f in /Library/Logs/DiagnosticReports/*.hang /Library/Logs/DiagnosticReports/*.spin ~/Library/Logs/DiagnosticReports/*.hang; do
    [ -f "$f" ] || continue; [ $(( ($(date +%s) - $(stat -f %m "$f")) / 86400 )) -le "$days" ] || continue
    app=$(basename "$f" | sed -E 's/_[0-9]{4}-.*//'); dt=$($G -m1 'Date/Time' "$f" | awk '{print $2, substr($3,1,5)}'); dur=$($G -m1 '^Duration:' "$f" | awk '{print $2}')
    cd=$($G -c 'CloudDocs' "$f"); ub=$($G -c 'ubiquityIdentityToken' "$f")
    top=$(awk '/com.apple.main-thread/{f=1} f&&/^$/{exit} f' "$f" | $G -m1 -oE '(CloudDocs|FileProvider|NSSavePanel|NSOpenPanel|CoreData|sqlite|mach_msg2_trap|__psynch_cvwait|semaphore_wait|read|write)[A-Za-z_]*' | head -1)
    printf '  %-22s %s  %8s  CloudDocs=%-4s ubiquityToken=%-3s main-thread: %s%s\n' "$app" "$dt" "$dur" "$cd" "$ub" "${top:-?}" "$( [ "$ub" -gt 0 ] && echo '  <-- cloud-sync daemon not answering (stopped or wedged)')"
  done | sort -k2 | tail -30
  echo "  Rule: ubiquityIdentityToken/CloudDocs on the main thread = the sync daemon is stopped or wedged, not memory. Restore or restart it, then re-check."
}

fleet() {
  echo "== MCP / npm exec / node server processes by owning session =="
  ps -axo pid=,ppid=,etime=,rss=,args= | $G -E ' (npm exec|npx |node [^ ]*(mcp|toolbox|server\.js)|uvx? .*(mcp|server\.py))' | $G -v "$G" | while read pid ppid et rss rest; do mb=$((rss/1024)); printf '  %-6s %10s %6d MB  %-70s  owner: %s\n' "$pid" "$et" "$mb" "$(echo "$rest" | cut -c1-70)" "$(root_of "$pid")"; done | sort -t: -k2 | head -60
  echo "  Rule: an AI CLI run that spawns more than a handful of servers is a config problem (npx @latest re-resolves every start). Count per run, then remove what is unused."
}

orphans() {
  echo "== automation browsers and drivers =="
  automation_rows | while read pid ppid et rss disp par rest; do
    mb=$((rss/1024)); case "$par" in alive:*) ps_="parent ${par#alive:} alive ($(ps -o comm= -p "${par#alive:}" | sed 's#.*/##'))";; *) ps_="launcher gone (ppid $ppid)";; esac
    printf '  %-6s %10s %6d MB  disposable=%-3s %-34s %s\n' "$pid" "$et" "$mb" "$disp" "$ps_" "$(echo "$rest" | sed 's#/Applications/##' | cut -c1-70)"
  done | head -40
  echo "  Candidates for cleanup: disposable=yes AND launcher gone. disposable=no means a normal profile: report it, never kill it."
}

cleanup() {
  local all=0 yes=0 a; for a in "$@"; do case "$a" in --all) all=1;; --yes) yes=1;; esac; done
  echo "== cleanup automation browsers/drivers ($( [ $all = 1 ] && echo 'all disposable' || echo 'disposable with launcher gone'); $( [ $yes = 1 ] && echo KILLING || echo 'dry run — add --yes to kill')) =="
  local cands; cands=$(automation_rows | awk -v all=$all '$5=="yes" && (all==1 || $6=="gone") {print $1}')
  [ -z "$cands" ] && { echo "  nothing to do"; return 0; }
  local pid; for pid in $cands; do printf '  %s %-6s %s\n' "$( [ $yes = 1 ] && echo TERM || echo would-kill )" "$pid" "$(ps -o args= -p "$pid" | cut -c1-90)"; [ $yes = 1 ] && kill "$pid" 2>/dev/null; done
  [ $yes = 1 ] || return 0
  sleep 3
  for pid in $cands; do   # only the ORIGINAL candidates, only if still alive and still matching
    kill -0 "$pid" 2>/dev/null || continue
    automation_rows | awk -v p="$pid" '$1==p && $5=="yes"' | $G -q . && kill -9 "$pid" 2>/dev/null && echo "  KILL $pid (did not exit on TERM)"
  done
  echo "  done. Re-run 'orphans' to confirm."
}

icloud() {
  case "${1:-status}" in
    status)  if [ -n "$ICLOUD_CONTROL" ] && [ -x "$ICLOUD_CONTROL" ]; then "$ICLOUD_CONTROL" status; else echo "no throttle controller configured (ICLOUD_CONTROL); daemon state:"; ps -axo pid=,stat=,%cpu=,comm= | $G -E '/(bird|cloudd|fileproviderd)$' | sed -E 's#/[^ ]*/##'; fi ;;
    throttle) if [ -n "$ICLOUD_CONTROL" ] && [ -x "$ICLOUD_CONTROL" ]; then "$ICLOUD_CONTROL" pause; else echo "no controller: nothing done (never SIGSTOP a sync daemon by hand; use taskpolicy -b -p <pid> to throttle)"; fi ;;
    restore)  if [ -n "$ICLOUD_CONTROL" ] && [ -x "$ICLOUD_CONTROL" ]; then "$ICLOUD_CONTROL" resume; else for p in $(pgrep -x bird) $(pgrep -u "$(id -u)" -x cloudd); do ps -o stat= -p "$p" | $G -q '^T' && kill -CONT "$p" && echo "SIGCONT $p"; done; fi ;;
    *) echo "usage: icloud {status|throttle|restore}"; return 1;;
  esac
}

verify() {
  local before="${1:-}"; [ -f "$before" ] || { echo "usage: verify BEFORE.snap (from: snapshot --save FILE)"; return 1; }
  local tmp; tmp=$(mktemp); snapshot --save "$tmp" >/dev/null || return 1
  echo "== before -> after =="; printf '  %-12s %10s  %10s\n' metric before after
  for k in load memfree swap chrome_mb npm mcp auto ai; do printf '  %-12s %10s  %10s\n' "$k" "$($G "^$k=" "$before" | cut -d= -f2)" "$($G "^$k=" "$tmp" | cut -d= -f2)"; done; rm -f "$tmp"
}

record() {
  local msg="${1:-}"; [ -n "$msg" ] || { echo "usage: record \"one-line lesson\""; return 1; }
  mkdir -p "$(dirname "$PERF_LESSONS")" || return 1; [ -f "$PERF_LESSONS" ] || printf '# Lessons learned — system performance\n\n' > "$PERF_LESSONS"
  printf '\n- %s — %s\n' "$(date '+%Y-%m-%d %H:%M')" "$msg" >> "$PERF_LESSONS" && echo "recorded in $PERF_LESSONS"
}

case "${1:-}" in
  snapshot) shift; snapshot "$@";; hangs) shift; hangs "$@";; fleet) fleet;; orphans) orphans;; cleanup) shift; cleanup "$@";;
  icloud) shift; icloud "$@";; verify) shift; verify "$@";; record) shift; record "$@";;
  *) sed -n '2,29p' "$0" | sed 's/^# \{0,1\}//'; exit 1;;
esac
