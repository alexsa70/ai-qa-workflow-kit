# Coverage Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add four project-agnostic kit skills (`coverage-backlog`, `requirement-grill`, `blackbox-review`, `night-shift`) and a `bin/qa-night` launcher that sit above a project's authoring skill, as designed in `docs/superpowers/specs/2026-10-23-coverage-pipeline-design.md`.

**Architecture:** Skills are Markdown procedures (`skills/<name>/SKILL.md` + `agents/claude.yaml` + `agents/openai.yaml`) routed by `agents/qa-orchestrator.md`. Every project fact comes from a new "Coverage Pipeline" section of the target's `ai-workflow/project-context.md`. The only executable code is two small Python helpers under `bin/lib/` (config reader, PR selector) and the Bash launcher `bin/qa-night`.

**Tech Stack:** Markdown, Python 3.11 stdlib (`unittest`, `argparse`, `json`), Bash 3.2-compatible (macOS), `gh` CLI, `git worktree`, `claude -p`.

## Global Constraints

- Kit files carry no project-specific names: the test deny-list is `kal sense`, `kal-sense`, `kaleidoo`, `it-dgx`, `catalog/`, `route_coverage`, `catalog-test`, `testmo project 5` (case-insensitive) over `skills/`, `agents/`, `templates/`.
- Every new pipeline `SKILL.md` is at most 200 lines (matches `hooks/skill-size-check.sh` default cap).
- `display_name` and `short_description` are identical in `claude.yaml` and `openai.yaml`; both contain the skill name.
- Every skill directory is listed in `README.md` (`<name>/`), `bin/qa-kit` and `docs/kit-only-mode.md` (enforced by existing tests).
- Nothing is committed to any target repository. Consumer drafts go to `/Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers/qa/` (outside the kit's git).
- The night shift never: merges, runs `gh pr ready`, records approval, force-pushes, pushes to the default branch, uses `bypassPermissions`, publishes to a non-sandbox target.
- Run the full suite with `python3 -m unittest discover -s tests -v` (same as CI).
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Spec amendment carried by this plan

The spec (§4.4, §7) says `bin/qa-night` verifies that the ready label was applied by a human. The night shift's `gh` runs under the user's own account, so a login check cannot tell the user from the night shift. Task 8 replaces it with: the last `labeled` event for the ready label is not from a bot or the configured `night.actor_login`, the PR has neither the done nor the blocked label, and no comment carrying `night-shift run ` is newer than that label event. The night shift is also forbidden to add the ready label. Task 8 edits the spec accordingly.

## File Structure

| Path | Responsibility | Task |
|---|---|---|
| `templates/project-context.md` | + "Coverage Pipeline" section (all keys) | 1 |
| `bin/lib/pipeline_config.py` | read one key from that section | 1 |
| `tests/test_coverage_pipeline.py` | all new kit tests | 1–8 |
| `skills/coverage-backlog/{SKILL.md,agents/*.yaml}` | computed backlog board | 2 |
| `agents/qa-orchestrator.md` | task type + 4 routing rules | 2,3,4,6 |
| `README.md`, `bin/qa-kit`, `docs/kit-only-mode.md` | list skills; authoring-skill exception | 2,3,4,6 |
| `skills/requirement-grill/{SKILL.md,agents/*.yaml,assets/grill-brief.md}` | alignment interview → grill brief | 3 |
| `skills/blackbox-review/{SKILL.md,agents/*.yaml,assets/findings.md,references/heuristics.md}` | black-box findings | 4 |
| `templates/project-heuristics.md` | project heuristics template | 4 |
| consumer dir `qa/heuristics.md`, `qa/heuristics-mining.md` | product heuristics draft, mining notes (not in kit git) | 5 |
| `skills/night-shift/{SKILL.md,agents/*.yaml,assets/night-prompt.md}` | AFK procedure + headless prompt | 6 |
| `bin/lib/select_ready_prs.py` | choose eligible PRs | 7 |
| `bin/qa-night` | launcher loop | 8 |
| consumer dir `qa/coverage-pipeline-section.md` | filled section for the qa repo | 9 |
| `docs/component-inventory.md` | record the four components | 9 |

---

### Task 1: Coverage Pipeline configuration

**Files:**
- Modify: `templates/project-context.md` (insert before `## Known Constraints`)
- Create: `bin/lib/pipeline_config.py`
- Create: `tests/test_coverage_pipeline.py`

**Interfaces:**
- Produces: `read_pipeline_config(text: str) -> dict[str, str]`; CLI `python3 bin/lib/pipeline_config.py --context <path> --key <key>` → prints value, exit 0; exit 2 context missing; exit 3 key missing or empty (stderr `pipeline_config: missing context key: <key>`).
- Produces: `PIPELINE_KEYS` list in the test module (reused by later tasks in the same file).

- [ ] **Step 1: Write the failing tests**

Create `tests/test_coverage_pipeline.py`:

```python
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PIPELINE_KEYS = [
    "coverage.uncovered_command",
    "coverage.detail_command",
    "coverage.day_batch_size",
    "requirements.source",
    "requirements.inventory_paths",
    "backend.checkout",
    "authoring.skill",
    "authoring.after_checkpoint_phases",
    "checks.safe",
    "checks.preflight",
    "run.live_sandbox",
    "review.command",
    "labels.ready",
    "labels.done",
    "labels.blocked",
    "night.permission_mode",
    "night.allowed_tools",
    "night.max_turns",
    "night.timeout_minutes",
    "night.actor_login",
    "heuristics.project_file",
]

PROJECT_TERMS = [
    "kal sense",
    "kal-sense",
    "kaleidoo",
    "it-dgx",
    "catalog/",
    "route_coverage",
    "catalog-test",
    "testmo project 5",
]


def load_module(relative_path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PipelineConfigTests(unittest.TestCase):
    def test_template_declares_every_pipeline_key(self):
        config = load_module("bin/lib/pipeline_config.py", "pipeline_config")
        text = (ROOT / "templates" / "project-context.md").read_text(encoding="utf-8")
        self.assertIn("## Coverage Pipeline", text)
        values = config.read_pipeline_config(text)
        for key in PIPELINE_KEYS:
            self.assertIn(key, values, key)

    def test_reader_ignores_other_sections(self):
        config = load_module("bin/lib/pipeline_config.py", "pipeline_config")
        text = (
            "## Paths\n\n- labels.ready: wrong\n\n"
            "## Coverage Pipeline\n\n- labels.ready: afk-ready\n"
            "- night.allowed_tools: Bash(git push origin HEAD:*),Read\n\n"
            "## Known Constraints\n\n- labels.done: wrong\n"
        )
        values = config.read_pipeline_config(text)
        self.assertEqual(values["labels.ready"], "afk-ready")
        self.assertEqual(values["night.allowed_tools"], "Bash(git push origin HEAD:*),Read")
        self.assertNotIn("labels.done", values)

    def test_cli_reports_missing_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            context = Path(tmp) / "project-context.md"
            context.write_text("## Coverage Pipeline\n\n- labels.ready:\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "bin/lib/pipeline_config.py"),
                 "--context", str(context), "--key", "labels.ready"],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 3)
        self.assertIn("missing context key: labels.ready", result.stderr)

    def test_cli_help(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "bin/lib/pipeline_config.py"), "--help"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout.lower())


class ProjectAgnosticTests(unittest.TestCase):
    def test_kit_skills_agents_and_templates_name_no_project(self):
        for folder in ("skills", "agents", "templates"):
            for path in (ROOT / folder).rglob("*"):
                if not path.is_file() or path.suffix not in {".md", ".yaml", ".json", ".py"}:
                    continue
                text = path.read_text(encoding="utf-8").lower()
                for term in PROJECT_TERMS:
                    self.assertNotIn(term, text, f"{path.relative_to(ROOT)} names '{term}'")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_coverage_pipeline -v`
Expected: `PipelineConfigTests` ERROR/FAIL (`bin/lib/pipeline_config.py` not found); `ProjectAgnosticTests` PASS.

- [ ] **Step 3: Add the template section**

In `templates/project-context.md`, insert this block immediately before the line `## Known Constraints`:

```markdown
## Coverage Pipeline

Read by `coverage-backlog`, `requirement-grill`, `blackbox-review`,
`night-shift` and `bin/qa-night`. One `- key: value` per line. A value is a
command, a path, a name or free text the skill reads literally. A skill stops
with a `missing context` blocker when a key it needs is empty.

- coverage.uncovered_command:
- coverage.detail_command:
- coverage.day_batch_size: 3
- requirements.source:
- requirements.inventory_paths:
- backend.checkout:
- authoring.skill:
- authoring.after_checkpoint_phases:
- checks.safe:
- checks.preflight:
- run.live_sandbox:
- review.command:
- labels.ready: afk-ready
- labels.done: afk-done
- labels.blocked: afk-blocked
- night.permission_mode: acceptEdits
- night.allowed_tools:
- night.max_turns: 200
- night.timeout_minutes: 120
- night.actor_login:
- heuristics.project_file:

```

- [ ] **Step 4: Write the reader**

Create `bin/lib/pipeline_config.py`:

```python
#!/usr/bin/env python3
"""Read one key from the "Coverage Pipeline" section of a project context file.

    python3 bin/lib/pipeline_config.py --context <target>/ai-workflow/project-context.md --key labels.ready

Exit 0 prints the value; exit 2 when the context file is missing; exit 3 when
the key is missing or empty.
"""
import argparse
import sys
from pathlib import Path

SECTION = "## Coverage Pipeline"


def read_pipeline_config(text):
    values = {}
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == SECTION
            continue
        if inside and line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            values[key.strip()] = value.strip()
    return values


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read one Coverage Pipeline key from a project context file.")
    parser.add_argument("--context", required=True, type=Path, help="path to project-context.md")
    parser.add_argument("--key", required=True, help="key such as labels.ready")
    args = parser.parse_args(argv)
    if not args.context.is_file():
        print(f"pipeline_config: context not found: {args.context}", file=sys.stderr)
        return 2
    value = read_pipeline_config(args.context.read_text(encoding="utf-8")).get(args.key, "")
    if not value:
        print(f"pipeline_config: missing context key: {args.key}", file=sys.stderr)
        return 3
    print(value)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Then `chmod +x bin/lib/pipeline_config.py`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v`
Expected: all PASS (existing 9 + new 5).

- [ ] **Step 6: Commit**

```bash
git add templates/project-context.md bin/lib/pipeline_config.py tests/test_coverage_pipeline.py
git commit -m "feat(pipeline): add Coverage Pipeline context section and reader

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: `coverage-backlog` skill, orchestrator wiring, authoring-skill exception

**Files:**
- Create: `skills/coverage-backlog/SKILL.md`, `skills/coverage-backlog/agents/claude.yaml`, `skills/coverage-backlog/agents/openai.yaml`
- Modify: `agents/qa-orchestrator.md`, `README.md`, `bin/qa-kit`, `docs/kit-only-mode.md`
- Test: `tests/test_coverage_pipeline.py`

**Interfaces:**
- Consumes: Coverage Pipeline keys `coverage.uncovered_command`, `coverage.detail_command`, `coverage.day_batch_size`, `requirements.inventory_paths` (Task 1).
- Produces: orchestrator task type `coverage-planning`; routing sentence form ``Use `<skill>` when:`` that later tasks repeat; `PIPELINE_SKILLS` list in tests.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_coverage_pipeline.py` (above `if __name__ == "__main__":`):

```python
PIPELINE_SKILLS = ["coverage-backlog"]


class PipelineSkillTests(unittest.TestCase):
    def test_pipeline_skills_exist_and_are_small(self):
        for name in PIPELINE_SKILLS:
            path = ROOT / "skills" / name / "SKILL.md"
            self.assertTrue(path.is_file(), name)
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertLessEqual(len(lines), 200, f"{name}: {len(lines)} lines")

    def test_orchestrator_routes_pipeline_skills(self):
        text = (ROOT / "agents" / "qa-orchestrator.md").read_text(encoding="utf-8")
        self.assertIn("`coverage-planning`", text)
        for name in PIPELINE_SKILLS:
            self.assertIn(f"Use `{name}` when:", text, name)

    def test_launchers_allow_the_project_authoring_skill(self):
        for relative in ("bin/qa-kit", "docs/kit-only-mode.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("authoring.skill", text, relative)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_coverage_pipeline -v`
Expected: the three new tests FAIL.

- [ ] **Step 3: Write `skills/coverage-backlog/SKILL.md`**

````markdown
---
name: coverage-backlog
description: Compute a prioritised coverage backlog that is never stored, from the project's coverage tool and its open pull requests, as a kanban board with blocking relationships and an AFK or HITL label per unit. Use when choosing what to cover next, planning a day of scenario work, checking which uncovered requirement units are free to claim, or turning outside-inventory findings into backlog units. Read-only - it never writes repository files, opens pull requests or claims units.
---

# Coverage Backlog

Turn "what is not covered yet" into "what to do next, in which order, and who
must be present". The board is recomputed on every run from live sources, so
it never drifts from the repository and never rots.

## Scope

Use this skill when:

- the user asks what to cover next, or plans a day shift of scenario work;
- uncovered requirement units must be checked against open claims;
- black-box `outside-inventory` findings must join the backlog.

Do not use it to design a case (`requirement-grill`, then the project's
authoring skill), to build an endpoint coverage workbook (`coverage-matrix`),
or to claim a unit (the authoring skill's claim step).

## Required Input

From the project context, section "Coverage Pipeline":

- `coverage.uncovered_command` - lists uncovered units, critical first;
- `coverage.detail_command` - coverage detail for named scenarios;
- `coverage.day_batch_size` - how many units to recommend (default 3);
- `requirements.inventory_paths` - where the requirement inventories live.

Also: the open pull requests of the target repository
(`gh pr list --state open --limit 200 --json number,title,body,headRefName,isDraft,labels,files`),
and any `outside-inventory` findings the user supplies or points to.

A missing key is a `missing context` blocker naming the key. Never substitute
a command of your own.

## Procedure

1. **Collect.** Run `coverage.uncovered_command` from the target root. Record
   the exact command and `git rev-parse --short HEAD`. It is read-only; if it
   needs network or credentials, stop and report.
2. **Exclude what is taken.** A unit is taken when the coverage tool reports a
   claim, or an open pull request names the unit id in its title, body or
   changed scenario files. A unit the tool reports as a twin of another
   domain's unit is excluded with the note "automate in <domain>".
3. **Tier.** P0: units the inventory marks critical. P1: other inventory
   units. P2: `outside-inventory` findings. Inside a tier, group by domain.
4. **Find blockers.** Read each candidate's inventory entry only far enough to
   name what must exist first:
   - `infra:driver` - a product call the test layer does not offer yet;
   - `infra:profile` - an organisation profile, capability or actor role;
   - `infra:fixture` - shared data or setup used by several units;
   - `<unit id>` - another unit whose scenario must exist first.
   Mark a blocker only when the inventory or the test layer shows it; never guess.
5. **Label AFK or HITL.**

   | AFK candidate - all must hold | HITL - any one is enough |
   |---|---|
   | the test layer already offers every product call | needs new infrastructure (`infra:*`) |
   | no consent flow, external account or manual step | needs an external account, consent or manual step |
   | cleanup can be proven by the product | destructive action on shared or standing data |
   | the requirement, inventory and code agree | requirement, inventory and code disagree |
   | an existing scenario shows the pattern | a new pattern for this domain |

   When unsure, label HITL. AFK here means "may be implemented by the night
   shift once a human has confirmed the cases", never "may skip confirmation".
6. **Group.** Units that share actor, preconditions and observable outcome
   become one suggested scenario with several cases.
7. **Recommend.** Pick `coverage.day_batch_size` units: highest tier first,
   unblocked, preferring units that unblock others.

## Output

```text
Backlog - <target> @ <short sha>, command: <exact command>
Counts: P0 <n> open / P1 <n> / P2 <n>; excluded: <n> claimed, <n> twins

| Unit | Tier | Domain | Blocked by | Label | Why | Suggested scenario |
|---|---|---|---|---|---|---|

Next <N> for the day shift:
1. <unit> - <one line why now>

Blockers to raise: <infra items with the units they hold back>
```

Write the board to chat. Write it to a file only when the user asks, and then
outside the repository (for example the session scratch directory).

## Rules

- Never write repository files, open or edit pull requests, add labels or
  claim units.
- The board is not a record. Re-run the skill instead of editing an old board.
- Never mark a P0 unit as done or skippable; a P0 unit that cannot be covered
  stays on the board with its blocker.
- Report the exact commands run; do not report coverage numbers you did not
  read from the tool.

## Completion

Report the command and commit, tier counts, the board, the recommendation and
the blockers. Next permitted action: `requirement-grill` on a recommended
unit, or the authoring skill directly for a unit the user already understands.
````

- [ ] **Step 4: Write the platform metadata**

`skills/coverage-backlog/agents/claude.yaml`:

```yaml
interface:
  display_name: "Coverage Backlog"
  short_description: "Compute the next coverage work as a kanban board"
  default_prompt: "Use the coverage-backlog skill to compute the uncovered units, exclude claimed ones, and recommend the next units with blockers and AFK or HITL labels."
```

`skills/coverage-backlog/agents/openai.yaml`:

```yaml
interface:
  display_name: "Coverage Backlog"
  short_description: "Compute the next coverage work as a kanban board"
  default_prompt: "Use $coverage-backlog to compute the uncovered units, exclude claimed ones, and recommend the next units with blockers and AFK or HITL labels."
```

- [ ] **Step 5: Wire the orchestrator**

In `agents/qa-orchestrator.md`, in `## Request Classification`, add after the `- \`ci-cd\`...` line:

```markdown
- `coverage-planning`: choose, align and schedule coverage work across
  requirement-inventory units;
```

Insert before `## Agent Routing`:

```markdown
Use `coverage-backlog` when:

- the user asks what to cover next or plans a day of scenario work;
- uncovered requirement units must be checked against open claims;
- `outside-inventory` findings must become backlog units.

`coverage-backlog` is read-only. It computes the board from the project's
coverage command and open pull requests on every run and never stores it,
claims a unit or opens a pull request.

```

- [ ] **Step 6: List the skill and add the authoring-skill exception**

`bin/qa-kit` and `docs/kit-only-mode.md` each contain the line
`  client-schema-sync, destructive-safety, testmo-csv).`
Replace it, in both files, with:

```text
  client-schema-sync, destructive-safety, testmo-csv, coverage-backlog).
- Исключение: authoring-скилл, указанный в project-context (ключ
  authoring.skill), разрешён, когда его вызывает скилл coverage pipeline.
```

`README.md`: in the skills tree, replace

```text
│   └── destructive-safety/
│       ├── SKILL.md
│       ├── agents/
│       │   ├── openai.yaml
│       │   └── claude.yaml
│       └── assets/
│           └── seeded-ids.template.json
```

with

```text
│   ├── destructive-safety/
│   │   ├── SKILL.md
│   │   ├── agents/
│   │   │   ├── openai.yaml
│   │   │   └── claude.yaml
│   │   └── assets/
│   │       └── seeded-ids.template.json
│   └── coverage-backlog/
│       ├── SKILL.md
│       └── agents/
│           ├── openai.yaml
│           └── claude.yaml
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v`
Expected: all PASS.

- [ ] **Step 8: Commit**

```bash
git add skills/coverage-backlog agents/qa-orchestrator.md README.md bin/qa-kit docs/kit-only-mode.md tests/test_coverage_pipeline.py
git commit -m "feat(skills): add coverage-backlog and coverage-planning routing

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: `requirement-grill` skill

**Files:**
- Create: `skills/requirement-grill/SKILL.md`, `skills/requirement-grill/agents/claude.yaml`, `skills/requirement-grill/agents/openai.yaml`, `skills/requirement-grill/assets/grill-brief.md`
- Modify: `agents/qa-orchestrator.md`, `README.md`, `bin/qa-kit`, `docs/kit-only-mode.md`, `tests/test_coverage_pipeline.py`

**Interfaces:**
- Consumes: keys `requirements.source`, `requirements.inventory_paths`, `backend.checkout`, `authoring.skill`.
- Produces: the grill brief format (`assets/grill-brief.md`) consumed by `blackbox-review` (Task 4) and the authoring skill.

- [ ] **Step 1: Extend the test list (failing)**

In `tests/test_coverage_pipeline.py` change `PIPELINE_SKILLS = ["coverage-backlog"]` to:

```python
PIPELINE_SKILLS = ["coverage-backlog", "requirement-grill"]
```

and append to `PipelineSkillTests`:

```python
    def test_grill_brief_has_required_sections(self):
        text = (ROOT / "skills/requirement-grill/assets/grill-brief.md").read_text(encoding="utf-8")
        for heading in ("## Units", "## Three questions", "## Cases", "## Not claimed",
                        "## Rejected options", "## Open questions", "## Sources read"):
            self.assertIn(heading, text, heading)
```

Run: `python3 -m unittest tests.test_coverage_pipeline -v` — Expected: FAIL.

- [ ] **Step 2: Write `skills/requirement-grill/SKILL.md`**

````markdown
---
name: requirement-grill
description: Interview the user relentlessly, one question at a time with a recommended answer for each, about one requirement-inventory unit (or a small related group) until requirement, inventory, code and expectation are aligned, then write a grill brief that the project's authoring skill takes as input. Use before admitting or claiming a new scenario, when a unit's expected behaviour, variants, cleanup or scope is unclear, or when a meeting transcript or requirement page must be turned into agreed cases. Never writes scenarios or tests.
---

# Requirement Grill

Reach a shared understanding of one unit before anything is claimed or
written. The output is not a plan; it is the agreed design of the cases,
including what is deliberately not claimed.

## Scope

Use this skill when:

- a unit chosen from `coverage-backlog` is about to be claimed;
- expected behaviour, variants, cleanup or scope of a unit is unclear;
- a requirement page or meeting transcript must become agreed cases.

Do not use it to write the scenario or the test (the authoring skill named in
`authoring.skill`), to resolve a factual conflict by itself
(`source-of-truth`), or to propose black-box additions (`blackbox-review`).

## Required Input

- the unit id(s) and the inventory entry, from `requirements.inventory_paths`;
- the requirement source, fetched as `requirements.source` describes;
- the backend code the inventory entry cites, read-only, from
  `backend.checkout`;
- `authoring.skill`, to shape the brief for it.

A missing key is a `missing context` blocker. A requirement page that cannot
be fetched is recorded under "Sources read" as unavailable, never imagined.

## Procedure

1. **Read first, ask second.** Read the inventory entry, the cited code and
   the requirement. Note every disagreement between them before the first
   question.
2. **Interview.** Ask exactly one question per message. Every question carries
   your recommended answer and why. Prefer a short list of real alternatives.
   Use the platform's question tool when it exists; plain text otherwise.
3. **Walk the decision tree.** Resolve these branches, in this order, and
   follow any sub-branch an answer opens:
   1. the observable outcome - what exactly is asserted, and where a user or
      client would see it;
   2. disagreements - requirement vs inventory vs code. Route each through
      `source-of-truth`. Never change an expectation to match the code; a
      known defect is recorded, not made green;
   3. actor, organisation set-up and variants;
   4. preconditions and test data, and how runs avoid colliding;
   5. waiting - what is polled, how often, the deadline and its start event;
   6. cleanup - what the case creates, how it is removed, how removal is
      proven;
   7. the failing run - what evidence a failure must record;
   8. what is **not** claimed, and options considered and rejected, with why.
4. **Stop when aligned.** Stop when every branch has an answer or an explicit
   open question. The user may also stop the interview; record what remains
   open.
5. **Write the brief.** Fill `assets/grill-brief.md`. Keep it in chat or in a
   scratch file outside the repository. It lives only until the claim: after
   that the scenario and its pull request are the record.

## Rules

- One question per message; always a recommendation.
- Never read a fact into the brief that no source showed; mark it open.
- Never write repository files, scenarios, tests or approval records.
- The brief names units by their inventory ids exactly as the inventory spells
  them.

## Completion

Report the brief, the open questions and the sources read. Next permitted
action: `blackbox-review` in `proposed` mode on the brief, then the authoring
skill's claim with the brief as its input.
````

- [ ] **Step 3: Write `skills/requirement-grill/assets/grill-brief.md`**

```markdown
# Grill Brief - <scenario working title>

- Status: draft (lives until the claim)
- Target: <repository> @ <short sha>
- Authoring skill: <authoring.skill>

## Units

| Unit id | Inventory file | Critical | Requirement reference |
|---|---|---|---|

## Three questions

- **Who acts:** <actor and what they ask for>
- **Observable outcome:** <what a user or client sees when it works>
- **Failing run:** <evidence a failure must record; what never to record>

## Cases

### <case working id> - <title: situation and expected outcome>

- Covers: <unit ids>
- Actor and set-up: <...>
- Variants: <id - what differs> (one per line)
- Preconditions and data: <...>
- Steps and expected results: <action -> observable result, one per line>
- Waiting: <poll interval, deadline, start event>
- Cleanup and proof of removal: <...>
- Known defects: <ticket - effect on the expectation>

## Not claimed

- <behaviour> - <why it is out of scope here>

## Rejected options

- <option> - <why rejected>

## Open questions

- <question> - <who can answer: product owner | developer | source-of-truth>

## Sources read

- <requirement page / inventory file@sha / code file:function> - <read | unavailable>
```

- [ ] **Step 4: Write the platform metadata**

`skills/requirement-grill/agents/claude.yaml`:

```yaml
interface:
  display_name: "Requirement Grill"
  short_description: "Align on one requirement unit before claiming it"
  default_prompt: "Use the requirement-grill skill to interview me one question at a time about this unit and produce a grill brief for the authoring skill."
```

`skills/requirement-grill/agents/openai.yaml`:

```yaml
interface:
  display_name: "Requirement Grill"
  short_description: "Align on one requirement unit before claiming it"
  default_prompt: "Use $requirement-grill to interview me one question at a time about this unit and produce a grill brief for the authoring skill."
```

- [ ] **Step 5: Wire and list**

Orchestrator - insert after the `coverage-backlog` block, before `## Agent Routing`:

```markdown
Use `requirement-grill` when:

- a requirement-inventory unit is about to be claimed for a new scenario;
- a unit's expected behaviour, variants, cleanup or scope is unclear;
- a requirement page or meeting transcript must become agreed cases.

`requirement-grill` asks one question at a time with a recommendation and
produces a grill brief for the project's authoring skill. It writes no
scenario, test or approval and routes every factual conflict through
`source-of-truth`.

```

`bin/qa-kit` and `docs/kit-only-mode.md`: replace `testmo-csv, coverage-backlog).` with

```text
testmo-csv, coverage-backlog,
  requirement-grill).
```

`README.md` tree: replace the `coverage-backlog` block

```text
│   └── coverage-backlog/
│       ├── SKILL.md
│       └── agents/
│           ├── openai.yaml
│           └── claude.yaml
```

with

```text
│   ├── coverage-backlog/
│   │   ├── SKILL.md
│   │   └── agents/
│   │       ├── openai.yaml
│   │       └── claude.yaml
│   └── requirement-grill/
│       ├── SKILL.md
│       ├── agents/
│       │   ├── openai.yaml
│       │   └── claude.yaml
│       └── assets/
│           └── grill-brief.md
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v` — Expected: all PASS.

- [ ] **Step 7: Commit**

```bash
git add skills/requirement-grill agents/qa-orchestrator.md README.md bin/qa-kit docs/kit-only-mode.md tests/test_coverage_pipeline.py
git commit -m "feat(skills): add requirement-grill with grill brief

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: `blackbox-review` skill and heuristics files

**Files:**
- Create: `skills/blackbox-review/SKILL.md`, `skills/blackbox-review/agents/claude.yaml`, `skills/blackbox-review/agents/openai.yaml`, `skills/blackbox-review/assets/findings.md`, `skills/blackbox-review/references/heuristics.md`, `templates/project-heuristics.md`
- Modify: `agents/qa-orchestrator.md`, `README.md`, `bin/qa-kit`, `docs/kit-only-mode.md`, `tests/test_coverage_pipeline.py`

**Interfaces:**
- Consumes: grill brief (Task 3); key `heuristics.project_file`, `requirements.source`.
- Produces: heuristic entry format (6 fields) used by Task 5; finding categories `variant`, `new-case-in-inventory`, `outside-inventory`, `question` used by `coverage-backlog` P2.

- [ ] **Step 1: Write the failing tests**

Change `PIPELINE_SKILLS` to `["coverage-backlog", "requirement-grill", "blackbox-review"]` and append:

```python
HEURISTIC_FIELDS = ["Applies when", "Try", "User expects", "Typical failure", "Technique", "Source"]
TECHNIQUES = {"boundary", "equivalence", "state", "decision-table", "error-guessing", "journey",
              "concurrency", "interruption", "data", "roles", "recovery"}


def heuristic_entries(text):
    # The format example inside a code fence ("### H-<AREA>-<NN>") is not an entry.
    blocks = re.split(r"^### ", text, flags=re.MULTILINE)[1:]
    return [block for block in blocks if re.match(r"H-[A-Z]+-\d{2} ", block)]


class HeuristicsFormatTests(unittest.TestCase):
    def check_file(self, relative, minimum):
        text = (ROOT / relative).read_text(encoding="utf-8")
        entries = heuristic_entries(text)
        self.assertGreaterEqual(len(entries), minimum, relative)
        ids = set()
        for entry in entries:
            entry_id = entry.split(" ", 1)[0]
            self.assertRegex(entry_id, r"^H-[A-Z]+-\d{2}$", entry_id)
            self.assertNotIn(entry_id, ids, entry_id)
            ids.add(entry_id)
            for field in HEURISTIC_FIELDS:
                self.assertIn(f"- **{field}:**", entry, f"{entry_id} lacks {field}")
            technique = re.search(r"- \*\*Technique:\*\* (\S+)", entry).group(1)
            self.assertIn(technique, TECHNIQUES, entry_id)

    def test_kit_heuristics(self):
        self.check_file("skills/blackbox-review/references/heuristics.md", 7)

    def test_project_heuristics_template(self):
        self.check_file("templates/project-heuristics.md", 1)

    def test_findings_template_names_every_category(self):
        text = (ROOT / "skills/blackbox-review/assets/findings.md").read_text(encoding="utf-8")
        for category in ("variant", "new-case-in-inventory", "outside-inventory", "question"):
            self.assertIn(category, text, category)
```

Run: `python3 -m unittest tests.test_coverage_pipeline -v` — Expected: FAIL.

- [ ] **Step 2: Write `skills/blackbox-review/SKILL.md`**

````markdown
---
name: blackbox-review
description: Review proposed or finished test cases from the user's side only - the requirement and the cases, never the product code - and propose black-box additions (variants, new cases for an inventory unit, outside-inventory cases, and questions for the product owner) using test-design techniques and the kit and project heuristics files. Use after requirement-grill and before a scenario is claimed (proposed mode), or over finished scenarios of a domain (audit mode), when coverage derived from code may miss what users actually do. Never writes tests or scenarios.
---

# Black-Box Review

Coverage derived from code verifies what the code does. This review asks what
a user will do, expect and notice - including behaviour the code never
implemented. Independence from the implementation is the point: do not read
product source code during this review.

## Scope

Use this skill when:

- `proposed` mode: a grill brief or draft scenario exists and is not claimed;
- `audit` mode: finished scenarios and their tests of a domain are reviewed
  for user-side gaps.

Do not use it to decide a verdict on a transition (`qa-review-gate`), to
resolve a disputed fact (`source-of-truth`), or to write the additions (the
authoring skill named in `authoring.skill`).

## Required Input

- the mode: `proposed` or `audit`;
- the requirement, fetched as `requirements.source` describes;
- the cases: a grill brief, or scenario files and their test classes;
- heuristics: `references/heuristics.md` in this skill, and the file named by
  `heuristics.project_file` when the key is set. If the key is set and the
  file is missing, say so and continue with the kit file only.

Out of bounds: product source code, inventory `src` citations, code comments.
Test code is read only for what it asserts, not for how the product works.

## Procedure

1. **Model the user.** From the requirement only: who the users are, what each
   wants, which journeys pass through this feature before and after it, which
   states the visible objects go through.
2. **Apply techniques** to every case and to the gaps between cases:
   equivalence classes and boundaries; state transitions (including invalid
   ones); decision tables over roles and settings; error guessing; journeys
   across features; interruption and recovery; retry and idempotency;
   concurrency between two actors or two sessions; data variety (languages,
   right-to-left text, sizes, empty, special characters); roles as the user
   experiences them.
3. **Apply heuristics.** For each heuristic whose "Applies when" matches, try
   its probe against the cases. Cite the heuristic id on every finding it
   produced.
4. **Classify each finding:**
   - `variant` - an existing case gains a variant;
   - `new-case-in-inventory` - a new case for a unit already in the inventory;
   - `outside-inventory` - behaviour no inventory unit describes; a new case
     with an empty coverage list and an outside-inventory reason, and a P2
     backlog unit;
   - `question` - the requirement is silent or ambiguous. Never turn a
     question into an assumed expectation; route it through `source-of-truth`
     to the product owner.
5. **Rank.** Risk is high when a user would lose data, see another user's data,
   be blocked on the main path, or get a silent wrong result; medium when the
   user is confused or must retry; low otherwise.
6. **Report** with `assets/findings.md`.

## Rules

- Never read product source code in this review.
- Never write scenarios, tests, heuristics files or approval records.
- Every finding states what the user does and what the user would notice.
- Do not repeat what a case already checks; cite the case id when close.
- Prefer ten sharp findings over forty generic ones.

## Learning loop

When the user accepts or rejects a finding for a reason that generalises, offer
a new heuristic entry in the format of `references/heuristics.md` - generic
ones for the kit file, product-specific ones for the project file. Write it
only when the user asks.

## Completion

Report the mode, the sources read, the findings table and the heuristics
applied. Next permitted action: accepted `variant` and `new-case-in-inventory`
findings go into the grill brief or the scenario through the authoring skill;
`outside-inventory` findings go to `coverage-backlog`; `question` findings go
to `source-of-truth`.
````

- [ ] **Step 3: Write `skills/blackbox-review/assets/findings.md`**

```markdown
# Black-Box Findings - <scenario or domain>

- Mode: proposed | audit
- Requirement: <reference> (read | unavailable)
- Cases reviewed: <brief title | scenario ids>
- Heuristics files: kit references/heuristics.md; project <path | not set>

| # | Category | Risk | Case or unit | User does | User would notice | Heuristic | Suggested addition |
|---|---|---|---|---|---|---|---|
| 1 | variant | high | <case id> | <...> | <...> | H-XXX-01 | <variant id and difference> |
| 2 | new-case-in-inventory | medium | <unit id> | <...> | <...> | - | <case title> |
| 3 | outside-inventory | medium | - | <...> | <...> | H-XXX-02 | <case title; outside-inventory reason> |
| 4 | question | - | <case id> | <...> | <...> | - | <question for the product owner> |

Not raised (already covered): <case id - heuristic id> (one per line)
```

- [ ] **Step 4: Write `skills/blackbox-review/references/heuristics.md`**

````markdown
# Black-Box Heuristics - Kit Level

Generic heuristics for any product. Product-specific heuristics live in the
project heuristics file named by `heuristics.project_file`. No product,
service, environment or company names in this file.

Entry format:

```markdown
### H-<AREA>-<NN> - <short name>

- **Applies when:** <what in a requirement or case makes it relevant>
- **Try:** <the concrete probe or variation>
- **User expects:** <the black-box oracle, in user terms>
- **Typical failure:** <what usually goes wrong>
- **Technique:** <boundary | equivalence | state | decision-table | error-guessing | journey | concurrency | interruption | data | roles | recovery>
- **Source:** <mined: suite/file | interview: date | review finding: reference | seed>
```

### H-RETRY-01 - Retry after a timeout must not duplicate

- **Applies when:** a create or submit action can time out or the client retries.
- **Try:** send the same create twice with the same payload; repeat after an artificial client timeout.
- **User expects:** one resource, or a clear "already exists"; never two silent copies.
- **Typical failure:** duplicate records, or the second call fails with a raw server error.
- **Technique:** error-guessing
- **Source:** seed

### H-DATA-01 - Bidirectional and non-Latin text survives the round trip

- **Applies when:** a user-supplied name, title, filename or free text is stored and shown again.
- **Try:** right-to-left text, mixed right-to-left and left-to-right with digits, combining characters, emoji, leading and trailing spaces, the maximum length in multi-byte characters.
- **User expects:** the same text back, searchable, correctly ordered.
- **Typical failure:** reversed or truncated text, failed search, a length limit counted in bytes instead of characters.
- **Technique:** data
- **Source:** seed

### H-STATE-01 - Act on something another user just deleted

- **Applies when:** two actors can see the same resource.
- **Try:** actor A opens or lists the resource; actor B deletes it; A acts on it.
- **User expects:** a clear "no longer exists", nothing half-done.
- **Typical failure:** a server error, a ghost entry, or the action brings the resource back.
- **Technique:** concurrency
- **Source:** seed

### H-INTR-01 - Interrupted long operation

- **Applies when:** an upload, import, scan or any asynchronous job.
- **Try:** cancel or lose the connection midway; restart; repeat the operation.
- **User expects:** either a complete result or a clean failure with a way to retry.
- **Typical failure:** a stuck "in progress" state, or partial data shown as complete.
- **Technique:** interruption
- **Source:** seed

### H-ROLE-01 - Permission removed during a session

- **Applies when:** roles or sharing can change while a user is active.
- **Try:** revoke the user's permission while they hold an open view or a token; let them continue.
- **User expects:** the next action is refused with an understandable message.
- **Typical failure:** the old session keeps full access until the next sign-in.
- **Technique:** roles
- **Source:** seed

### H-BND-01 - Limits at, below and above

- **Applies when:** a documented size, count, length or rate limit.
- **Try:** limit minus one, the limit, limit plus one; zero; empty.
- **User expects:** the limit is enforced exactly as documented, with a message that names it.
- **Typical failure:** off-by-one, or a generic error that does not name the limit.
- **Technique:** boundary
- **Source:** seed

### H-ERR-01 - Error messages are actionable

- **Applies when:** any refusal the user can trigger.
- **Try:** each refusal path in the requirement.
- **User expects:** what went wrong and what to do next; no stack traces or internal ids.
- **Typical failure:** a generic "something went wrong", or leaked internals.
- **Technique:** error-guessing
- **Source:** seed
````

- [ ] **Step 5: Write `templates/project-heuristics.md`**

````markdown
# Project Heuristics - <project name>

Product-specific black-box heuristics for `blackbox-review`. Keep this file
next to the project context (untracked when the repository is shared) and set
`heuristics.project_file` to its path. Generic heuristics belong in the kit
file `skills/blackbox-review/references/heuristics.md`, not here.

Use the same entry format as the kit file. The example below is fictional.

### H-SYNC-01 - Source renamed between two syncs

- **Applies when:** a connector syncs files from an external storage account.
- **Try:** sync; rename a folder in the external account; sync again.
- **User expects:** the renamed folder appears once, under the new name, with its files.
- **Typical failure:** both names shown, or the files counted twice in search.
- **Technique:** state
- **Source:** interview: 2026-10-23
````

- [ ] **Step 6: Write the platform metadata**

`skills/blackbox-review/agents/claude.yaml`:

```yaml
interface:
  display_name: "Black-Box Review"
  short_description: "Propose user-side test additions without reading code"
  default_prompt: "Use the blackbox-review skill to review these cases from the user's side and propose variants, new cases, outside-inventory cases and product questions."
```

`skills/blackbox-review/agents/openai.yaml`:

```yaml
interface:
  display_name: "Black-Box Review"
  short_description: "Propose user-side test additions without reading code"
  default_prompt: "Use $blackbox-review to review these cases from the user's side and propose variants, new cases, outside-inventory cases and product questions."
```

- [ ] **Step 7: Wire and list**

Orchestrator - insert after the `requirement-grill` block:

```markdown
Use `blackbox-review` when:

- a grill brief or draft scenario should be checked from the user's side
  before it is claimed;
- finished scenarios of a domain should be audited for user-side gaps;
- coverage derived from code may miss what users actually do.

`blackbox-review` never reads product source code and never writes tests,
scenarios or approvals. Its `outside-inventory` findings go to
`coverage-backlog`; its `question` findings go to `source-of-truth`.

```

`bin/qa-kit` and `docs/kit-only-mode.md`: replace `  requirement-grill).` with `  requirement-grill, blackbox-review).`

`README.md` tree: replace

```text
│   └── requirement-grill/
│       ├── SKILL.md
│       ├── agents/
│       │   ├── openai.yaml
│       │   └── claude.yaml
│       └── assets/
│           └── grill-brief.md
```

with

```text
│   ├── requirement-grill/
│   │   ├── SKILL.md
│   │   ├── agents/
│   │   │   ├── openai.yaml
│   │   │   └── claude.yaml
│   │   └── assets/
│   │       └── grill-brief.md
│   └── blackbox-review/
│       ├── SKILL.md
│       ├── agents/
│       │   ├── openai.yaml
│       │   └── claude.yaml
│       ├── assets/
│       │   └── findings.md
│       └── references/
│           └── heuristics.md
```

and in the `templates/` part of the tree replace

```text
└── templates/
    ├── project-context.md
    └── test-design-contract.md
```

with

```text
└── templates/
    ├── project-context.md
    ├── project-heuristics.md
    └── test-design-contract.md
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v` — Expected: all PASS.

- [ ] **Step 9: Commit**

```bash
git add skills/blackbox-review templates/project-heuristics.md agents/qa-orchestrator.md README.md bin/qa-kit docs/kit-only-mode.md tests/test_coverage_pipeline.py
git commit -m "feat(skills): add blackbox-review with seed heuristics

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Mine and interview heuristics (HITL)

This task needs the user present. It reads the legacy suites read-only and
changes only the kit heuristics file; product-specific output stays outside the
kit's git.

**Files:**
- Modify: `skills/blackbox-review/references/heuristics.md`
- Create (outside kit git): `/Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers/qa/heuristics-mining.md`, `/Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers/qa/heuristics.md`

**Interfaces:**
- Consumes: entry format and `HeuristicsFormatTests` (Task 4).

- [ ] **Step 1: Inventory the sources**

```bash
mkdir -p /Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers/qa
cd /Users/alex/MyRepos/qa
git ls-files api-tests/tests e2e-ui-tests/tests e2e-ui-tests/specs Docs/draft-test-plans | wc -l
git log --format='%an' -- api-tests/tests e2e-ui-tests | sort | uniq -c | sort -rn | head
```

Expected: file count and authors; record which authors are the user (the user's own tests are the primary signal).

- [ ] **Step 2: Extract candidate checks**

Dispatch one read-only Explore subagent per source (`api-tests`, `e2e-ui-tests`, `Docs/draft-test-plans`), each with this prompt:

```text
Read-only. In <source path> of /Users/alex/MyRepos/qa, list recurring test checks that do NOT
follow from reading backend code: negative inputs, boundary values, data variety (languages,
RTL, sizes, special characters, empty), repeated or concurrent actions, interrupted operations,
role and permission combinations, cross-feature journeys, error-message expectations, cleanup
and recovery. For each pattern give: a one-line description, 2-3 example file:line references,
how often it recurs, and whether it is generic (any product) or specific to this product
(name the feature). Return a markdown table. No fixes, no opinions on code quality.
```

Write the merged tables to `.../ai-qa-workflow-kit-consumers/qa/heuristics-mining.md`.

- [ ] **Step 3: Split and draft**

For every pattern, draft an entry in the format of Task 4 with `Source: mined: <file>`:
- generic → append to `skills/blackbox-review/references/heuristics.md` (new ids, e.g. `H-PAGE-01`);
- product-specific → `.../ai-qa-workflow-kit-consumers/qa/heuristics.md` (start from `templates/project-heuristics.md`, delete the fictional example).

Re-run the agnostic test after every batch: `python3 -m unittest tests.test_coverage_pipeline -v`.

- [ ] **Step 4: Interview the user**

Run the `requirement-grill` interview style (one question, a recommendation each) over gaps the mining did not cover. Ask at least:
1. Where in this product do bugs usually hide that developers do not expect?
2. What do you check on every new feature without being asked?
3. Which user complaints from production taught you a check?
4. Which test types from the legacy suites have no equivalent in the new catalog?
5. Which areas of the mining table are wrong or overstated?

Each answer that generalises becomes an entry with `Source: interview: 2026-10-23` (use the actual date).

- [ ] **Step 5: Review with the user**

Show both files' entry lists (id, name, technique). Apply the user's edits. Run `python3 -m unittest discover -s tests -v` — Expected: all PASS.

- [ ] **Step 6: Commit the kit file only**

```bash
git add skills/blackbox-review/references/heuristics.md
git commit -m "feat(blackbox-review): seed heuristics from mined suites and interview

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Tell the user to copy `.../ai-qa-workflow-kit-consumers/qa/heuristics.md` to `<qa>/ai-workflow/heuristics.md` on the work machine and set `heuristics.project_file` to that path.

---

### Task 6: `night-shift` skill and headless prompt

**Files:**
- Create: `skills/night-shift/SKILL.md`, `skills/night-shift/agents/claude.yaml`, `skills/night-shift/agents/openai.yaml`, `skills/night-shift/assets/night-prompt.md`
- Modify: `agents/qa-orchestrator.md`, `README.md`, `bin/qa-kit`, `docs/kit-only-mode.md`, `tests/test_coverage_pipeline.py`

**Interfaces:**
- Consumes: keys `authoring.skill`, `authoring.after_checkpoint_phases`, `checks.safe`, `checks.preflight`, `run.live_sandbox`, `review.command`, `labels.*`; `destructive-safety` skill.
- Produces: prompt placeholders `{{PR}}`, `{{BRANCH}}`, `{{RUN_ID}}`, `{{KIT_DIR}}`, `{{TARGET}}` (filled by `bin/qa-night`, Task 8); report marker `night-shift run <RUN_ID>` (read by Task 7).

- [ ] **Step 1: Write the failing tests**

Change `PIPELINE_SKILLS` to `["coverage-backlog", "requirement-grill", "blackbox-review", "night-shift"]` and append:

```python
class NightShiftContentTests(unittest.TestCase):
    def test_prompt_has_every_placeholder(self):
        text = (ROOT / "skills/night-shift/assets/night-prompt.md").read_text(encoding="utf-8")
        for placeholder in ("{{PR}}", "{{BRANCH}}", "{{RUN_ID}}", "{{KIT_DIR}}", "{{TARGET}}"):
            self.assertIn(placeholder, text, placeholder)
        self.assertIn("night-shift run {{RUN_ID}}", text)

    def test_skill_forbids_approval_and_merge(self):
        text = (ROOT / "skills/night-shift/SKILL.md").read_text(encoding="utf-8")
        for phrase in ("gh pr ready", "merge", "approval", "force-push", "bypassPermissions",
                       "ready label", "destructive-safety"):
            self.assertIn(phrase, text, phrase)
```

Run: `python3 -m unittest tests.test_coverage_pipeline -v` — Expected: FAIL.

- [ ] **Step 2: Write `skills/night-shift/SKILL.md`**

````markdown
---
name: night-shift
description: Implement one human-confirmed scenario pull request without a human present - run the project's authoring skill for the phases after its confirmation checkpoint, the safe checks, a destructive-safety gate, a live run in the sandbox environment and a self-review, then push to the pull request's branch, comment a report and swap the ready label for done or blocked. Use only inside a headless session started by bin/qa-night in a worktree of a draft pull request that carries the ready label. Never asks questions, approves, merges or widens scope.
---

# Night Shift

The day shift (a human with `coverage-backlog`, `requirement-grill`,
`blackbox-review` and the authoring skill) claimed the scenario and confirmed
its cases. The night shift implements exactly that, proves it, and leaves a
report for the morning. Nobody is watching: when in doubt, stop.

## Preconditions

Check all before any edit. Any failure: stop, mark blocked (see Stop).

1. The session runs in a git worktree of the target on the pull request's
   branch (`git branch --show-current` equals the branch in the prompt).
2. The pull request is an open draft and carries `labels.ready`, and carries
   neither `labels.done` nor `labels.blocked`
   (`gh pr view <n> --json isDraft,state,labels`).
3. The confirmed cases are recorded: the scenario file on the branch and the
   confirmation the authoring skill's checkpoint left in the pull request
   (description or comments). No confirmation found: stop.
4. Every key used below exists in the project context's "Coverage Pipeline"
   section (read the file named in the prompt, not the worktree).
5. The `destructive-safety` denylist exists. Missing: safe checks only, no
   live run, then stop as blocked.

## Procedure

1. **Read.** The pull request (`gh pr view <n> --comments`), its diff against
   the default branch, the scenario and the confirmation. List the confirmed
   cases and the files the pull request may touch.
2. **Implement.** Invoke the skill named by `authoring.skill` and run only the
   phases listed in `authoring.after_checkpoint_phases`. Follow that skill's
   rules; this skill never overrides them.
3. **Safe checks.** Run every command in `checks.safe`. Fix only what your own
   change broke. Repeat until clean or until the change would leave the
   confirmed scope.
4. **Destructive gate.** Run `destructive-safety` over every destructive call
   the new tests make. A call it does not clear: stop.
5. **Preflight.** Run `checks.preflight`. A failure is `blocked: environment`,
   never "not verified" reported as success.
6. **Live run.** Run `run.live_sandbox`, sandbox target only. Publish what the
   command publishes; never another target.
7. **Self-review.** Run `review.command`. Fix findings that change a verdict;
   record why for the rest. Repeat until it reports nothing you act on.
8. **Commit and push.** Commit with explicit paths. Every commit message ends
   with `night-shift run <run id>`. Push with `git push origin HEAD:<branch>`.
9. **Report.** Comment on the pull request with the template below, then
   `gh pr edit <n> --remove-label <labels.ready> --add-label <labels.done>`.

## Stop

Stop at once - no workaround - when:

- the work would depart from the confirmed cases (a new case, a changed
  expectation, a dropped variant) - the authoring skill's "ask again" point;
- it needs a new fixture, probe, runner flag or anything that skill reserves
  for a human;
- a file outside the listed scope must change, or another open pull request
  also changes it;
- a destructive call is not cleared, the preflight fails, or the budget runs
  out.

To stop: commit and push whatever is finished and consistent, comment the
report with status `blocked` and the exact question a human must answer, then
`gh pr edit <n> --remove-label <labels.ready> --add-label <labels.blocked>`.

## Never

- ask a question inside the session; the question goes into the report;
- add the ready label, mark the pull request ready (`gh pr ready`), merge,
  record approval, or edit approval fields;
- force-push, push to the default branch, or rewrite earlier commits;
- run with `bypassPermissions`, or publish to a non-sandbox target;
- change an expectation to match what the product does.

## Report template

```markdown
### Night shift - night-shift run <run id>

**Status:** done | blocked
**Cases:** <case id - passed | failed | not verified> (one per line)
**Live run:** <command>, <environment>, <sandbox link or run id>
**Evidence:** <failing step, expected vs actual, resource ids - for every non-pass>
**Self-review:** <level, findings fixed, findings left with reason>
**Commits:** <short sha - subject>
**Blocked on:** <the exact question for a human, or "-">
```
````

- [ ] **Step 3: Write `skills/night-shift/assets/night-prompt.md`**

```markdown
You are the night shift for pull request #{{PR}} (branch {{BRANCH}}), run {{RUN_ID}}.

Governance is the AI QA Workflow Kit only. First read
{{KIT_DIR}}/agents/qa-orchestrator.md, then follow
{{KIT_DIR}}/skills/night-shift/SKILL.md exactly.

Target project: {{TARGET}}. Read project facts only from
{{TARGET}}/ai-workflow/project-context.md (it is not in this worktree).
The only non-kit skill you may use is the one named by authoring.skill in
that file.

Your working directory is a git worktree of the target on branch {{BRANCH}}.
No human is watching this session: never ask a question here. When the skill
says stop, push what is consistent, comment the report with status blocked
and your question, swap the labels, and end.

End every commit message and every pull request comment with
"night-shift run {{RUN_ID}}".
```

- [ ] **Step 4: Write the platform metadata**

`skills/night-shift/agents/claude.yaml`:

```yaml
interface:
  display_name: "Night Shift"
  short_description: "Implement one confirmed scenario PR without a human"
  default_prompt: "Use the night-shift skill to implement this confirmed scenario pull request, prove it in the sandbox, push, report and swap the labels."
```

`skills/night-shift/agents/openai.yaml`:

```yaml
interface:
  display_name: "Night Shift"
  short_description: "Implement one confirmed scenario PR without a human"
  default_prompt: "Use $night-shift to implement this confirmed scenario pull request, prove it in the sandbox, push, report and swap the labels."
```

- [ ] **Step 5: Wire and list**

Orchestrator - insert after the `blackbox-review` block:

```markdown
Use `night-shift` when:

- a headless session started by `bin/qa-night` must implement one draft
  pull request whose cases a human confirmed and labelled ready.

`night-shift` runs the authoring skill's post-confirmation phases, the safe
checks, `destructive-safety`, a sandbox live run and a self-review, then
pushes and reports. It never asks, approves, merges, marks a pull request
ready, adds the ready label or widens scope; any deviation ends the run as
blocked.

```

`bin/qa-kit` and `docs/kit-only-mode.md`: replace `  requirement-grill, blackbox-review).` with `  requirement-grill, blackbox-review, night-shift).`

`README.md` tree: replace

```text
│   └── blackbox-review/
│       ├── SKILL.md
│       ├── agents/
│       │   ├── openai.yaml
│       │   └── claude.yaml
│       ├── assets/
│       │   └── findings.md
│       └── references/
│           └── heuristics.md
```

with

```text
│   ├── blackbox-review/
│   │   ├── SKILL.md
│   │   ├── agents/
│   │   │   ├── openai.yaml
│   │   │   └── claude.yaml
│   │   ├── assets/
│   │   │   └── findings.md
│   │   └── references/
│   │       └── heuristics.md
│   └── night-shift/
│       ├── SKILL.md
│       ├── agents/
│       │   ├── openai.yaml
│       │   └── claude.yaml
│       └── assets/
│           └── night-prompt.md
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v` — Expected: all PASS.

- [ ] **Step 7: Commit**

```bash
git add skills/night-shift agents/qa-orchestrator.md README.md bin/qa-kit docs/kit-only-mode.md tests/test_coverage_pipeline.py
git commit -m "feat(skills): add night-shift skill and headless prompt

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: PR selector `bin/lib/select_ready_prs.py`

**Files:**
- Create: `bin/lib/select_ready_prs.py`
- Modify: `tests/test_coverage_pipeline.py`

**Interfaces:**
- Consumes: `gh pr list --json number,headRefName,isDraft,labels,files` output; per-PR `<n>.events.json`, `<n>.comments.json` (JSON array or JSON lines); marker `night-shift run ` (Task 6).
- Produces: `load_json_items(path) -> list`, `last_label_event(events, label) -> dict | None`, `classify(pr, events, comments, others, labels, bot_pattern, night_actor) -> tuple[str, str]` returning `("eligible", "")` or `("skipped", reason)`; CLI prints `"<number>\t<branch>"` per eligible PR to stdout and `"skip #<n>: <reason>"` to stderr; flags `--prs`, `--events-dir`, `--label-ready`, `--label-done`, `--label-blocked`, `--night-actor`, `--bot-pattern`, `--only`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_coverage_pipeline.py`:

```python
LABELS = {"ready": "afk-ready", "done": "afk-done", "blocked": "afk-blocked"}


def pr(number, labels=("afk-ready",), draft=True, files=("catalog/x.yaml",)):
    return {"number": number, "headRefName": f"branch-{number}", "isDraft": draft,
            "labels": [{"name": name} for name in labels],
            "files": [{"path": path} for path in files]}


def labeled(login, at, label="afk-ready", kind="labeled", actor_type="User"):
    return {"event": kind, "created_at": at, "label": {"name": label},
            "actor": {"login": login, "type": actor_type}}


class SelectReadyPrsTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_module("bin/lib/select_ready_prs.py", "select_ready_prs")

    def classify(self, item, events, comments=(), others=(), night_actor=""):
        return self.mod.classify(item, list(events), list(comments), list(others),
                                 LABELS, r"\[bot\]$", night_actor)

    def test_human_label_is_eligible(self):
        self.assertEqual(self.classify(pr(1), [labeled("alex", "2026-10-23T10:00:00Z")]),
                         ("eligible", ""))

    def test_bot_label_is_skipped(self):
        status, reason = self.classify(pr(1), [labeled("ci[bot]", "2026-10-23T10:00:00Z", actor_type="Bot")])
        self.assertEqual(status, "skipped")
        self.assertIn("ci[bot]", reason)

    def test_night_actor_label_is_skipped(self):
        status, _ = self.classify(pr(1), [labeled("night", "2026-10-23T10:00:00Z")], night_actor="night")
        self.assertEqual(status, "skipped")

    def test_unlabeled_after_labeled_is_skipped(self):
        events = [labeled("alex", "2026-10-23T10:00:00Z"),
                  labeled("alex", "2026-10-23T11:00:00Z", kind="unlabeled")]
        self.assertEqual(self.classify(pr(1), events)[0], "skipped")

    def test_not_draft_and_done_and_blocked_are_skipped(self):
        event = [labeled("alex", "2026-10-23T10:00:00Z")]
        self.assertEqual(self.classify(pr(1, draft=False), event)[0], "skipped")
        self.assertEqual(self.classify(pr(1, labels=("afk-ready", "afk-done")), event)[0], "skipped")
        self.assertEqual(self.classify(pr(1, labels=("afk-ready", "afk-blocked")), event)[0], "skipped")

    def test_report_newer_than_label_is_skipped_older_is_not(self):
        event = [labeled("alex", "2026-10-23T10:00:00Z")]
        newer = [{"body": "### Night shift - night-shift run 1", "created_at": "2026-10-23T12:00:00Z"}]
        older = [{"body": "### Night shift - night-shift run 0", "created_at": "2026-10-22T12:00:00Z"}]
        self.assertEqual(self.classify(pr(1), event, newer)[0], "skipped")
        self.assertEqual(self.classify(pr(1), event, older)[0], "eligible")

    def test_file_shared_with_other_open_pr_is_skipped(self):
        event = [labeled("alex", "2026-10-23T10:00:00Z")]
        other = pr(2, labels=(), files=("framework/drivers/files.py",))
        status, reason = self.classify(pr(1, files=("framework/drivers/files.py",)), event, others=[other])
        self.assertEqual(status, "skipped")
        self.assertIn("framework/drivers/files.py", reason)

    def test_load_json_items_reads_array_and_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            array = Path(tmp) / "a.json"
            lines = Path(tmp) / "b.json"
            array.write_text('[{"x": 1}, {"x": 2}]', encoding="utf-8")
            lines.write_text('{"x": 1}\n{"x": 2}\n', encoding="utf-8")
            self.assertEqual(self.mod.load_json_items(array), [{"x": 1}, {"x": 2}])
            self.assertEqual(self.mod.load_json_items(lines), [{"x": 1}, {"x": 2}])
            self.assertEqual(self.mod.load_json_items(Path(tmp) / "missing.json"), [])

    def test_cli_prints_eligible_and_reports_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "prs.json").write_text(json.dumps([pr(12), pr(13, files=("b.yaml",))]), encoding="utf-8")
            (tmp / "12.events.json").write_text(json.dumps([labeled("alex", "2026-10-23T10:00:00Z")]), encoding="utf-8")
            (tmp / "13.events.json").write_text(json.dumps([labeled("ci[bot]", "2026-10-23T10:00:00Z", actor_type="Bot")]), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "bin/lib/select_ready_prs.py"), "--prs", str(tmp / "prs.json"),
                 "--events-dir", str(tmp), "--label-ready", "afk-ready", "--label-done", "afk-done",
                 "--label-blocked", "afk-blocked"],
                capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "12\tbranch-12")
        self.assertIn("skip #13:", result.stderr)

    def test_cli_help(self):
        result = subprocess.run([sys.executable, str(ROOT / "bin/lib/select_ready_prs.py"), "--help"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout.lower())
```

Run: `python3 -m unittest tests.test_coverage_pipeline -v` — Expected: `SelectReadyPrsTests` ERROR (module missing).

- [ ] **Step 2: Write `bin/lib/select_ready_prs.py`**

```python
#!/usr/bin/env python3
"""Choose which open pull requests the night shift may take.

A pull request is eligible when it is an open draft with the ready label, the
last `labeled` event for that label (not undone by an `unlabeled` event) came
from neither a bot nor the night-shift account, it has neither the done nor the
blocked label, no comment carrying "night-shift run " is newer than that event,
and it changes no file that another open pull request also changes.

Prints "<number>\\t<branch>" per eligible pull request; reasons for skips go to
stderr as "skip #<number>: <reason>".
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPORT_MARKER = "night-shift run "


def load_json_items(path):
    path = Path(path)
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return data if isinstance(data, list) else [data]


def label_names(pr):
    return {label["name"] for label in pr.get("labels", [])}


def changed_files(pr):
    return {item["path"] for item in pr.get("files", [])}


def last_label_event(events, label):
    latest = None
    for event in sorted(events, key=lambda item: item.get("created_at", "")):
        if (event.get("label") or {}).get("name") != label:
            continue
        if event.get("event") == "labeled":
            latest = event
        elif event.get("event") == "unlabeled":
            latest = None
    return latest


def is_human(actor, bot_pattern, night_actor):
    if not actor:
        return False
    login = actor.get("login", "")
    if actor.get("type") == "Bot" or re.search(bot_pattern, login):
        return False
    return not (night_actor and login == night_actor)


def classify(pr, events, comments, others, labels, bot_pattern, night_actor):
    names = label_names(pr)
    if not pr.get("isDraft"):
        return "skipped", "not a draft"
    if labels["ready"] not in names:
        return "skipped", "no ready label"
    for key in ("done", "blocked"):
        if labels[key] in names:
            return "skipped", f"has the {labels[key]} label"
    event = last_label_event(events, labels["ready"])
    if event is None:
        return "skipped", "no labeled event for the ready label"
    actor = event.get("actor") or {}
    if not is_human(actor, bot_pattern, night_actor):
        return "skipped", f"ready label applied by {actor.get('login', 'unknown')}"
    labelled_at = event.get("created_at", "")
    for comment in comments:
        if REPORT_MARKER in comment.get("body", "") and comment.get("created_at", "") > labelled_at:
            return "skipped", "a night-shift report is newer than the ready label"
    shared = set()
    for other in others:
        shared |= changed_files(pr) & changed_files(other)
    if shared:
        return "skipped", "files also changed by another open PR: " + ", ".join(sorted(shared))
    return "eligible", ""


def main(argv=None):
    parser = argparse.ArgumentParser(description="Choose the pull requests the night shift may take.")
    parser.add_argument("--prs", required=True, type=Path, help="gh pr list JSON (all open PRs)")
    parser.add_argument("--events-dir", required=True, type=Path, help="dir with <n>.events.json and <n>.comments.json")
    parser.add_argument("--label-ready", required=True)
    parser.add_argument("--label-done", required=True)
    parser.add_argument("--label-blocked", required=True)
    parser.add_argument("--night-actor", default="", help="login the night shift acts as, if distinct")
    parser.add_argument("--bot-pattern", default=r"\[bot\]$")
    parser.add_argument("--only", type=int, help="consider only this pull request number")
    args = parser.parse_args(argv)

    labels = {"ready": args.label_ready, "done": args.label_done, "blocked": args.label_blocked}
    prs = load_json_items(args.prs)
    for item in prs:
        number = item["number"]
        if labels["ready"] not in label_names(item):
            continue
        if args.only is not None and number != args.only:
            continue
        events = load_json_items(args.events_dir / f"{number}.events.json")
        comments = load_json_items(args.events_dir / f"{number}.comments.json")
        others = [other for other in prs if other["number"] != number]
        status, reason = classify(item, events, comments, others, labels, args.bot_pattern, args.night_actor)
        if status == "eligible":
            print(f"{number}\t{item['headRefName']}")
        else:
            print(f"skip #{number}: {reason}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Then `chmod +x bin/lib/select_ready_prs.py`.

- [ ] **Step 3: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v` — Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add bin/lib/select_ready_prs.py tests/test_coverage_pipeline.py
git commit -m "feat(night-shift): add ready-PR selector

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Launcher `bin/qa-night` and spec amendment

**Files:**
- Create: `bin/qa-night`
- Modify: `tests/test_coverage_pipeline.py`, `docs/superpowers/specs/2026-10-23-coverage-pipeline-design.md`, `README.md`

**Interfaces:**
- Consumes: `bin/lib/pipeline_config.py` (Task 1), `bin/lib/select_ready_prs.py` (Task 7), `skills/night-shift/assets/night-prompt.md` (Task 6).
- Produces: CLI `qa-night <target> [--dry-run] [--once <n>]`; env overrides `QA_NIGHT_GH`, `QA_NIGHT_CLAUDE`, `QA_NIGHT_HOME`; dry-run stdout lines `would run: #<n> (<branch>)`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_coverage_pipeline.py`:

```python
FAKE_GH = """#!/usr/bin/env bash
case "$1" in
  pr) cat "$FIXTURES/prs.json" ;;
  api)
    n=$(printf '%s' "$2" | sed -E 's#.*/issues/([0-9]+)/.*#\\1#')
    case "$2" in
      */events) cat "$FIXTURES/$n.events.json" 2>/dev/null || echo '[]' ;;
      */comments) cat "$FIXTURES/$n.comments.json" 2>/dev/null || echo '[]' ;;
    esac ;;
esac
"""

CONTEXT = """# Project Context

## Coverage Pipeline

- labels.ready: afk-ready
- labels.done: afk-done
- labels.blocked: afk-blocked
- night.permission_mode: {mode}
- night.allowed_tools: Read,Edit
- night.max_turns: 5
- night.timeout_minutes: 1
- night.actor_login:
"""


class QaNightTests(unittest.TestCase):
    def run_night(self, *args, mode="acceptEdits"):
        tmp = Path(self.tmp.name)
        target = tmp / "target"
        (target / "ai-workflow").mkdir(parents=True, exist_ok=True)
        (target / "ai-workflow" / "project-context.md").write_text(CONTEXT.format(mode=mode), encoding="utf-8")
        fixtures = tmp / "fixtures"
        fixtures.mkdir(exist_ok=True)
        (fixtures / "prs.json").write_text(json.dumps([pr(12), pr(13, files=("b.yaml",))]), encoding="utf-8")
        (fixtures / "12.events.json").write_text(json.dumps([labeled("alex", "2026-10-23T10:00:00Z")]), encoding="utf-8")
        (fixtures / "13.events.json").write_text(json.dumps([labeled("ci[bot]", "2026-10-23T10:00:00Z", actor_type="Bot")]), encoding="utf-8")
        gh = tmp / "gh"
        gh.write_text(FAKE_GH, encoding="utf-8")
        gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
        env = dict(os.environ, QA_NIGHT_GH=str(gh), QA_NIGHT_HOME=str(tmp / "home"),
                   QA_NIGHT_CLAUDE="false", FIXTURES=str(fixtures))
        return subprocess.run([str(ROOT / "bin/qa-night"), str(target), *args],
                              env=env, capture_output=True, text=True, check=False)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_shell_syntax(self):
        result = subprocess.run(["bash", "-n", str(ROOT / "bin/qa-night")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_help(self):
        result = subprocess.run([str(ROOT / "bin/qa-night"), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("qa-night <target-path>", result.stdout)

    def test_requires_target(self):
        result = subprocess.run([str(ROOT / "bin/qa-night")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("target path is required", result.stderr)

    def test_dry_run_selects_human_labelled_pr_only(self):
        result = self.run_night("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("would run: #12 (branch-12)", result.stdout)
        self.assertNotIn("#13", result.stdout)
        self.assertIn("skip #13:", result.stderr)

    def test_once_limits_to_one_pr(self):
        result = self.run_night("--dry-run", "--once", "13")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("nothing to do", result.stdout)

    def test_refuses_bypass_permissions(self):
        result = self.run_night("--dry-run", mode="bypassPermissions")
        self.assertEqual(result.returncode, 1)
        self.assertIn("bypassPermissions is not allowed", result.stderr)
```

Run: `python3 -m unittest tests.test_coverage_pipeline -v` — Expected: `QaNightTests` FAIL (script missing).

- [ ] **Step 2: Write `bin/qa-night`**

```bash
#!/usr/bin/env bash
# qa-night - run the night shift over draft PRs a human labelled ready.
#
# Usage:
#   qa-night <target-path> [--dry-run] [--once <pr-number>]
#
# One PR at a time: a git worktree on its branch, a fresh headless Claude
# session with the night-shift skill, one log per PR under
# ${QA_NIGHT_HOME:-~/.qa-night}/runs/<run-id>/. Settings come from the
# "Coverage Pipeline" section of <target>/ai-workflow/project-context.md.
#
# Overrides (tests): QA_NIGHT_GH, QA_NIGHT_CLAUDE, QA_NIGHT_HOME.

set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GH="${QA_NIGHT_GH:-gh}"
CLAUDE="${QA_NIGHT_CLAUDE:-claude}"

usage() { sed -n '4,5p' "$0" | sed 's/^# \{0,1\}//'; }

TARGET=""
DRY_RUN=0
ONCE=""
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --dry-run) DRY_RUN=1 ;;
    --once) ONCE="${2:-}"; shift ;;
    *)
      if [ -z "$TARGET" ]; then TARGET="$1"
      else echo "qa-night: unexpected argument: $1" >&2; exit 1; fi ;;
  esac
  shift
done

if [ -z "$TARGET" ]; then
  echo "qa-night: target path is required" >&2
  usage >&2
  exit 1
fi
if [ ! -d "$TARGET" ]; then
  echo "qa-night: target path not found: $TARGET" >&2
  exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"
CONTEXT="$TARGET/ai-workflow/project-context.md"
if [ ! -f "$CONTEXT" ]; then
  echo "qa-night: project context is missing: $CONTEXT" >&2
  exit 1
fi

cfg() { python3 "$KIT_DIR/bin/lib/pipeline_config.py" --context "$CONTEXT" --key "$1"; }
cfg_optional() { cfg "$1" 2>/dev/null || true; }

READY="$(cfg labels.ready)"
DONE="$(cfg labels.done)"
BLOCKED="$(cfg labels.blocked)"
MODE="$(cfg night.permission_mode)"
TOOLS="$(cfg night.allowed_tools)"
TURNS="$(cfg night.max_turns)"
MINUTES="$(cfg night.timeout_minutes)"
NIGHT_ACTOR="$(cfg_optional night.actor_login)"

if [ "$MODE" = "bypassPermissions" ]; then
  echo "qa-night: bypassPermissions is not allowed" >&2
  exit 1
fi

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${QA_NIGHT_HOME:-$HOME/.qa-night}/runs/$RUN_ID"
mkdir -p "$RUN_DIR/pr"

( cd "$TARGET" && "$GH" pr list --state open --limit 200 \
    --json number,headRefName,isDraft,labels,files ) > "$RUN_DIR/prs.json"

LABELLED="$(python3 -c '
import json, sys
prs = json.load(open(sys.argv[1]))
print(" ".join(str(p["number"]) for p in prs if sys.argv[2] in {l["name"] for l in p.get("labels", [])}))
' "$RUN_DIR/prs.json" "$READY")"

for n in $LABELLED; do
  if [ -n "$ONCE" ] && [ "$n" != "$ONCE" ]; then continue; fi
  ( cd "$TARGET" && "$GH" api "repos/{owner}/{repo}/issues/$n/events" --paginate --jq '.[]' ) \
    > "$RUN_DIR/pr/$n.events.json"
  ( cd "$TARGET" && "$GH" api "repos/{owner}/{repo}/issues/$n/comments" --paginate --jq '.[]' ) \
    > "$RUN_DIR/pr/$n.comments.json"
done

SELECT=(--prs "$RUN_DIR/prs.json" --events-dir "$RUN_DIR/pr"
        --label-ready "$READY" --label-done "$DONE" --label-blocked "$BLOCKED"
        --night-actor "$NIGHT_ACTOR")
if [ -n "$ONCE" ]; then SELECT+=(--only "$ONCE"); fi
SELECTED="$(python3 "$KIT_DIR/bin/lib/select_ready_prs.py" "${SELECT[@]}" 2> "$RUN_DIR/skipped.txt")"
cat "$RUN_DIR/skipped.txt" >&2

if [ -z "$SELECTED" ]; then
  echo "qa-night: nothing to do (run $RUN_ID)"
  exit 0
fi
if [ "$DRY_RUN" = 1 ]; then
  printf '%s\n' "$SELECTED" | while IFS="$(printf '\t')" read -r n branch; do
    echo "would run: #$n ($branch)"
  done
  exit 0
fi

if command -v timeout >/dev/null 2>&1; then TO=(timeout "${MINUTES}m")
elif command -v gtimeout >/dev/null 2>&1; then TO=(gtimeout "${MINUTES}m")
else TO=(); echo "qa-night: no timeout command found; running without a time limit" >&2; fi

PROMPT_TEMPLATE="$KIT_DIR/skills/night-shift/assets/night-prompt.md"
STATUS=0
while IFS="$(printf '\t')" read -r n branch; do
  WT="$RUN_DIR/wt-$n"
  LOG="$RUN_DIR/pr-$n.log"
  echo "qa-night: #$n ($branch) -> $LOG"
  if ! git -C "$TARGET" fetch --quiet origin "$branch" >>"$LOG" 2>&1 \
     || ! git -C "$TARGET" worktree add -B "$branch" "$WT" "origin/$branch" >>"$LOG" 2>&1; then
    echo "qa-night: #$n worktree failed, see $LOG" >&2
    STATUS=1
    continue
  fi
  PROMPT="$(sed -e "s|{{PR}}|$n|g" -e "s|{{BRANCH}}|$branch|g" -e "s|{{RUN_ID}}|$RUN_ID|g" \
                -e "s|{{KIT_DIR}}|$KIT_DIR|g" -e "s|{{TARGET}}|$TARGET|g" "$PROMPT_TEMPLATE")"
  set +e
  ( cd "$WT" && ${TO[@]+"${TO[@]}"} "$CLAUDE" -p "$PROMPT" --add-dir "$KIT_DIR" \
      --permission-mode "$MODE" --allowedTools "$TOOLS" --max-turns "$TURNS" ) >>"$LOG" 2>&1
  CODE=$?
  set -e
  git -C "$WT" fetch --quiet origin "$branch" >>"$LOG" 2>&1 || true
  if [ -z "$(git -C "$WT" status --porcelain)" ] \
     && [ -z "$(git -C "$WT" log --oneline "origin/$branch..HEAD" 2>/dev/null)" ]; then
    git -C "$TARGET" worktree remove "$WT" >>"$LOG" 2>&1 || true
    echo "qa-night: #$n finished (exit $CODE), worktree removed"
  else
    echo "qa-night: #$n left unpushed work, worktree kept: $WT" >&2
    STATUS=1
  fi
  if [ "$CODE" != 0 ]; then STATUS=1; fi
done <<< "$SELECTED"

exit "$STATUS"
```

Then `chmod +x bin/qa-night`.

- [ ] **Step 3: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v` — Expected: all PASS.

- [ ] **Step 4: Amend the spec**

In `docs/superpowers/specs/2026-10-23-coverage-pipeline-design.md`:
- in §4.4 replace `Per PR: verify the label event's actor is a human (`gh api .../issues/<n>/events`), skip
otherwise →` with `Per PR: the selector (bin/lib/select_ready_prs.py) skips it unless the last ready-label event is from neither a bot nor night.actor_login, it has no done/blocked label, no "night-shift run " comment is newer than that event, and no other open PR changes the same files →`;
- in §4.5 table add the row `| night.actor_login | qa-night | login the night shift acts as, when it is a separate account (optional) |`;
- in §6 replace the row `| Ready label applied by a bot or by the night shift | PR skipped |` with `| Ready label from a bot or night.actor_login, a done/blocked label, or a report newer than the label | PR skipped; the night shift itself never adds the ready label |`.

- [ ] **Step 5: Document the launcher in README**

Append to `README.md` a section after `## Hooks`:

```markdown
## Night Shift Launcher

`bin/qa-night <target> [--dry-run] [--once <pr>]` runs the `night-shift` skill
over draft pull requests a human labelled ready, one at a time, each in its own
git worktree and a fresh headless session. Settings come from the target's
`ai-workflow/project-context.md`, section "Coverage Pipeline". Start with
`--dry-run`, then `--once <pr>` while tuning the prompt.
```

- [ ] **Step 6: Run tests and commit**

Run: `python3 -m unittest discover -s tests -v` — Expected: all PASS.

```bash
git add bin/qa-night tests/test_coverage_pipeline.py docs/superpowers/specs/2026-10-23-coverage-pipeline-design.md README.md
git commit -m "feat(night-shift): add qa-night launcher

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: Consumer draft, inventory and behaviour checks

**Files:**
- Create (outside kit git): `/Users/alex/MyRepos/work/ai-qa-workflow-kit-consumers/qa/coverage-pipeline-section.md`
- Modify: `docs/component-inventory.md`

- [ ] **Step 1: Draft the qa repository's section**

Write `.../ai-qa-workflow-kit-consumers/qa/coverage-pipeline-section.md`. Values marked `CONFIRM` need the user's check on the work machine:

```markdown
## Coverage Pipeline

- coverage.uncovered_command: python3 scripts/route_coverage.py --critical
- coverage.detail_command: python3 scripts/route_coverage.py --scenarios <ID> --detail
- coverage.day_batch_size: 3
- requirements.source: Outline pages through the Outline connector; the domain design in the backend checkout at docs/<domain>/<domain>.md
- requirements.inventory_paths: catalog/<domain>/_flows.yaml, catalog/<domain>/_guarantees.yaml
- backend.checkout: CONFIRM (path of the backend checkout on the work machine)
- authoring.skill: catalog-test
- authoring.after_checkpoint_phases: 3 (case steps only, within the confirmed cases), 4, 5, 7, 8, 9
- checks.safe: python3 scripts/check_scenario.py <ID>; python3 -m pytest tests --ignore=tests/tooling --collect-only -q; python3 -m pytest tests/tooling/test_catalog_rules.py -q
- checks.preflight: python3 scripts/catalog_preflight.py --select "<nodeid>" (see catalog-test run-and-report.md)
- run.live_sandbox: python3 scripts/catalog_preflight.py --publish --environment CONFIRM --select "<nodeid>" -- python3 scripts/run_catalog.py --org-mode existing --environment CONFIRM --output out/<run> --select "<nodeid>" --publish --target sandbox
- review.command: /code-review medium origin/main...HEAD (high when framework/, scripts/ or a driver changed)
- labels.ready: afk-ready
- labels.done: afk-done
- labels.blocked: afk-blocked
- night.permission_mode: acceptEdits
- night.allowed_tools: Read,Edit,Write,Grep,Glob,Skill,Bash(python3 *),Bash(git status*),Bash(git diff*),Bash(git log*),Bash(git add *),Bash(git commit *),Bash(git push origin HEAD:*),Bash(gh pr view *),Bash(gh pr diff *),Bash(gh pr list *),Bash(gh pr comment *),Bash(gh pr edit *)
- night.max_turns: 200
- night.timeout_minutes: 120
- night.actor_login:
- heuristics.project_file: ai-workflow/heuristics.md
```

Tell the user: paste it into `<qa>/ai-workflow/project-context.md` before `## Known Constraints`, fix the `CONFIRM` values, and create the three labels in the GitHub repository (an outward-facing write the user does themselves).

- [ ] **Step 2: Record the components**

In `docs/component-inventory.md`, add these rows to the end of the `## Core Architecture Candidates` table:

```markdown
| Coverage backlog | Skill | Kit (`skills/coverage-backlog`) | Computed, never-stored kanban over uncovered inventory units | Coverage command and inventory paths via project context | `adopt` | P1 |
| Requirement grill | Skill | Kit (`skills/requirement-grill`) | One-question-at-a-time alignment before a claim | Authoring skill named via project context | `adopt` | P1 |
| Black-box review | Skill | Kit (`skills/blackbox-review`) | User-side additions without reading code; heuristics files | Product heuristics in an untracked project file | `adopt` | P1 |
| Night shift | Skill + launcher | Kit (`skills/night-shift`, `bin/qa-night`) | AFK implementation of confirmed scenario PRs, sequential, fresh context | Commands, labels, permissions via project context | `adopt` | P2 |
```

- [ ] **Step 3: Behaviour checks (superpowers:writing-skills)**

For `coverage-backlog`, `requirement-grill` and `blackbox-review`, dispatch two general-purpose subagents each over the same scenario - one told to follow `skills/<name>/SKILL.md`, one with no skill - using `/Users/alex/MyRepos/qa` as the read-only target and a project context built from Step 1's draft in a scratch copy. Scenarios:
- backlog: "What should I cover next in the connectors domain?"
- grill: "Grill me on FLOW_CON_0052_R7" (the subagent writes questions only, answers are scripted: "take your recommendation");
- blackbox: proposed mode on the grill output; audit mode on `catalog/connectors/CON-DL-01.yaml`.

Compare: the skilled run must obey every rule in its SKILL.md (read-only, one question per message, no code read in black-box). Any violation → tighten the SKILL.md wording, re-run, re-run the kit tests. `night-shift` is checked only by `bin/qa-night --dry-run` here; its live acceptance (`--once` on a test draft PR) happens on the work machine.

- [ ] **Step 4: Full verification and commit**

Run: `python3 -m unittest discover -s tests -v` — Expected: all PASS.
Run: `bash hooks/skill-size-check.sh` if it accepts no arguments; otherwise `wc -l skills/{coverage-backlog,requirement-grill,blackbox-review,night-shift}/SKILL.md` — Expected: each ≤ 200.

```bash
git add docs/component-inventory.md skills
git commit -m "docs(inventory): record coverage pipeline components

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Report to the user: branch, commits, test output, the consumer files to copy, the labels to create, and that the night shift's live acceptance is still pending on the work machine.
