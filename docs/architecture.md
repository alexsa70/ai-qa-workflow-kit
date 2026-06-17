# Architecture

## Components

### Agent

Owns a task, makes decisions, chooses procedures, enforces gates, and reports
the result. An agent describes responsibility, not a shell command or a prompt
alias.

The QA Orchestrator is the single entry agent. It owns routing and workflow
state, but detailed repeatable procedures belong in skills.

### Skill

Defines a repeatable procedure used by one or more agents. Skills may include
scripts, references, or templates. Agents decide when a skill is needed.

### Artifact

Stores a durable result that another role can inspect or consume. Examples
include an API contract, approved test design, review report, and verification
result.

### Gate

Defines a condition that must be satisfied before the workflow advances.
Examples include confirmed API behavior, approved test cases, and successful
verification.

### Project Context

Contains facts that vary between repositories: paths, commands, frameworks,
source repositories, markers, environment rules, and local policies.

## Dependency Direction

```text
User request
    |
    v
QA Orchestrator
    |
    +--> reads project context
    |
    +--> works directly or selects an agent or skill
    |
    +--> requires an artifact
    |
    +--> evaluates a gate
    |
    v
Verified result
```

Reusable components may read project context, but they must not embed
project-specific facts.

## Orchestration Boundary

The Orchestrator answers:

- What is the current objective?
- What is known or unknown?
- What capability should act next?
- Which gate protects the transition?
- What evidence is required to finish?

A skill answers:

- What exact repeatable procedure should be followed?
- Which tools and references are needed?
- What artifact does the procedure produce?

A specialist agent answers:

- What independent judgement is required for this domain?
- Is the produced artifact acceptable?

This separation keeps the Orchestrator small while allowing workflows to grow
without turning it into a collection of unrelated procedures.

## Growth Rule

Add a new component only when a real workflow needs it:

- add an agent for distinct decision ownership;
- add a skill for a repeated procedure;
- add an artifact when a result must survive the current conversation;
- add a gate when proceeding without evidence creates meaningful risk.
