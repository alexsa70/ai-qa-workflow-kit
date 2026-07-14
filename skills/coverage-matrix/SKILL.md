---
name: coverage-matrix
description: Build a per-endpoint test-coverage matrix (an .xlsx workbook, one Summary sheet plus one sheet per endpoint) from an automated test suite and an authoritative endpoint list, so uncovered endpoints and per-endpoint test counts are visible at a glance. Use when a QA request asks to map which API endpoints have tests, audit coverage of a service or the whole API, produce or refresh a coverage/monitoring spreadsheet from the repo, or fold end-to-end/system tests into an existing coverage view. The endpoint list comes from a source of truth (an Outline/Confluence API doc, an OpenAPI spec, or a hand-listed set). Do not use for authoring new tests (see test-design / test-implementation), for pass/fail reporting, or for coverage of non-HTTP surfaces without adapting the client-call detection.
---

# Coverage Matrix

Turn "which endpoints are tested?" into a durable, reviewable workbook derived
from the repository itself — never from guesswork. Coverage is computed by
statically reading the test suite (pytest collection + AST) and mapping each test
to the endpoint of the API-client method it calls.

The deliverable is one `.xlsx` per service (or per logical group): a **Summary**
sheet (endpoint, method, path, test counts) plus one sheet per endpoint listing
`File name / Test name / Test type / Testmo ID`. Endpoints with zero rows are the
coverage gaps — they stay visible as empty sheets, they are not dropped.

## When To Use

- "Which endpoints of `<service>` are not covered?" / "audit our API coverage".
- "Fill / refresh the coverage spreadsheet from the current tests."
- "Fold the system (E2E) tests into the coverage files."
- Establishing a coverage baseline before a gap-closing push.

For turning a gap into an actual test, hand off to `test-design` +
`test-implementation`. This skill only *measures*.

## Required Input

1. **Repo + test dirs** — the suite to read, and which directory(ies) hold the
   tests for this service.
2. **Endpoint list (source of truth)** — every endpoint the service exposes, in
   documentation order, as `endpoints.json`:
   ```json
   [["/api/agents/create", "Create Agent", "POST"],
    ["/api/agents/get",    "Get Agent",    "POST"]]
   ```
   Each entry is `[path, section_title, method]`. `section_title` becomes the
   sheet name (truncated to Excel's 31-char limit). Pull it from the project's
   API doc (Outline/OpenAPI) — do not invent endpoints. Include endpoints with no
   tests; their empty sheets are the point. See `assets/endpoints-config.md`.

Keep all project-specific values (repo path, client-module glob, endpoint paths,
doc URLs) in the invocation / project-context — never bake them into the skill.

## Workflow

### 1. Assemble The Endpoint List
Fetch the service's endpoints from the source of truth and write `endpoints.json`
in doc order. Reconcile against reality: drop endpoints the backend removed, add
ones the docs omit (verify against the client/code), and note either as a doc gap.

### 2. Run The Builder
`scripts/build_coverage_matrix.py` does the mechanical work:

```
COVERAGE_REPO=<repo> \
python scripts/build_coverage_matrix.py \
    <out.xlsx> <test_dirs> <endpoints.json> [<extra_test_files>] [<system_dirs>]
```

- `COVERAGE_REPO` — repo root (default: cwd). `COVERAGE_CLIENTS_GLOB` overrides the
  client-module glob (default `src/clients/*.py`).
- `test_dirs` / `system_dirs` — comma-separated, repo-relative or absolute.

It: parses each client module for `self.api.post/get("/path")` → `method→path`;
runs `pytest --collect-only`; AST-reads each test's `@allure.title`, markers,
`@parametrize` (incl. `pytest.param(..., id=)`) testmo ids, and the client methods
it calls; then attributes each test to an endpoint.

### 3. Understand The Attribution Rules (so you can sanity-check output)
- The client method a test calls **is** the endpoint it exercises.
- A test hitting several endpoints (e.g. create + cleanup-delete, or "act then
  GET to verify") is disambiguated by the **test name**: endpoint path-token
  first, then section-title words. This keeps a `set_priority_table` test that
  also calls `org/get` on the Set-Priority sheet, not on Get-Organization.
- Helper/fixture-driven tests with no direct client call inherit their file's,
  then the service's, dominant endpoint.
- **System/E2E tests** (the `system_dirs` arg) get **multi-attribution**: each is
  added to *every* in-scope endpoint it calls, tagged test-type `system`, so one
  E2E flow shows as coverage on each endpoint it truly exercises.

### 4. Verify, Don't Trust Blindly
Read the printed summary + `UNASSIGNED` list. Zero unassigned is the goal. Spot-
check a couple of sheets: are cleanup calls stealing rows? did an f-string path
(e.g. `/api/files/{file_id}`) fail to match its config entry? Fix the config path
to match what the client actually builds, or adjust the test name, and rerun.

### 5. Report Gaps Honestly
Summarize covered vs uncovered per endpoint. Classify remaining gaps (e.g.
super-admin-only, connector CRUD, non-REST/WebSocket) so "uncovered" is not
mistaken for "forgotten". If you build a cross-service overview, compute it live
from the workbooks; distinguish `unit` from `system-only` coverage.

## Guardrails

- **Repo is the source for coverage; the doc is the source for the endpoint set.**
  Never report an endpoint as covered/uncovered without the workbook backing it.
- **Do not drop uncovered endpoints** — empty sheets are the deliverable's value.
- **Do not loosen or invent** to make numbers look better; a system test that only
  calls an endpoint as cleanup is still real coverage, but label it `system`.
- **Keep the skill portable** — no hardcoded repo/venv/output paths in the script
  or config; pass them per invocation.
- The client-call detection assumes an httpx-style `self.api.post/get("/path")`
  client. For a suite that wraps requests differently, adapt `first_path` — say so
  rather than silently producing empty coverage.
