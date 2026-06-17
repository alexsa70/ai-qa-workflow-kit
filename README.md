# AI QA Workflow Kit

A reusable workflow layer for AI-assisted QA engineering.

The kit separates:

- agents: who owns decisions and work;
- skills: how repeatable procedures are performed;
- artifacts: what durable result a task produces;
- gates: what must be true before work can continue;
- project context: repository-specific paths, commands, and rules.

## First Version

This version contains the reusable QA Orchestrator and the `source-of-truth`,
`test-design`, and `test-implementation` skills. The approved Test Design
Contract remains the durable artifact across design, implementation, and
verification.

```text
ai-qa-workflow-kit/
├── AGENTS.md
├── README.md
├── agents/
│   └── qa-orchestrator.md
├── skills/
│   ├── source-of-truth/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       └── assets/
│           └── source-verdict.md
│   ├── test-design/
│       ├── SKILL.md
│       └── agents/
│           └── openai.yaml
│   └── test-implementation/
│       ├── SKILL.md
│       └── agents/
│           └── openai.yaml
├── docs/
│   ├── architecture.md
│   ├── component-inventory.md
│   ├── test-design-contract.md
│   └── test-implementation.md
└── templates/
    ├── project-context.md
    └── test-design-contract.md
```

## Design Documents

- `docs/architecture.md` defines the component boundaries.
- `docs/component-inventory.md` records existing agents, skills, artifacts, and
  migration decisions discovered across local QA repositories.
- `docs/test-design-contract.md` defines the lifecycle and gates for the first
  reusable workflow artifact.
- `docs/test-implementation.md` defines scope lock, traceability, and layered
  verification for implementation.

## How A Project Connects

1. Copy `templates/project-context.md` into the target project.
2. Fill in only facts that belong to that project.
3. Point the target project's `AGENTS.md` to this kit and its project context.
4. Start every request through the QA Orchestrator.

The project context is configuration. The reusable agent remains independent
from any one repository.
