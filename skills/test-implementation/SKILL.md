---
name: test-implementation
description: Implement and verify automated tests from an explicitly approved Test Design Contract. Use when approved case IDs and exact parameter variants must be translated into project-native tests, traced to code, statically checked, collected, executed in an authorized non-production environment, and recorded back into the contract. Also use to resume pending live verification for an implemented contract. Do not use when the design is missing, awaiting approval, blocked, or materially inconsistent with live project evidence.
---

# Test Implementation

Implement only the approved contract and preserve traceability from case IDs to
code and verification.

## Required Input

Obtain:

- the target project and project context;
- one Test Design Contract;
- artifact status `approved`, or `implemented` only when resuming its pending
  live verification;
- an approval record naming exact case IDs and parameter variants;
- approved assertions, cleanup, constraints, and implementation handoff;
- the project execution policy and configured target environment;
- project-native test structure, reusable components, and verification
  commands.

If approval is missing, ambiguous, or broader than the recorded variants,
return a `missing approval` blocker without editing test code.

## Workflow

### 1. Lock The Approved Scope

Record:

```text
Design artifact:
Approved case IDs and variants:
Approved behavior:
Approved cleanup:
Allowed support changes:
Required verification:
Execution authorization:
```

Treat the approved design as the implementation contract. Do not silently add,
remove, merge, or reinterpret cases.

### 2. Check For Drift

Read the smallest relevant set of current project files. Confirm:

- target paths and reusable fixtures, clients, schemas, page objects, helpers,
  and factories still exist;
- implementation conventions still match project context;
- approved behavior does not conflict with newer controlling evidence;
- required secrets, environment, or capabilities are not being invented.

Repository drift that changes implementation details but preserves approved
behavior may be handled directly. Drift that changes scope, expected results,
actors, parameter variants, assertions, or cleanup is a material design change:
stop implementation and return the contract to `awaiting-approval`.

### 3. Map Cases To Code

Create a traceability map before editing:

| Case ID | Approved variants | Test location | Verification |
|---|---|---|---|
| | | | |

Every approved case and variant must map to test code. Prefer project-native
parameterization when behavior and assertions are shared.

Do not encode the case ID in a test name when that conflicts with local naming
conventions. Preserve traceability in the contract, test metadata, parametrized
IDs, or a concise code comment where appropriate.

### 4. Implement Minimally

- Reuse existing fixtures, clients, schemas, page objects, factories,
  assertions, and helpers.
- Add support code only when an approved case cannot be implemented correctly
  without it.
- Keep support changes within the ownership boundaries named by project
  context and the approved handoff.
- Preserve existing project style and test organization.
- Implement the approved response and cleanup assertions exactly.
- Register cleanup as soon as persistent test data becomes identifiable.
- Do not weaken assertions to make collection or execution pass.
- Do not expose secrets or reproduce environment-file values.

If implementation reveals an unknown expected result, route the claim through
`source-of-truth`. If the answer materially changes the contract, stop and
request renewed approval.

### 5. Verify In Layers

Use project-configured commands and report each layer separately:

1. syntax or static checks;
2. target test collection or discovery;
3. exact approved variants in the configured non-production QA environment
   when project context authorizes autonomous execution;
4. broader execution only when separately authorized.

Collection is not test execution. A collected test is not a passing test.

Approval of the exact contract variants authorizes their implementation,
state-changing execution, and approved cleanup in the project-configured
non-production QA environment when project context enables autonomous
execution. Do not ask for a second approval for this exact scope.

Require separate approval for production, variants outside the approval
record, broader suites, or destructive actions not defined by approved
cleanup. If the configured environment, credentials, or cleanup capability is
unavailable, report an environment blocker instead of asking for duplicate
scope approval.

On failure:

- fix implementation defects within approved scope;
- stop on product/environment failures or contract conflicts;
- preserve the failing command and concise evidence;
- do not change expected results to match an unexpected runtime result.

### 6. Update The Contract

Update the existing Test Design Contract `Implementation` section:

- implemented case IDs and exact variants;
- case-to-test traceability;
- changed files;
- verification commands and outcomes;
- live execution command, environment class, outcome, and cleanup result;
- deferred cases and reasons;
- remaining risks.

Set artifact status:

- keep `approved` when implementation is incomplete or required verification
  has not passed;
- set `blocked` only when project policy uses that state for an implementation
  blocker;
- set `implemented` only when every approved case and variant is implemented
  and the required non-live verification has passed.

When autonomous QA execution is authorized, do not stop after collection:
execute the exact approved variants and record the result before returning.
Do not claim runtime correctness when execution did not complete.

An artifact already marked `implemented` may be resumed for pending live
verification without renewed approval when its Approval section still names
the exact variants and project context authorizes autonomous QA execution.

### 7. Return To The Orchestrator

Report:

```text
Artifact:
Implemented case IDs and variants:
Changed files:
Static verification:
Collection:
Live execution:
Deferred or blocked work:
Artifact status:
Next permitted transition:
```

## Guardrails

- Never implement from `draft`, `awaiting-approval`, `blocked`, or
  `superseded`.
- Never treat conversational intent as approval when the artifact approval
  record is still pending.
- Never implement variants absent from the approval record.
- Never change product expectations, coverage, or cleanup without renewed
  approval.
- Never claim tests passed when they were only collected.
- Never request duplicate approval for exact approved variants in an
  autonomously authorized non-production QA environment.
- Never run against production, expand execution scope, or perform destructive
  actions outside approved cleanup without separate approval.
- Never perform unrelated refactors.
