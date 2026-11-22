# Sourced by the kit hooks. Not a hook itself.
#
# target_repo "<hook stdin JSON>"
#   Prints the toplevel of the repository a Bash command actually TARGETS, not
#   the hook's own cwd. In kit-only mode the session cwd is the kit while git
#   commands run in the target project, so resolving from $PWD would check the
#   wrong repository. Priority:
#     1. an explicit `git -C <dir>`;
#     2. the last `cd <dir>` in the command;
#     3. the hook payload's own "cwd";
#     4. $PWD.
#   Returns non-zero (prints nothing) when the target is not a git repository.
target_repo() {
  local input="$1" dir
  dir="$(printf '%s' "$input" | grep -oE 'git[[:space:]]+-C[[:space:]]+[^[:space:]"]+' | head -n1 | sed -E 's/^git[[:space:]]+-C[[:space:]]+//')"
  if [ -z "$dir" ]; then
    dir="$(printf '%s' "$input" | grep -oE '(^|[;&|"[:space:]])cd[[:space:]]+[^[:space:]"&;|]+' | tail -n1 | sed -E 's/.*cd[[:space:]]+//')"
  fi
  if [ -z "$dir" ]; then
    dir="$(printf '%s' "$input" | sed -nE 's/.*"cwd"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p' | head -n1)"
  fi
  [ -z "$dir" ] && dir="$PWD"
  case "$dir" in "~"|"~/"*) dir="$HOME${dir#\~}" ;; esac
  git -C "$dir" rev-parse --show-toplevel 2>/dev/null
}

# is_git_cmd "<hook stdin JSON>" "<subcommand regex>"
#   True when the command runs one of the given git subcommands, including the
#   forms with global options before it (`git -C <dir> commit`, `git -c k=v add`).
is_git_cmd() {
  printf '%s' "$1" | grep -qE "(^|[[:space:];&|(\"])git[[:space:]]+((-C|-c)[[:space:]]+[^[:space:]\"]+[[:space:]]+|--[a-z-]+=[^[:space:]\"]+[[:space:]]+)*($2)([[:space:]\"]|\$)"
}
