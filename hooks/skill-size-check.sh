#!/bin/bash
# Claude Code PreToolUse hook (matcher: Bash).
# Fires on every Bash tool call — exits silently unless the command is a git
# commit. Enforces a line cap on staged parent SKILL.md files at
# .claude/skills/<name>/SKILL.md or skills/<name>/SKILL.md (one level deep).
# Sub-skill files, templates, agents, and assets are exempt. A skill that grows
# past the cap should be split into sub-skill files, not padded.
#
# Config (optional env var):
#   SKILL_LINE_CAP  maximum lines per parent SKILL.md. Default: 200.

INPUT=$(cat)

echo "$INPUT" | grep -qE 'git commit' || exit 0

REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
STAGED=$(git -C "$REPO" diff --cached --name-only --diff-filter=ACM 2>/dev/null | \
  grep -E '^(\.claude/)?skills/[^/]+/SKILL\.md$' || true)

[ -z "$STAGED" ] && exit 0

CAP="${SKILL_LINE_CAP:-200}"
VIOLATIONS=""
while IFS= read -r FILE; do
  [ -z "$FILE" ] && continue
  ABS="$REPO/$FILE"
  [ -f "$ABS" ] || continue
  LINES=$(wc -l < "$ABS" | tr -d ' ')
  if [ "$LINES" -gt "$CAP" ]; then
    OVER=$((LINES - CAP))
    VIOLATIONS="$VIOLATIONS\n  $FILE = $LINES lines (over by $OVER)"
  fi
done <<< "$STAGED"

if [ -n "$VIOLATIONS" ]; then
  printf "SKILL.md %s-line cap violation:%b\n" "$CAP" "$VIOLATIONS" >&2
  printf "Fix: split the overflow into sub-skill files under the skill directory.\n" >&2
  exit 2
fi

exit 0
