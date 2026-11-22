# Kit Hooks

Reusable, project-agnostic Claude Code hooks for QA repositories. Each is a
`PreToolUse` hook matched on the `Bash` tool: it reads the tool call from stdin,
inspects the command, and either stays silent, injects advisory context, or
blocks the action.

| Hook | Fires on | Effect |
|---|---|---|
| `pre-commit-branch-guard.sh` | `git commit` | **Blocks** (exit 2) a commit on a protected branch (`main`/`master`); warns which branch a commit is landing on otherwise. Explicit escape hatch: prefix with `ALLOW_MAIN_COMMIT=1` to warn-and-allow an intentional direct-to-main commit. |
| `skill-size-check.sh` | `git commit` | **Blocks** (exit 2) when a staged parent `SKILL.md` exceeds the line cap (default 200); hint to split into sub-skills. |
| `branch-needs-worktree.sh` | `git checkout -b/-B`, `git switch -c/-C/--create`, `git branch <name>` | **Blocks** (exit 2) creating a branch in place; points at `bin/qa-worktree <target-path> <branch> [base]`. Listing, deleting, renaming and `git worktree add -b` pass. |
| `pre-commit-check.sh` | `git commit`, `git add` | Advisory only. Warns on bulk `git add -A/./--all` with many untracked files, and on very large staged diffs that likely contain generated artifacts. |

None of the hooks depend on external tooling — plain `git` + POSIX shell
(`branch-needs-worktree.sh` uses `python3` to read the command when available).
Each hook resolves the repository the command TARGETS through
`lib/target-repo.sh`: an explicit `git -C <dir>`, else the last `cd <dir>`, else
the payload cwd. In kit-only mode the session cwd is the kit while git commands
run in the target project, so the checks apply to the target, not the kit.

## Configuration

Each hook reads optional environment variables; defaults match common QA
conventions.

| Variable | Hook | Default |
|---|---|---|
| `PROTECTED_BRANCHES` | branch-guard | `main master` |
| `SKILL_LINE_CAP` | skill-size-check | `200` |
| `BULK_ADD_THRESHOLD` | pre-commit-check | `20` |
| `LARGE_DIFF_LINES` | pre-commit-check | `5000` |
| `ARTIFACT_PATTERN` | pre-commit-check | `allure-results/\|reports/\|outputs/\|\.html$\|report\.` |

## Wiring

In the kit itself the hooks are already wired in `.claude/settings.json`
(paths via `$CLAUDE_PROJECT_DIR`), so every session started in the kit — including
`bin/qa-kit` — runs them on any machine after a clone. For another repository
they are opt-in: add them to its `.claude/settings.json`, pointing at the kit's
absolute path. Make the
scripts executable first:

```bash
chmod +x /absolute/path/to/ai-qa-workflow-kit/hooks/*.sh
```

Then merge into `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "bash /absolute/path/to/ai-qa-workflow-kit/hooks/pre-commit-branch-guard.sh" },
          { "type": "command", "command": "bash /absolute/path/to/ai-qa-workflow-kit/hooks/branch-needs-worktree.sh" },
          { "type": "command", "command": "bash /absolute/path/to/ai-qa-workflow-kit/hooks/skill-size-check.sh" },
          { "type": "command", "command": "bash /absolute/path/to/ai-qa-workflow-kit/hooks/pre-commit-check.sh 2>/dev/null || true" }
        ]
      }
    ]
  }
}
```

The blocking hooks (`branch-guard`, `branch-needs-worktree`, `skill-size-check`) run without a
`|| true` guard so their exit code 2 reaches Claude Code. The advisory hook is
guarded so a transient error never blocks a commit.

To override a default in one project, set the env var on the command, e.g.:

```json
{ "type": "command", "command": "SKILL_LINE_CAP=300 bash /absolute/path/to/ai-qa-workflow-kit/hooks/skill-size-check.sh" }
```

## Escape hatch: intentional direct-to-main commit

`pre-commit-branch-guard.sh` hard-blocks a commit on a protected branch by
default. For an intentional small change that belongs directly on `main` (a typo
fix, a doc tweak — not test code), prefix the commit with the override flag:

```bash
ALLOW_MAIN_COMMIT=1 git commit -m "docs: fix typo"
```

The hook then emits a warning and allows the commit instead of blocking it. Add
this flag only when a direct-to-main commit is deliberately authorized — it is
per-command and never implicit, so an accidental commit to a protected branch is
still blocked.
