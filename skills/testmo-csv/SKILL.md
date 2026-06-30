---
name: testmo-csv
description: Generate a Testmo-import CSV from existing automated tests on demand. Use when the user wants to export, convert, or turn ready tests (a test file, a directory, or a named set of tests) into a CSV for import into Testmo / TestMO — covering folder, name, description, preconditions, steps, expected results, automated flag, and tags. Do not use to write or modify tests, to design new coverage, or to push to Testmo via API; this skill only produces the import CSV.
---

# Testmo CSV

Turn ready automated tests into a Testmo-import CSV. Read tests as evidence;
never invent steps, assertions, or preconditions that are not in the test.

## Required Input

Obtain:

- the scope: one test file, a directory, or a named list of tests;
- the target project and project context (test conventions, output location);
- the project's test annotation style (how name, steps, markers are expressed).

If scope or project context is missing, return a blocker to the QA Orchestrator.

## Output Format

Emit one CSV with this exact header (the proven Testmo-import column set):

```text
Name,Automated,Description,Expected,Folder,Pre-conditions,State,Steps,Tags
```

See `assets/testmo-csv-format.md` for quoting rules, value rules, and a worked
example. One test = one row.

## Field Mapping

| Column | Source in the test | Rule |
|---|---|---|
| `Folder` | the test **file name** | `test_<snake>.py` → Title Case of `<snake>` (e.g. `test_conversation_editing.py` → `Conversation Editing`). One folder per file. |
| `Name` | the test title | The human title (`@allure.title(...)` in pytest+allure). Fallback: humanized function name. |
| `Description` | what the test verifies | One-to-two sentences describing the behavior under test, derived from the test docstring / title / body. Not a step list. |
| `Expected` | the assertions | The expected outcome(s): status codes, response fields, side effects asserted in the test. |
| `Pre-conditions` | setup / fixtures | The state required before the action (auth role, owned resource, seeded data) from fixtures, factory setup, and the first setup steps. |
| `State` | — | `Active`. |
| `Steps` | the test actions | Numbered list (`1. … 2. …`) from the test's step titles (`with allure.step("…")`) or the logical actions in body order. |
| `Automated` | — | `Yes`. |
| `Tags` | pytest markers | `api-automation` plus polarity: `positive` or `negative`, decided from the `positive`/`negative` marker (or, if absent, from whether the test asserts a 2xx success or a 4xx/5xx rejection). Comma-separated in one cell, e.g. `api-automation,negative`. |

Project context may override the `Folder` derivation (e.g. prefix a service:
`Files Service/Conversation Editing`) and the tag set. Follow project context
when it specifies a convention; otherwise use the rules above.

## Workflow

### 1. Resolve Scope

List the concrete test items in scope (file paths and, where given, specific
test functions). Confirm the project's annotation conventions from project
context before extracting.

### 2. Extract Mechanical Fields

For each test, extract the fields that come straight from structure:
`Folder`, `Name`, `Steps`, `Tags`, `Automated`, `State`.

For a pytest + allure project, `scripts/tests_to_testmo_csv.py` does this
deterministically (parses `@allure.title`, `with allure.step(...)`, and
`positive`/`negative` markers). Run it to produce a draft CSV, then refine the
judgment fields. For other stacks, extract the same fields by reading the test.

### 3. Fill Judgment Fields

`Description`, `Pre-conditions`, and `Expected` require reading the test body:

- `Description` — the behavior the test confirms, in plain language.
- `Pre-conditions` — required state from fixtures, factory setup, and setup
  steps. Include only what the test actually establishes.
- `Expected` — the asserted outcome: status code, response/body fields, and any
  side-effect or cleanup assertion the test makes.

Do not copy implementation code into these cells. Do not assert behavior the
test does not check. If a test's expected result is unclear from the code, mark
that cell `TODO: confirm` rather than guessing.

### 4. Build And Validate The CSV

- Write the header exactly as specified.
- Quote any cell containing a comma, quote, or newline; escape `"` as `""`.
- One row per test; stable row order (file, then definition order).
- Validate the file parses (e.g. load it back with a CSV reader) and the column
  count matches the header before declaring done.

### 5. Write And Report

Write the CSV to the project-configured Testmo-import location. Report:

```text
Scope:
Tests exported:
Output file:
Folders produced:
Rows with TODO/unconfirmed cells:
Next action:
```

## Guardrails

- Read-only over tests. Never edit a test to make extraction easier.
- Never invent steps, preconditions, assertions, or expected results absent from
  the test.
- Never set `Automated` to anything but `Yes` (this skill exports automated
  tests); if a target test is not actually automated, exclude it and say so.
- Keep `positive`/`negative` faithful to the test's real assertion (success vs
  rejection), not to its name.
- Do not push to Testmo or call any Testmo API; this skill only writes a CSV.
- Do not deduplicate or rename against live Testmo state; folder/title hygiene
  against existing Testmo is a separate step.
- This skill's column set and procedure are the single source of truth for the
  Testmo CSV. When invoked, they take precedence over any global or user-level
  `CLAUDE.md` TestMO/CSV column preference. Do not substitute global columns
  (e.g. `Priority` / `Type`) or build the CSV inline "from memory"; use this
  skill's header and the extractor. Project context may extend the column set
  only when it explicitly defines a project Testmo convention.
