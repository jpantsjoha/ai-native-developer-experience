#!/usr/bin/env bash
# context-graph-refresh.sh — keep a code-intelligence graph coherent, on demand.
#
# A semantic code graph (graft, or any indexer an agent queries for "where is X /
# who calls Y / what's this file's API") is a snapshot. It rots silently: the
# agent keeps answering from a structure that no longer matches the tree, and
# nothing errors. This guard makes the graph self-heal.
#
# It is idempotent and cheap when fresh (one `find`, then exit) and rebuilds ONLY
# when a tracked source file is newer than the graph. An atomic lock single-flights
# concurrent callers (git hook + SessionStart hook + manual) so a half-built graph
# is never queried mid-write.
#
# Portable: configure via env, defaults target a graft graph.
#   CGF_REPO       repo root                     (default: git toplevel of $PWD)
#   CGF_GRAPH      file whose mtime = freshness   (default: $REPO/graft/.graph/wiring.json)
#   CGF_BUILD_CMD  rebuild command                (default: npx -y @nanonets/graft@0.10.1 build)
#   CGF_SRC        find-expr of source extensions (default: py,ts,tsx,js — see below)
#   CGF_PRUNE      dir names to skip              (default: .git node_modules .venv graft .next dist build)
#
# Usage:
#   context-graph-refresh.sh          # rebuild only if stale (what hooks call)
#   context-graph-refresh.sh --force  # rebuild unconditionally
# Callers that must not block should background it:  context-graph-refresh.sh &

set -uo pipefail

REPO="${CGF_REPO:-$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")}"
GRAPH="${CGF_GRAPH:-$REPO/graft/.graph/wiring.json}"
BUILD_CMD="${CGF_BUILD_CMD:-npx -y @nanonets/graft@0.10.1 build}"
LOCK="${CGF_LOCK:-$REPO/.context-graph.refresh.lock}"
LOG="${CGF_LOG:-$REPO/.context-graph.refresh.log}"
# space-separated extensions (no dot); default covers Python + TS/JS front-ends
CGF_EXTS="${CGF_EXTS:-py ts tsx js}"
CGF_PRUNE="${CGF_PRUNE:-.git node_modules .venv graft .next dist build}"

FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

cd "$REPO" || { echo "context-graph: repo not found: $REPO" >&2; exit 1; }

# Build the find(1) expression from the configured extensions and prune dirs.
_prune=(); for d in $CGF_PRUNE; do _prune+=( -name "$d" -o ); done
unset '_prune[${#_prune[@]}-1]'                       # drop trailing -o
_exts=(); for e in $CGF_EXTS; do _exts+=( -name "*.$e" -o ); done
unset '_exts[${#_exts[@]}-1]'

is_stale() {
  [ ! -f "$GRAPH" ] && return 0                       # no graph yet → stale
  local newer
  newer=$(find . -type d \( "${_prune[@]}" \) -prune -o \
                 -type f \( "${_exts[@]}" \) -newer "$GRAPH" -print -quit 2>/dev/null)
  [ -n "$newer" ]
}

if [ "$FORCE" -eq 0 ] && ! is_stale; then
  echo "context-graph: FRESH — graph newer than all tracked source, skip"
  exit 0
fi

# atomic single-flight (mkdir is atomic on all POSIX filesystems)
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "context-graph: rebuild already running (lock held) — skip"
  exit 0
fi
trap 'rm -rf "$LOCK"' EXIT

echo "context-graph: rebuild START $(date '+%F %T')  [$BUILD_CMD]" >>"$LOG"
if ( eval "$BUILD_CMD" ) >>"$LOG" 2>&1; then
  echo "context-graph: rebuild OK    $(date '+%F %T')" >>"$LOG"
  echo "context-graph: rebuilt OK (log: $LOG)"
else
  rc=$?
  echo "context-graph: rebuild FAIL  $(date '+%F %T') rc=$rc" >>"$LOG"
  echo "context-graph: rebuild FAILED rc=$rc — see $LOG" >&2
  exit "$rc"
fi
