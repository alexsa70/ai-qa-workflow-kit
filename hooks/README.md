# Kit Hooks

Reusable, project-agnostic Claude Code hooks for QA repositories. Each is a
`PreToolUse` hook matched on the `Bash` tool: it reads the tool call from stdin,
inspects the command, and either stays silent, injects advisory context, or
blocks the action.

| Hook | Fires on | Effect |
|---|---|---|
| `pre-commit-branch-guard.sh` | `git commit` | **Blocks** (exit 2) a commit on a protected branch (`main`/`master`); warns which branch a commit is landing on otherwise. |
| `skill-size-check.sh` | `git commit` | **Blocks** (exit 2) when a staged parent `SKILL.md` exceeds the line cap (default 200); hint to split into sub-skills. |
| `pre-commit-check.sh` | `git commit`, `git add` | Advisory only. Warns on bulk `git add -A/./--all` with many untracked files, and on very large staged diffs that likely contain generated artifacts. |

None of the hooks depend on external tooling — plain `git` + POSIX shell. All
paths resolve from `git rev-parse --show-toplevel`, so the same scripts work in
the kit's own repo and in any connected project.

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

Hooks are opt-in. Add them to a `.claude/settings.json` — either in the kit
repo, or in a connected project pointing at the kit's absolute path. Make the
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
          { "type": "command", "command": "bash /absolute/path/to/ai-qa-workflow-kit/hooks/skill-size-check.sh" },
          { "type": "command", "command": "bash /absolute/path/to/ai-qa-workflow-kit/hooks/pre-commit-check.sh 2>/dev/null || true" }
        ]
      }
    ]
  }
}
```

The two blocking hooks (`branch-guard`, `skill-size-check`) run without a
`|| true` guard so their exit code 2 reaches Claude Code. The advisory hook is
guarded so a transient error never blocks a commit.

To override a default in one project, set the env var on the command, e.g.:

```json
{ "type": "command", "command": "SKILL_LINE_CAP=300 bash /absolute/path/to/ai-qa-workflow-kit/hooks/skill-size-check.sh" }
```
