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

## Consumer Setup In 5 Minutes

Use this when connecting a new repository to the workflow kit.

1. From the target repository, create the workflow folder:

   ```bash
   mkdir -p ai-workflow
   cp /absolute/path/to/ai-qa-workflow-kit/templates/project-context.md \
     ai-workflow/project-context.md
   ```

2. Fill `ai-workflow/project-context.md` with target-project facts only:

   - repository root and project purpose;
   - technology stack and verification commands;
   - source registry and freshness/update policy;
   - authority order for API contract, expected behavior, permissions, and
     runtime behavior;
   - allowed paths for tests, clients, schemas, assertions, fixtures, and
     artifacts;
   - autonomous QA execution policy and cases that still require separate
     approval.

3. Add or update the target project's `AGENTS.md`:

   ```markdown
   Before working in this project:

   1. Read `/absolute/path/to/ai-qa-workflow-kit/agents/qa-orchestrator.md`.
   2. Read `ai-workflow/project-context.md`.
   3. Use workflow skills listed under `Available Roles And Skills` in the
      project context.
   4. Treat this repository as the target project.
   5. Keep generated project artifacts inside this repository.
   ```

4. Create the local artifact root if the project will use test design:

   ```bash
   mkdir -p test-design
   ```

5. Run a smoke prompt from the target repository:

   ```text
   Назови активный Orchestrator, путь к project context и доступный
   source-of-truth, не выполняя исследование.
   ```

Expected result: the answer names the reusable QA Orchestrator, the local
`ai-workflow/project-context.md`, and the configured `source-of-truth` skill or
states that source-of-truth is not configured yet.

## Ready Prompts

Run these prompts from a connected target repository.

### Connection Smoke Check

```text
Назови активный Orchestrator, путь к project context и доступный
source-of-truth, не выполняя исследование.
```

Use this to confirm that the target repository is connected to the reusable
workflow kit.

### Source-Of-Truth Verdict

```text
Используй source-of-truth и определи, является ли <claim> верным для этого
проекта. Укажи status, confidence, controlling source, точные пути к
доказательствам, freshness, contradictions и next permitted transition.
Не изменяй файлы и не запускай тесты.
```

Use this when endpoint behavior, permissions, payloads, response contracts, or
project policy are unclear.

### Test Design Contract

```text
Используй test-design для <feature-or-endpoint>. Создай или обнови
test-design/<area>/<contract-name>.md со статусом awaiting-approval.
Покрой actor-target матрицу, response contract, side effects и cleanup.
Не реализуй тесты и не запускай их.
```

Use this before automation when the coverage, assertions, or cleanup must be
made durable.

### Approval

```text
Одобряю <TC IDs> со всеми вариантами, перечисленными в
test-design/<area>/<contract-name>.md. Зафиксируй approval record.
```

Use this as the single approval gate before implementation. After approval,
`test-implementation` may implement the exact variants and run their
project-authorized QA verification without another approval request.

### Implementation And QA Verification

```text
Используй test-implementation для реализации
test-design/<area>/<contract-name>.md. Не изменяй Approval record.
```

Use this after approval. The expected flow is: scope lock, implementation,
static checks, collection, exact approved QA execution when project context
allows it, cleanup, and contract update.

### Resume Pending Live Verification

```text
Используй test-implementation для продолжения pending live verification в
test-design/<area>/<contract-name>.md. Запускай только утверждённые варианты,
зафиксируй runtime result и cleanup. Не изменяй Approval record.
```

Use this when tests are already implemented but live execution was previously
pending or blocked by environment availability.

### Review Implemented Tests

```text
Проведи code review реализации для test-design/<area>/<contract-name>.md.
Проверь соответствие approved variants, response assertions, cleanup,
traceability и verification evidence. Findings first.
```

Use this after implementation or live execution to check for framework and
contract drift.
