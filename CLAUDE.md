# AI QA Workflow Kit Instructions

This file is the Claude entry point for the kit. It is the platform twin of
`AGENTS.md` (the Codex / OpenAI entry point); both point at the same reusable
QA Orchestrator and must stay in agreement.

Use the QA Orchestrator as the single entry point for work in this repository.

Before analyzing a request, editing files, or running commands:

1. Read `agents/qa-orchestrator.md`.
2. Follow its classification, prerequisite, gate, and verification workflow.
3. Read the connected project's context file when the task targets another
   repository.

Files under `agents/` define roles and decision authority. They do not become
independent runtime agents unless the active AI platform explicitly launches
them.

Project-specific paths, commands, technologies, and policies must not be added
to reusable agent definitions. Keep them in a project context file based on
`templates/project-context.md`.

## Shared Memory

Use the shared AI memory vault at
`/Users/alexanderle/Library/CloudStorage/GoogleDrive-alexsa70@gmail.com/My Drive/My_WIKI/API_Memory`
as the long-term memory for work on this kit itself. At session start, Claude
Code hooks inject the vault index and recent daily log automatically.
Important decisions, lessons, and follow-up items about the kit's own agents,
skills, and orchestrator behavior (as opposed to any connected target project)
should be captured into that vault by the configured hooks.

## Platform Notes

- Skills live under `skills/<name>/SKILL.md`. The `name` and `description`
  frontmatter is the shared, platform-neutral definition Claude reads to decide
  when to invoke a skill.
- Each skill carries platform launch metadata under `skills/<name>/agents/`:
  `claude.yaml` for Claude, `openai.yaml` for Codex / OpenAI. The two files
  describe the same skill and must stay consistent.
- Reusable specialist agents live under `agents/` alongside the orchestrator
  (currently `qa-review-gate`, an adversarial PASS|EDIT|FAIL review gate). Like
  the orchestrator, they carry no project-specific paths, commands, or services.
- `hooks/` ships opt-in, project-agnostic Claude Code `PreToolUse` hooks. They
  are inert until wired into a `.claude/settings.json`; see `hooks/README.md`.
- When a request targets another repository, that repository's own `CLAUDE.md`
  and `AGENTS.md` should point here and to its `ai-workflow/project-context.md`.
