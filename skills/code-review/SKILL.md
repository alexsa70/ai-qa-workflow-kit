---
name: code-review
description: Review implemented QA automation changes against project context, approved Test Design Contracts, source-of-truth evidence, and verification results. Use after test implementation, live QA execution, bug fixes, or meaningful framework/client/schema/fixture/test changes to find behavioral regressions, contract drift, missing assertions, unsafe cleanup, traceability gaps, or insufficient verification. Do not use to implement fixes or approve unapproved designs.
---

# Code Review

Review QA automation changes as an evidence-backed gate. Prioritize bugs,
contract drift, false positives, unsafe data handling, and missing
verification.

## Required Input

Obtain:

- the target project and project context;
- the review target: changed files, diff, branch, artifact, or explicit path;
- applicable Test Design Contract when the change implements approved cases;
- source-of-truth verdicts or controlling sources referenced by the artifact;
- verification evidence recorded by implementation or supplied by the user;
- project-native review commands or adapter skills when configured.

If the target, artifact, or relevant diff cannot be determined, return a
`missing context` blocker. Do not guess which changes should be reviewed.

## Workflow

### 1. Define Review Scope

Record:

```text
Review target:
Task type:
Project context:
Relevant artifact:
Approved case IDs and variants:
Changed files:
Verification evidence:
Out of scope:
```

Keep scope tied to the latest user request. If the request says to review a
contract implementation, prioritize the approved cases and their support code.

### 2. Load Evidence

Read the smallest sufficient set:

- project context and applicable workflow policy;
- Test Design Contract approval, cases, implementation, and verification
  sections;
- source-of-truth verdicts named by the contract;
- changed tests and narrowly required support code;
- current diff or user-provided patch;
- verification output or commands, when available.

Treat runtime output as evidence of actual behavior, not as proof of intended
behavior. If intended behavior is unclear or conflicts with implementation,
route that claim through `source-of-truth`.

### 3. Select Review Lenses

Always check:

- approved case IDs and exact variants are implemented and not broadened;
- response status, body/schema, business assertions, headers, error contract,
  side effects, and cleanup match the contract;
- every state-changing test registers cleanup as soon as the persistent ID is
  available;
- traceability maps each approved variant to a test location and verification;
- verification evidence distinguishes static checks, collection, live
  execution, and cleanup;
- tests cannot pass while the product behavior under review is wrong;
- no secrets, hardcoded environment values, internal-only APIs, or unrelated
  refactors are introduced;
- support code remains within the allowed paths and project conventions.

When project context names stack-specific review skills or commands, use them
as adapters after applying this contract-level review. Stack adapters may add
findings, but they must not override the approved contract or source hierarchy.

### 4. Verify Findings Before Reporting

For each potential finding:

- identify the exact rule or approved expectation it violates;
- inspect the relevant file and line, not just a summary;
- confirm the scenario can occur from the implemented code path;
- distinguish implementation defect, product defect, environment issue, and
  missing evidence;
- avoid reporting style preferences unless they create a real risk.

If evidence is insufficient, list an open question or verification gap instead
of a finding.

Do not run live, destructive, production, or broader-suite checks unless the
project context and user request authorize that exact scope. Static analysis,
diff inspection, and collection are allowed when project policy permits them.

### 5. Report Findings First

Use this order:

```text
Findings:
- [Severity] File:line - Problem. Impact. Fix.

Open questions:

Verification reviewed:

Scope reviewed:

Summary:
```

Severity:

- `P0`: test or framework can cause destructive damage, leak secrets, or block
  all usage.
- `P1`: approved behavior is not tested, assertions can false-pass, cleanup is
  unsafe, or implementation materially conflicts with contract/source.
- `P2`: meaningful reliability, maintainability, traceability, or verification
  gap.
- `P3`: minor issue with low behavioral risk.

If no findings are found, say so directly and still report residual risks or
unverified areas.

## Guardrails

- Never modify code, artifacts, approval records, or expected results during
  review unless the user explicitly asks for fixes.
- Never approve a design or implementation; report review outcome only.
- Never treat collection as test execution.
- Never treat a runtime success as proof of intended behavior when the contract
  or authority chain says otherwise.
- Never invent source evidence, verification output, or line numbers.
- Never bury findings below a long summary.
- Never expand review scope beyond the requested target without saying why.
