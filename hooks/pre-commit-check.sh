#!/bin/bash
# Claude Code PreToolUse hook (matcher: Bash).
# Fires on every Bash tool call — exits silently unless the command is a git
# commit or git add. Advisory only (never blocks): warns before a bulk stage of
# many untracked files, and before a very large staged diff that likely contains
# generated artifacts.
#
# Config (optional env vars):
#   BULK_ADD_THRESHOLD  untracked-file count that triggers the bulk-add warning. Default: 20.
#   LARGE_DIFF_LINES    staged-line count that triggers the large-diff warning. Default: 5000.
#   ARTIFACT_PATTERN    egrep of paths treated as likely generated artifacts.
#                       Default: 'allure-results/|reports/|outputs/|\.html$|report\.'

INPUT=$(cat)

echo "$INPUT" | grep -qE 'git (commit|add)' || exit 0

REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
BULK_ADD_THRESHOLD="${BULK_ADD_THRESHOLD:-20}"
LARGE_DIFF_LINES="${LARGE_DIFF_LINES:-5000}"
ARTIFACT_PATTERN="${ARTIFACT_PATTERN:-allure-results/|reports/|outputs/|\.html\$|report\.}"

# Bulk-staging guard: warn before git add -A / . / --all when many untracked files exist.
if echo "$INPUT" | grep -qE 'git add[[:space:]]+(-A|--all|\.)([[:space:]"]|$)'; then
  UNTRACKED=$(git -C "$REPO" status --porcelain 2>/dev/null | grep -c '^??' || echo 0)
  if [ "$UNTRACKED" -gt "$BULK_ADD_THRESHOLD" ]; then
    echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"additionalContext\":\"BULK-ADD WARN: $UNTRACKED untracked files detected. Review before staging all — stage individual files or verify .gitignore covers generated artifacts.\"}}"
  fi
fi

LINES=$(git -C "$REPO" diff --cached --numstat 2>/dev/null | awk '{s+=$1} END {print s+0}')
FILES=$(git -C "$REPO" diff --cached --name-only 2>/dev/null)
FILE_COUNT=$(echo "$FILES" | grep -c . || true)

[ "$LINES" -eq 0 ] && exit 0

SUSPECTS=$(echo "$FILES" | grep -E "$ARTIFACT_PATTERN" | head -5)

if [ "$LINES" -gt "$LARGE_DIFF_LINES" ]; then
  MSG="PRE-COMMIT WARN: $LINES lines staged across $FILE_COUNT files."
  if [ -n "$SUSPECTS" ]; then
    MSG="$MSG Likely generated artifacts detected: $(echo "$SUSPECTS" | tr '\n' ' '). Add to .gitignore if unintentional."
  else
    MSG="$MSG Verify no generated/build artifacts are included."
  fi
  echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"additionalContext\":\"$MSG\"}}"
fi
