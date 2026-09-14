#!/usr/bin/env bash
# review-gate.sh — independent code review on a Gemini lane, from the git pre-commit hook or by hand.
#
# The writer never approves its own work. This script asks a different model (Gemini 3.8 flash
# high by default, via the `agy` or `gemini` CLI) to review a diff and return one VERDICT line.
# Records live under .git/review-gate/; a PR review is also posted as a comment when `gh` is
# available. Bash 3.2 compatible; no repo-external dependencies beyond the CLI.
#
#   scripts/review-gate.sh --staged [--mode block|async]     what the next commit will contain (default block: wait for the verdict)
#   scripts/review-gate.sh --range <base>..<head>           any commit range
#   scripts/review-gate.sh --pr <number> [--no-comment]     a pull request (uses gh)
#   scripts/review-gate.sh --last                           print the most recent record
#
# Modes:   block  (default on demand) wait for the verdict; exit 1 on BLOCK (or on CONCERNS when REVIEW_GATE_STRICT=1)
#          async  detach; the verdict is recorded and printed by the next hook run (the opt-in pre-commit uses this)
# Not wired to run automatically: enable per commit with REVIEW_GATE=async|block or per clone with git config review.gate.
# Env:     REVIEW_GATE=off|async|block   REVIEW_GATE_MODEL (default gemini-3.8-flash-high)
#          REVIEW_GATE_LANE=agy|gemini    REVIEW_GATE_TIMEOUT seconds (default 600)   REVIEW_GATE_MAXLINES (default 4000)
set -uo pipefail
MODEL="${REVIEW_GATE_MODEL:-gemini-3.8-flash-high}"; TIMEOUT="${REVIEW_GATE_TIMEOUT:-600}"; MAXLINES="${REVIEW_GATE_MAXLINES:-4000}"
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "review-gate: not a git repository" >&2; exit 0; }
GITDIR="$(cd "$ROOT" && git rev-parse --absolute-git-dir 2>/dev/null || echo "$ROOT/.git")"   # a worktree has a .git FILE
DIR="$GITDIR/review-gate"; mkdir -p "$DIR"

lane() {  # prints the CLI to use, or nothing
  case "${REVIEW_GATE_LANE:-}" in agy|gemini) command -v "$REVIEW_GATE_LANE" >/dev/null 2>&1 && { echo "$REVIEW_GATE_LANE"; return; };; esac
  command -v agy >/dev/null 2>&1 && { echo agy; return; }; command -v gemini >/dev/null 2>&1 && { echo gemini; return; }
}
run_lane() {  # $1 prompt file -> stdout
  local cli; cli=$(lane); [ -n "$cli" ] || { echo "VERDICT: NONE — no review lane: install the agy or gemini CLI"; return 0; }
  local prompt; prompt=$(cat "$1")
  if command -v perl >/dev/null 2>&1; then
    case "$cli" in
      agy)    perl -e 'alarm shift; exec @ARGV' "$TIMEOUT" agy -p "$prompt" --model "$MODEL" --output-format text 2>&1 ;;
      gemini) perl -e 'alarm shift; exec @ARGV' "$TIMEOUT" gemini -p "$prompt" -m "$MODEL" 2>&1 ;;
    esac
  else
    case "$cli" in agy) agy -p "$prompt" --model "$MODEL" --output-format text 2>&1;; gemini) gemini -p "$prompt" -m "$MODEL" 2>&1;; esac
  fi
}
review() {  # $1 label, $2 diff file, $3 commits file, $4 record id -> prints record path; sets VERDICT
  local label=$1 diff=$2 commits=$3 id=$4 n; n=$(wc -l < "$diff" | tr -d ' ')
  [ "$n" -gt "$MAXLINES" ] && { head -"$MAXLINES" "$diff" > "$diff.h"; mv "$diff.h" "$diff"; echo "(diff truncated to $MAXLINES of $n lines)" >> "$commits"; }
  local p="$DIR/$id.prompt"
  { echo "You are the independent reviewer for '$label' in the repository $(basename "$ROOT"). Review adversarially: correctness and edge cases; security (injection, secrets, credentials, unsafe shell); tests present and biting; documentation and delivery records touched where needed; internal consistency (names, counts, dates); no AI attribution in commits or docs. Report concrete findings with file:line and a severity (critical/high/medium/low); be brief on what is fine. End with exactly one line: VERDICT: PASS or VERDICT: CONCERNS or VERDICT: BLOCK, followed by a one-line reason."; echo; echo "## Commits"; cat "$commits"; echo; echo "## Unified diff"; echo '```diff'; cat "$diff"; echo '```'; } > "$p"
  local raw; raw=$(run_lane "$p"); local v; v=$(printf '%s\n' "$raw" | /usr/bin/grep -oE 'VERDICT: (PASS|CONCERNS|BLOCK|NONE)[^|]*' | tail -1 | cut -c1-300); [ -z "$v" ] && v="VERDICT: NONE — the lane returned no verdict (not an approval)"
  { echo "# review-gate — $(date '+%Y-%m-%d %H:%M') — $label — model $MODEL"; echo; echo "$v"; echo; printf '%s\n' "$raw" | /usr/bin/grep -vE '^\s*$' | /usr/bin/grep -viE 'VERDICT:' | head -40 | cut -c1-240; } > "$DIR/$id.md"
  rm -f "$p" "$diff" "$commits"; printf '%s\n' "$v" > "$DIR/LAST"; VERDICT="$v"; echo "$DIR/$id.md"
}

mode="${REVIEW_GATE:-block}"; what=""; arg=""; comment=1
while [ $# -gt 0 ]; do case "$1" in --staged) what=staged; shift;; --range) what=range; arg=$2; shift 2;; --pr) what=pr; arg=$2; shift 2;; --last) what=last; shift;; --mode) mode=$2; shift 2;; --no-comment) comment=0; shift;; --worker) what=worker; shift;; *) shift;; esac; done
[ "$mode" = off ] && exit 0
case "$what" in
  last) [ -f "$DIR/LAST" ] && { echo "review-gate: last verdict — $(cat "$DIR/LAST")"; ls -t "$DIR"/*.md 2>/dev/null | head -1 | xargs -I{} echo "  record: {}"; } || echo "review-gate: no record yet"; exit 0 ;;
  staged)
    id="$(date '+%Y%m%d-%H%M%S')-staged"; git diff --cached > "$DIR/$id.diff"; [ -s "$DIR/$id.diff" ] || { rm -f "$DIR/$id.diff"; exit 0; }
    git diff --cached --stat > "$DIR/$id.commits"; echo "(staged, not yet committed)" >> "$DIR/$id.commits"
    if [ "$mode" = async ]; then
      [ -f "$DIR/LAST" ] && echo "review-gate: last verdict — $(cat "$DIR/LAST")" >&2
      nohup bash "$0" --worker --range "$id" >/dev/null 2>&1 & echo "review-gate: independent review of the staged diff queued ($MODEL); verdict in .git/review-gate/$id.md and on the next commit" >&2; exit 0
    fi
    rec=$(review "staged changes" "$DIR/$id.diff" "$DIR/$id.commits" "$id"); echo "review-gate: $VERDICT" >&2; echo "  record: $rec" >&2
    case "$VERDICT" in *BLOCK*) exit 1;; *CONCERNS*) [ "${REVIEW_GATE_STRICT:-0}" = 1 ] && exit 1;; esac; exit 0 ;;
  worker) id=$arg; rec=$(review "staged changes" "$DIR/$id.diff" "$DIR/$id.commits" "$id"); exit 0 ;;
  range)
    id="$(date '+%Y%m%d-%H%M%S')-range"; git diff "$arg" > "$DIR/$id.diff"; git log --format='%h %s' "$arg" > "$DIR/$id.commits" 2>/dev/null
    [ -s "$DIR/$id.diff" ] || { echo "review-gate: empty diff for $arg"; rm -f "$DIR/$id.diff" "$DIR/$id.commits"; exit 0; }
    rec=$(review "$arg" "$DIR/$id.diff" "$DIR/$id.commits" "$id"); echo "review-gate: $VERDICT"; echo "  record: $rec"; case "$VERDICT" in *BLOCK*) exit 1;; esac; exit 0 ;;
  pr)
    command -v gh >/dev/null 2>&1 || { echo "review-gate: gh is required for --pr"; exit 1; }
    id="$(date '+%Y%m%d-%H%M%S')-pr$arg"; gh pr diff "$arg" > "$DIR/$id.diff" 2>/dev/null; gh pr view "$arg" --json commits --jq '.commits[] | "\(.oid[0:8]) \(.messageHeadline)"' > "$DIR/$id.commits" 2>/dev/null
    [ -s "$DIR/$id.diff" ] || { echo "review-gate: could not read the diff of PR #$arg"; exit 1; }
    rec=$(review "PR #$arg" "$DIR/$id.diff" "$DIR/$id.commits" "$id"); echo "review-gate: $VERDICT"; echo "  record: $rec"
    if [ "$comment" = 1 ]; then body="Independent review (review-gate, model $MODEL). $VERDICT
$(sed -n '5,30p' "$rec")
Record: .git/review-gate/$id.md. A changed candidate gets a fresh review; the merge decision stays with the delivery gate and the operator."; gh pr comment "$arg" --body "$body" >/dev/null 2>&1 && echo "  comment posted on PR #$arg" || echo "  (could not post the comment)"; fi
    case "$VERDICT" in *BLOCK*) exit 1;; esac; exit 0 ;;
  *) sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
