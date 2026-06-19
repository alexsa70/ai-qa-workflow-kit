---
name: test-design
description: Create or update a concise, evidence-based Test Design Contract before automated test implementation, and propose new test coverage from a requirement source. Use when a QA request requires defining scope, actor-target role combinations, coverage, test cases, expected results, API response assertions, cleanup, or an approval-ready implementation handoff, or when the requirement arrives as an Outline document link, a Jira issue, a Testmo case or run, or free-text instructions that must be turned into a proposed design. Also use when existing proposed test cases must be normalized into a durable approved design. Do not use for writing test code, executing tests, or resolving unknown product behavior without source-of-truth.
---

# Test Design

Produce a durable, approval-ready test design without implementing tests.

Keep the artifact case-focused. Record only facts and decisions needed to
understand, approve, and implement the cases. Do not turn it into a research
report.

## Required Input

Obtain:

- the user objective;
- the requirement source (see `Requirement Intake`);
- target project and project context;
- intended test level or target area when known;
- available evidence and applicable authority policy;
- the target project's artifact location;
- existing tests, fixtures, clients, page objects, schemas, or design artifacts
  relevant to the requested scope.

If the target project, artifact location, or required context is missing, return
a blocker to the QA Orchestrator.

## Requirement Intake

A requirement may arrive in any of these forms. Resolve it to normalized,
attributed evidence before designing cases.

- **Outline document link**: a knowledge-base page describing a feature,
  decision, or behavior.
- **Jira issue**: a ticket, story, bug, or epic key or URL.
- **Testmo case or run**: an existing manual or automated case, suite, or run.
- **Free text**: instructions written directly by the user.

Intake source priority is `requirement input`, not `controlling source`. A
requirement source states *what the user wants covered*; it does not by itself
prove *how the product behaves*. Expected behavior taken from any source is a
claim until confirmed against the project authority order through
`source-of-truth`.

Use the project context to read each source:

- Read an Outline page, Jira issue, or Testmo entry only through a connector,
  command, or path that project context authorizes. If no authorized access
  exists, ask the user to paste the relevant content and record it as
  `user-provided`.
- Never invent ticket contents, acceptance criteria, or Testmo steps that were
  not retrieved or pasted.
- Preserve the source identifier (Outline URL, Jira key, Testmo case ID) for
  traceability and for the implementation handoff.

See `assets/intake-sources.md` for per-source handling, mixed-source rules, and
a claim ledger format.

## Workflow

### 1. Resolve The Requirement Source

Record the intake before any design work:

```text
Source type:        outline | jira | testmo | free-text | mixed
Source reference:   <url / issue key / case or run id / "user-provided">
Access method:      <connector / command / path / pasted by user>
Retrieved:          yes | no (and why)
Stated requirement: <one-paragraph normalized summary>
Stated expected behavior (claims): <bulleted, each marked unverified>
Stated scope hints: <areas, actors, endpoints, screens named by the source>
Out-of-scope notes: <anything the source explicitly excludes>
Open questions:     <ambiguities the source does not resolve>
```

Rules:

- Split the source into a `requirement` (what to cover) and `claims` (asserted
  behavior). Mark every claim `unverified` until `source-of-truth` confirms it.
- For a Testmo case, treat existing steps and expected results as *prior
  design*, not as confirmed product behavior; reconcile them with the
  controlling source before reuse, and preserve the Testmo ID for the case.
- For a Jira issue, separate acceptance criteria (requirement) from comments and
  speculation (context only).
- For free text, restate the requirement back in normalized form so scope is
  explicit before approval.
- If the source names behavior that conflicts with project authority, do not
  silently pick one. Route the conflict through `source-of-truth`.

Then continue to establish the contract.

### 2. Establish The Design Contract

Record:

```text
Objective:
Scope:
Exclusions:
Evidence:
Open decisions:
Constraints:
```

Keep the scope narrow enough to approve and implement as one coherent unit.

### 3. Resolve Behavior-Affecting Unknowns

Identify unknowns that can change:

- expected behavior;
- actors, roles, or permissions;
- inputs, outputs, or schemas;
- environment or configuration;
- assertions;
- persistent data or cleanup;
- inclusion or exclusion of a case.

Route these claims through `source-of-truth`. Do not invent an expected result
or infer product intent from existing tests unless project policy makes those
tests authoritative.

If a required claim is `unresolved`, set the artifact to `blocked`. If it is
`provisional`, follow the confidence gate defined by project context.

### 4. Inspect Existing Test Architecture

Read only the smallest relevant set of project files. Identify:

- existing naming and organization;
- reusable fixtures, clients, page objects, helpers, and schemas;
- markers, projects, suites, or test levels;
- data creation and cleanup patterns;
- allowed static, collection, isolated, and live verification commands.

Treat implementation as evidence of repository convention, not automatically
as evidence of intended product behavior.

### 5. Build The Coverage Model

Select only dimensions relevant to the request, such as:

- valid and invalid input partitions;
- boundaries and transitions;
- request actors and permissions;
- target subject type, role, or state;
- resource state or lifecycle;
- configuration or environment;
- positive, negative, and failure behavior;
- response, schema, UI state, side effects, and cleanup;
- regression risk.

Use equivalence partitions and boundary values when the evidence defines
classes or boundaries. Do not generate combinations mechanically. Prefer the
smallest set that covers distinct behavior and meaningful risk.

Record exclusions and explain why they are outside the current contract.

Identify which selected dimensions are independent. Cover the cross-product of
independent dimensions unless evidence proves that a smaller representative
set preserves the intended risk coverage. A reduction must state:

- which combinations are omitted;
- why their behavior is equivalent;
- which evidence supports the equivalence;
- which residual risk is accepted.

Do not select one representative value merely because another case already
covers the remaining values in a different dimension.

For permission-dependent operations, always distinguish:

- **request actor**: the identity and role performing the operation;
- **target subject**: the entity being created, changed, viewed, or deleted;
- **target role or state**: the role/state assigned to or held by the target.

Never assume the request actor role and target role are the same. Use evidence
to enumerate allowed actor-target combinations. If combinations share the same
behavior, parameterize one logical case and list all mandatory variants. If
expected behavior differs, create separate cases.

Normalize evidence vocabulary before building cases. If sources use different
names for the same role, state, field, route, or result, resolve the conflict
through `source-of-truth`. An unresolved naming or contract conflict blocks the
artifact; do not choose one spelling silently.

### 6. Define Test Cases

Assign stable IDs such as `TC-001`.

For every case specify:

- target and priority;
- request actor;
- target role/state variants when applicable;
- essential preconditions and test data;
- action;
- observable assertions;
- cleanup;
- evidence reference.

Do not include a case whose expected result is unresolved.

For every API case, define an explicit API Response Contract:

- expected HTTP status;
- expected body shape or absence of body;
- response schema when the response is structured and a contract is available;
- required headers when contractually relevant;
- field-level assertions for business-significant values;
- error body and error fields for negative cases;
- observable side effects or persistence checks when the operation changes
  state.

Expected HTTP status is always mandatory. Every other field must contain a
verified expectation or `not applicable` with a reason. Do not treat successful
deserialization or schema validation as sufficient when important response
values require semantic assertions.

Resolve unknown status codes, schemas, error contracts, response fields, or
side effects through `source-of-truth`. An API case with an incomplete or
unresolved response contract cannot move to `awaiting-approval`.

Define cleanup only from confirmed evidence. Do not add polling, retries,
timeouts, completion states, or terminal assertions unless the source contract
defines the observable state and the project context permits the check. When
an operation is asynchronous and only initiation is confirmed, assert
initiation and record residual cleanup risk.

Avoid repetition:

- define shared setup, response rules, and cleanup once;
- let cases reference shared rules;
- cite a source once unless a different claim needs another citation;
- keep implementation file lists and helper changes in a short handoff;
- do not copy source code behavior into narrative paragraphs.

### 7. Create Or Update The Artifact

Use `../../templates/test-design-contract.md`.

Store the artifact at the project-configured location. Preserve stable case IDs
when updating an existing artifact.

Set status:

- `draft` while research or case definition is incomplete;
- `blocked` when a required fact, capability, environment, or decision is
  missing;
- `awaiting-approval` only when behavior-affecting unknowns are resolved and
  source conflicts are resolved, the selected coverage matrix is complete or
  its reduction is evidenced, and the design is complete enough for a user
  decision.

Never set `approved` without an explicit recorded user decision.

### 8. Request Approval

Present:

- scope and exclusions;
- case IDs and mandatory parameter variants;
- unresolved risks or conditions;
- the exact decision requested.

Enumerate approval scope explicitly, for example:

```text
TC-001: actor=admin x target_role=[user, admin]
TC-002: actor=admin x target_role=[user, admin] x image=png
```

Do not use ambiguous phrases such as `all listed variants`, `all indicated
cases`, or `the cases above`.

Approval applies only to recorded case IDs and conditions. Material changes to
approved behavior, scope, actors, assertions, or cleanup require renewed
approval.

### 9. Return To The Orchestrator

Report:

```text
Artifact:
Status:
Requirement source:
Confirmed scope:
Case IDs:
Evidence:
Unverified claims from source:
Unknowns or risks:
Approval state:
Next permitted transition:
```

The QA Orchestrator decides whether implementation may begin.

## Guardrails

- Do not write or modify automated test code.
- Do not run live tests during test design. The approved contract and project
  policy determine whether `test-implementation` executes them autonomously.
- Do not broaden scope merely to maximize case count or coverage metrics.
- Do not duplicate cases that exercise the same behavior and risk.
- Do not prescribe a framework pattern that conflicts with project context.
- Do not approve an API test design that lacks an explicit response contract.
- Do not move to approval with an unresolved source conflict.
- Do not invent cleanup completion behavior.
- Do not omit an independent coverage combination without evidence.
- Do not treat a requirement source (Outline, Jira, Testmo, free text) as proof
  of product behavior; confirm asserted behavior through `source-of-truth`.
- Do not invent the contents of a ticket, document, or Testmo case that was not
  retrieved through an authorized access method or pasted by the user.
- Do not hardcode credentials, secrets, environment values, or test data not
  authorized by project policy.
- Do not mark an artifact `implemented`; implementation and verification own
  that transition.
