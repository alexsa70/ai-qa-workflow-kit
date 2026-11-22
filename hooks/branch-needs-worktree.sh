#!/bin/bash
# Claude Code PreToolUse hook (matcher: Bash).
# Rule: every new branch lives in its own git worktree.
# Blocks in-place branch creation (git checkout -b/-B, git switch -c/-C/--create,
# git branch <name>) and points at the kit's bin/qa-worktree.
# Allowed: git worktree add -b ..., git branch with listing/deleting/renaming flags.
INPUT=$(cat)
CMD=$(printf '%s' "$INPUT" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("tool_input",{}).get("command",""))
except Exception: pass' 2>/dev/null)
# No python3: fall back to the raw payload (the patterns still match inside JSON).
[ -n "$CMD" ] || CMD="$INPUT"
[ -n "$CMD" ] || exit 0

# git, optionally followed by global options such as -C <path>
G='(^|[;&|(]|&&|\|\|)[[:space:]]*git([[:space:]]+(-C[[:space:]]+[^[:space:]]+|-c[[:space:]]+[^[:space:]]+|--[a-z-]+=[^[:space:]]+))*[[:space:]]+'

block=""
printf '%s' "$CMD" | grep -qE "${G}checkout[[:space:]]+(.*[[:space:]])?-[bB]([[:space:]]|$)" && block=1
printf '%s' "$CMD" | grep -qE "${G}switch[[:space:]]+(.*[[:space:]])?(-[cC]|--create|--force-create)([[:space:]=]|$)" && block=1
# `git branch <name>` creates; `git branch` with -d/-D/-m/-M/-l/-a/-r/-v/--list/--show-current etc. does not.
if printf '%s' "$CMD" | grep -qE "${G}branch[[:space:]]+[^-[:space:]]"; then
  printf '%s' "$CMD" | grep -qE "${G}branch[[:space:]]+.*(-[dDmMcClarv]|--(delete|move|copy|list|all|remotes|show-current|contains|merged|no-merged|set-upstream-to|unset-upstream|edit-description))([[:space:]=]|$)" || block=1
fi
[ -n "$block" ] || exit 0

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cat >&2 <<MSG
BLOCKED: a new branch must be created in its own git worktree, not in place.
Use:  bash $KIT/bin/qa-worktree <target-path> <branch> [base]
It creates the worktree, links/copies the local files listed in the target's
ai-workflow/project-context.md (section "Worktrees"), and prints the new target
path. Continue the work there (git -C <path> ..., or use it as the target).
MSG
exit 2
