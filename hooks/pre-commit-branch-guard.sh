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

INPUT=$(cat)

echo "$INPUT" | grep -qE '(^|[[:space:];&|("])git[[:space:]]+commit([[:space:]"]|$)' || exit 0

REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
BRANCH="$(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null)" || exit 0

PROTECTED_BRANCHES="${PROTECTED_BRANCHES:-main master}"
for P in $PROTECTED_BRANCHES; do
  if [ "$BRANCH" = "$P" ]; then
    printf "BLOCKED: attempted commit on '%s'. Rule: never commit directly to a protected branch.\n" "$BRANCH" >&2
    printf "Create a feature branch first: git checkout -b <topic>/<scope>\n" >&2
    exit 2
  fi
done

echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"additionalContext\":\"Committing on branch '$BRANCH'. Confirm this is the intended feature branch — a pull/merge/checkout hook can flip HEAD mid-session.\"}}"
