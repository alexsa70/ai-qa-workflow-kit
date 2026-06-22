# Kit-Only Mode

Run Claude or Codex so that governance is the **AI QA Workflow Kit orchestrator
only** — the target repository's own `CLAUDE.md` / `AGENTS.md` / installed
skills and agents are ignored. The kit is the active project; the target repo is
treated as data, with facts read from its `ai-workflow/project-context.md`.

The rule that makes this work: governance is decided by **where you launch and
what you connect**, not by a flag. Launch with the kit as the active project and
treat the target repo as a folder you operate on.

## Launcher (CLI)

`bin/qa-kit` launches Claude or Codex from the kit directory with the kit-only
governance prompt injected as the first message.

```bash
qa-kit                                 # api-tests, claude (defaults)
qa-kit ~/workspace/QA/e2e-ui-tests     # e2e suite, claude
qa-kit ~/workspace/QA/api-tests codex  # api-tests, codex
```

Add an alias once (zsh — adjust path if the kit lives elsewhere):

```bash
echo "alias qa-kit='$HOME/workspace/ai-qa-workflow-kit/bin/qa-kit'" >> ~/.zshrc
source ~/.zshrc
```

Defaults can also be set via env: `QA_KIT_TARGET`, `QA_KIT_TOOL`.

## Cowork (desktop)

You cannot pass CLI args, so:

1. Start a new session. Connect **only** `ai-qa-workflow-kit` (active project)
   and `QA/api-tests` (file access). Do **not** connect the `QA` root — that
   injects the heavy `QA/CLAUDE.md`.
2. Paste the governance prompt below as the first message.

## Governance Prompt (copy-paste)

```text
Режим kit-only. Governance — строго AI QA Workflow Kit:
- Единая точка входа: <KIT_DIR>/agents/qa-orchestrator.md.
- Target project: <TARGET_PATH>.
- Факты проекта бери ТОЛЬКО из <TARGET_PATH>/ai-workflow/project-context.md.
- Используй ТОЛЬКО скиллы kit (source-of-truth, test-design, test-implementation,
  bug-fixing, code-review, api-layered-architecture, testmo-csv).
- Игнорируй правила и инструменты самого проекта: его CLAUDE.md, AGENTS.md,
  .claude/skills, .claude/agents и корневой QA/CLAUDE.md.
- Помни authority order из project-context: backend-код выше runtime; для
  негативных/permission-ассертов решай по гарду в коде, не по успешному ответу.
Подтверди режим одной строкой и жди задачу.
```

Replace `<KIT_DIR>` with the kit path and `<TARGET_PATH>` with the target repo
(e.g. `/Users/alexanderle/workspace/QA/api-tests`).

## Notes

- `ai-workflow/project-context.md` is **facts** (paths, commands, authority
  order), not target-repo *rules* — keep it; without it the kit has no project
  structure. For zero target influence, omit it and supply paths/commands by
  hand.
- Kit skills are files read via the orchestrator, not installed slash skills, so
  "use only kit skills" means: follow the orchestrator and the SKILL.md files,
  ignore the target repo's installed `/...` skills.
- Verify the mode held: the agent should name `qa-orchestrator.md` and the
  target's `ai-workflow/project-context.md`, and should not cite `QA/CLAUDE.md`
  or project `/skills`.
