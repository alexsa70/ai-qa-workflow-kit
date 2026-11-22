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

- A skill's `skills/<name>/agents/claude.yaml` and `openai.yaml` describe the
  same skill and must stay consistent.
- `.claude/agents/qa-review-gate.md` is the Claude runtime launch of
  `agents/qa-review-gate.md`: a thin, read-only (`Read`, `Grep`, `Glob`)
  subagent wrapper that loads the role file and runs it in a separate context.
  When the orchestrator routes to `qa-review-gate`, dispatch it with the Agent
  tool (`subagent_type: qa-review-gate`) and pass the artifact, pending
  transition, lens, authority order, and approved contract or scope. The role
  file stays the single source of truth; do not copy its rules into the wrapper.
- `.claude/agents/qa-blackbox-reviewer.md` launches the `blackbox-review` skill
  the same way, in a fresh read-only context that has not seen product code.
  Dispatch it (`subagent_type: qa-blackbox-reviewer`) whenever the work routes
  to `blackbox-review`; pass the mode, requirement, inventory path, case files,
  heuristics files and the target's context path, never code paths.
- When a request targets another repository, that repository's own `CLAUDE.md`
  and `AGENTS.md` should point here and to its `ai-workflow/project-context.md`.
