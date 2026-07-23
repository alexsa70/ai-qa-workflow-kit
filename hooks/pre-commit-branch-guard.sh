#!/bin/bash
# Claude Code PreToolUse hook (matcher: Bash).
# Fires on every Bash tool call — exits silently unless the command is a git
# commit. Enforces "never commit directly to the default branch" mechanically
# (hard block, exit 2), and surfaces the current branch on every other commit
# as a soft guard against a HEAD flip mid-session (a pull/merge/checkout hook
# can move HEAD without the model noticing).
#
# Config (optional env vars):
#   PROTECTED_BRANCHES  space-separated names to hard-block. Default: "main master".
#
# Explicit escape hatch: prefix the commit with ALLOW_MAIN_COMMIT=1 to permit an
# intentional direct-to-main commit — the hook then warns and allows instead of
# blocking, e.g. `ALLOW_MAIN_COMMIT=1 git commit -m "..."`. Add this only when a
# direct commit to a protected branch is deliberately authorized.

INPUT=$(cat)

echo "$INPUT" | grep -qE '(^|[[:space:];&|("])git[[:space:]]+commit([[:space:]"]|$)' || exit 0

# Resolve the repo the commit actually TARGETS, not the hook's own cwd. In a
# multi-repo setup the session cwd (where this hook runs) can differ from the
# directory the command commits in (e.g. `cd /path/to/other-repo && git commit`).
# Derive the target dir from the command itself, in priority order:
#   1. an explicit `git -C <dir>`;
#   2. the last `cd <dir>` before the commit;
#   3. the hook payload's own "cwd";
#   4. $PWD.
TARGET="$(printf '%s' "$INPUT" | grep -oE 'git[[:space:]]+-C[[:space:]]+[^[:space:]"]+' | head -n1 | sed -E 's/^git[[:space:]]+-C[[:space:]]+//')"
if [ -z "$TARGET" ]; then
  TARGET="$(printf '%s' "$INPUT" | grep -oE '(^|[;&|"[:space:]])cd[[:space:]]+[^[:space:]"&;|]+' | tail -n1 | sed -E 's/.*cd[[:space:]]+//')"
fi
if [ -z "$TARGET" ]; then
  TARGET="$(printf '%s' "$INPUT" | sed -nE 's/.*"cwd"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p' | head -n1)"
fi
[ -z "$TARGET" ] && TARGET="$PWD"

REPO="$(git -C "$TARGET" rev-parse --show-toplevel 2>/dev/null)" || exit 0
BRANCH="$(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null)" || exit 0

PROTECTED_BRANCHES="${PROTECTED_BRANCHES:-main master}"
for P in $PROTECTED_BRANCHES; do
  if [ "$BRANCH" = "$P" ]; then
    if echo "$INPUT" | grep -qE 'ALLOW_MAIN_COMMIT=(1|true|yes)'; then
      echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"additionalContext\":\"WARNING: direct commit to protected branch '$BRANCH' allowed via explicit ALLOW_MAIN_COMMIT override. Use only for an intentional, small, non-test change the user authorized.\"}}"
      exit 0
    fi
    printf "BLOCKED: attempted commit on '%s'. Rule: never commit directly to a protected branch.\n" "$BRANCH" >&2
    printf "Create a feature branch first: git checkout -b <topic>/<scope>\n" >&2
    printf "If a direct-to-main commit is intentional and explicitly authorized, re-run with: ALLOW_MAIN_COMMIT=1 git commit ...\n" >&2
    exit 2
  fi
done

echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"additionalContext\":\"Committing on branch '$BRANCH'. Confirm this is the intended feature branch — a pull/merge/checkout hook can flip HEAD mid-session.\"}}"
