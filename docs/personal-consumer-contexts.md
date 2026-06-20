# Personal Consumer Contexts For Shared Repositories

## Purpose

Use this approach when a target repository is shared with a team and the
`ai-qa-workflow-kit` should remain a personal workflow layer.

Do not commit kit-specific workflow files into shared repositories unless the
team explicitly agrees to adopt the kit.

## Rule

For shared repositories such as:

```text
/Users/alex/MyRepos/work/qa/api-tests
/Users/alex/MyRepos/work/qa/e2e-ui-tests
```

do not:

- replace the shared `AGENTS.md`;
- replace the shared `CLAUDE.md`;
- commit `ai-workflow/project-context.md`;
- commit kit-specific instructions into the shared repository.

Instead, keep personal consumer contexts outside the shared repositories.

## Recommended Local Layout

Create a private/local adapter repository or folder:

```text
/Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers/
  api-tests/
    project-context.md
  e2e-ui-tests/
    project-context.md
```

This folder can be a private Git repository if the contexts should be synced
between machines.

The workflow kit remains here:

```text
/Users/alex/MyRepos/work/ai-qa-workflow-kit
```

The target projects remain unchanged:

```text
/Users/alex/MyRepos/work/qa/api-tests
/Users/alex/MyRepos/work/qa/e2e-ui-tests
```

## Codex Or Claude Startup Prompt

Use a prompt like this when working in a shared target project:

```text
Target project:
/Users/alex/MyRepos/work/qa/api-tests

Use workflow kit:
/Users/alex/MyRepos/work/ai-qa-workflow-kit

Use local project context:
/Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers/api-tests/project-context.md

Do not use or modify the target project's AGENTS.md or CLAUDE.md as workflow
authority. Treat those files only as legacy reference unless the local project
context explicitly promotes a rule from them.

Do not commit ai-workflow/ or kit-specific instructions into the shared target
repository.
```

For E2E:

```text
Target project:
/Users/alex/MyRepos/work/qa/e2e-ui-tests

Use workflow kit:
/Users/alex/MyRepos/work/ai-qa-workflow-kit

Use local project context:
/Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers/e2e-ui-tests/project-context.md

Do not use or modify the target project's AGENTS.md or CLAUDE.md as workflow
authority. Treat those files only as legacy reference unless the local project
context explicitly promotes a rule from them.

Do not commit ai-workflow/ or kit-specific instructions into the shared target
repository.
```

## Local Project Context Policy

The personal `project-context.md` is the adapter between the reusable kit and
the shared target project.

It should contain:

- target project path;
- stack and commands;
- source registry;
- source-of-truth hierarchy;
- API layered architecture map;
- allowed edit paths;
- verification policy;
- legacy instruction handling;
- rules that are trusted;
- rules that are legacy assumptions only.

For `api-tests`, start from this stance:

```text
Legacy project instructions may contain unverified assumptions derived from
Testmo. They are reference material only, not controlling source-of-truth.

Four-layer API architecture is trusted and should be preserved.

Working contract tests are trusted as implementation examples, but they do not
define product behavior by themselves.

Testmo is requirement/design input only, not product authority.

Destructive endpoint and Keycloak/admin identity rules are legacy safety
hypotheses unless confirmed by source-of-truth.
```

## Why This Is The Best Balance

This keeps the kit personal while still usable in real shared repositories:

- no shared repository workflow churn;
- no accidental adoption by teammates;
- no conflict with existing team instructions;
- no kit-specific files committed into team projects;
- same workflow can be used from Codex and Claude;
- personal adapters can be versioned privately;
- legacy rules can be selectively promoted into trusted project context only
  after review.

## Work-Machine Setup Checklist

On the work machine:

1. Clone or pull the personal workflow kit:

   ```bash
   cd /Users/alex/MyRepos/work
   git clone git@github.com:alexsa70/ai-qa-workflow-kit.git
   ```

   If it already exists:

   ```bash
   cd /Users/alex/MyRepos/work/ai-qa-workflow-kit
   git pull --ff-only origin main
   ```

2. Create the personal consumer-context folder:

   ```bash
   mkdir -p /Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers/api-tests
   mkdir -p /Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers/e2e-ui-tests
   ```

3. Copy the template:

   ```bash
   cp /Users/alex/MyRepos/work/ai-qa-workflow-kit/templates/project-context.md \
     /Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers/api-tests/project-context.md

   cp /Users/alex/MyRepos/work/ai-qa-workflow-kit/templates/project-context.md \
     /Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers/e2e-ui-tests/project-context.md
   ```

4. Fill each context with personal adapter rules.

5. Do not add these contexts to the shared target repositories.

6. Optional: initialize a private Git repository for the consumer contexts:

   ```bash
   cd /Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers
   git init
   git add .
   git commit -m "chore: add personal consumer contexts"
   ```

7. Use the startup prompt from this document when beginning a Codex or Claude
   session for a shared target project.
