# AI QA Workflow Kit Instructions

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
