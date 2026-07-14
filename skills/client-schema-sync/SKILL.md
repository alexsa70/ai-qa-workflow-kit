---
name: client-schema-sync
description: Refresh the project's backend checkout, detect changes to the backend's public API contract since the last synced revision, and reconcile the project's API clients and schemas against that contract under explicit per-item approval. Use when the user says "sync clients with backend", "check backend for contract changes", "update clients and schemas", "pull backend and diff contracts", "did the API change", or a similar request to refresh generated or hand-maintained API clients and schemas from a live backend repository. Requires project context to define a backend repository path, API client location, schema location, a contract diff mechanism, and a sync-state location. Do not use this to design test coverage (use test-design), implement tests (use test-implementation), or resolve unknown product behavior unrelated to contract sync (use source-of-truth).
---

# Client/Schema Sync

Keep project API clients and schemas aligned with the backend's current
public contract, without silently absorbing backend changes into test code.

## Required Input

Obtain from project context:

- the backend repository path and its git remote/branch conventions;
- whether refreshing the backend checkout (fetch and fast-forward pull) is
  pre-authorized for this skill, or requires approval before every run;
- the API client location and the schema location;
- the contract diff mechanism: a command or pipeline that compares two git
  refs of the backend and reports added, removed, or modified endpoints;
- the sync-state location that records the backend revision the clients and
  schemas were last reconciled against.

If the backend repository path, client location, schema location, contract
diff mechanism, or sync-state location is missing, return a blocker to the QA
Orchestrator instead of guessing a path or inventing a comparison method.

## Workflow

### 1. Refresh The Backend Checkout

- Read the sync-state file for the last-synced backend commit. If it is
  missing entirely (first run), say so and ask the user to confirm or supply
  a starting revision before diffing against the full history.
- Inspect state before touching anything: working-tree status, current
  branch, and ahead/behind the configured remote.
- If the working tree is dirty or on an unexpected branch, stop and report;
  do not stash, reset, or switch branches.
- If project context pre-authorizes this skill's refresh, fetch the
  configured remote and fast-forward only. Otherwise request approval first,
  exactly as project policy requires.
- If the pull is not a fast-forward (diverged history), stop and report the
  divergence; never force, rebase, or merge.
- Record the before/after revision for the report.
- Never modify anything else in the backend checkout. Beyond this refresh
  step it is read-only source of truth.

### 2. Diff The Contract Since Last Sync

- Run the project-configured contract diff mechanism from the last-synced
  revision (recorded in sync-state) to the refreshed revision.
- Scope the diff to the services or paths relevant to the project's existing
  clients and schemas, unless the user asks for a full-repository scan.
- Read the mechanism's structured output (for example a diff manifest or a
  per-service change list); do not re-derive the diff by hand when a
  configured mechanism exists.
- If the diff mechanism is unavailable (missing dependency, missing branch,
  missing binary), stop and report the exact missing capability. Do not fall
  back to reading route handlers by hand as a silent substitute unless
  project context explicitly allows that fallback.

### 3. Compare Against Existing Clients And Schemas

Read the project's existing clients and schemas at their configured
locations. For every contract change reported in step 2, classify it as:

- **changed** — an endpoint the project already has a client/schema for, and
  the reported change affects path, method, fields, types, required-ness,
  status codes, or the auth/permission guard;
- **new** — an endpoint with no corresponding client/schema yet, reported as
  added since the last sync;
- **removed** — an endpoint a client/schema currently covers, reported as
  removed since the last sync;
- **not applicable** — a reported change outside the scope of existing
  clients/schemas (an endpoint the project has never automated).

Ignore changes that do not affect contract shape (comments, internal
refactors, non-public routes) when the diff mechanism can distinguish them.

### 4. Report Findings Before Changing Anything

Report, without modifying any file yet:

```text
Backend revision: <last synced> -> <current>
Contract changes reviewed: <count>
Changed (affects existing client/schema): <list, before/after shape>
New (no client/schema yet): <list>
Removed (client/schema now stale): <list>
Not applicable (out of current scope): <count>
Affected files: <clients/schemas that would need edits>
```

If nothing relevant changed, say so, update the sync-state revision (the
comparison itself is confirmed current even with zero relevant changes), and
stop — do not touch client or schema code.

### 5. Request Approval Before Updating

- Present the exact proposed edit per file: the client method signature or
  schema field being added, changed, or removed.
- Wait for explicit approval naming which changed/new/removed items to
  apply. Do not update client or schema code without it.
- An item the user does not approve stays as reported; record it as a known
  gap rather than silently applying or silently dropping it.
- Removing or renaming a client method or schema field requires explicit
  confirmation even when the backend confirms the endpoint is gone — a test
  may still reference it.

### 6. Apply Approved Updates Only

- Update only the approved client methods and schema fields; keep unrelated
  code untouched.
- Preserve existing naming, typing, and project conventions.
- Do not modify tests, factories, or fixtures. Flag files that reference a
  changed client/schema as `possibly affected` for a follow-up `test-design`,
  `test-implementation`, or `code-review` pass — this skill does not update
  tests.
- Do not weaken, remove, or loosen an existing assertion-relevant field to
  make an update easier to apply.

### 7. Update Sync State

After applying (or explicitly deferring) the reviewed changes, update the
sync-state file to the current backend revision, and record which changes
were applied vs. deferred. Do not advance the recorded revision past changes
that were never actually reviewed (for example if the diff mechanism failed
partway through a service).

### 8. Return To The Orchestrator

Report:

```text
Backend revision: <before> -> <after>
Contract changes: changed / new / removed / not applicable counts
Approved updates applied:
Deferred or rejected updates:
Files changed:
Tests or fixtures possibly affected (not modified):
Sync-state updated to:
Next permitted action:
```

## Guardrails

- Never force-push, force-pull, hard-reset, or rebase the backend checkout.
- Never modify backend application code; it is read-only source of truth.
- Never update a client or schema without explicit per-item approval.
- Never delete or rename a client method or schema field without explicit
  confirmation, even when the backend confirms removal.
- Never modify test files, factories, or fixtures; hand affected ones to
  `test-design`, `test-implementation`, or `code-review`.
- Never invent an endpoint, field, type, or status code not observed in the
  diff mechanism's output or the backend source.
- Never advance the sync-state revision past changes that were not actually
  reviewed.
- Treat a successful response as evidence of shape only; permission and
  business-rule questions still resolve through `source-of-truth` and the
  project authority order, not from this skill's diff alone.
- If the backend refresh is not pre-authorized by project context, request
  approval before pulling instead of running it silently.
