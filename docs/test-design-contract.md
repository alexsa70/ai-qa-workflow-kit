# Test Design Contract

## Purpose

The Test Design Contract is the durable boundary between research, test
design, approval, implementation, and verification.

It exists when implementation depends on an agreed scope or when approval must
survive the current conversation. Small exploratory questions that do not lead
to implementation do not require this artifact.

## Ownership

The QA Orchestrator decides when the artifact is required and enforces its
gates. The `test-design` skill defines the repeatable procedure for creating
and updating it.

The artifact belongs to the connected project, not to the workflow kit.
Projects choose its concrete storage path in `project-context.md`.

The artifact is an implementation contract, not a research report. Keep
source investigation in `source-of-truth` output and cite only the evidence
needed to approve each coverage decision.

## Lifecycle

```text
draft
  |
  | required facts resolved and design complete
  v
awaiting-approval
  |
  | explicit approval recorded
  v
approved
  |
  | approved cases implemented and verified
  v
implemented
```

`blocked` may be entered from any incomplete state when a required fact,
capability, environment, or decision is unavailable. `superseded` is terminal
and points to the replacement artifact.

## Gates

### Entry Gate

Before design begins:

- the target project and scope are known;
- project context is available;
- applicable source and authority policy is available;
- unknown expected behavior is routed through `source-of-truth`.

### Approval Gate

Before implementation:

- artifact status is `awaiting-approval`;
- behavior-affecting unknowns are resolved;
- scope, cases, assertions, and cleanup are explicit;
- request actors are separated from target roles or states;
- all required actor-target combinations are selected or explicitly excluded;
- independent coverage dimensions are fully crossed or reduced with evidence;
- source vocabulary and contract conflicts are resolved;
- cleanup contains only confirmed observable behavior;
- every API case has a complete response contract;
- the user records an approval decision;
- status is changed to `approved`.

Approval applies only to the recorded case IDs and conditions.

## Steps And API Response Contract

A case is a numbered sequence of steps. A single-action case is still a
one-step list; add steps only when more than one request or observable action
is needed to prove the behavior (for example: create, then fetch, to confirm
persisted state).

Every step that issues a request states an example request (method, path, and
an illustrative payload when a body is sent) and its own pass criteria — that
step's API Response Contract:

- expected HTTP status;
- expected message or key response body field, or explicit absence of body;
- response schema when applicable;
- contractually relevant headers;
- semantic assertions for business-significant fields (value checks);
- error contract for negative responses;
- side effects or persistence verification for state-changing operations.

Expected HTTP status is mandatory for every request step. Other fields may be
`not applicable` only with a recorded reason. Schema validation proves
structure and types; it does not replace semantic assertions for values
important to the behavior under test.

Example payloads illustrate request shape; they are not proof of behavior.
Build them from a confirmed schema, fixture, or evidence already cited for the
case. Never present an invented value as confirmed; mark illustrative
placeholders clearly.

Concrete project requirements, assertion helpers, schema locations, and
exceptions belong in project context.

## Actor And Target Matrix

Permission-dependent design must distinguish:

- the request actor performing the operation;
- the target entity affected by the operation;
- the target role or state being assigned or changed.

The design must derive allowed combinations from evidence. Combinations with
identical behavior should be parameter variants of one logical case.
Combinations with different expected behavior require separate cases.

## Combination Coverage

Selected independent dimensions form a coverage matrix. The default is to
cover their cross-product. A smaller representative set is allowed only when
the artifact records omitted combinations, evidence of behavioral equivalence,
and accepted residual risk.

Coverage in one case does not automatically justify omitting the same value
from another independent dimension.

## Source Conflicts

Different names or contracts for the same role, field, route, state, or result
must be resolved before approval. The artifact may not silently choose one
source value. An unresolved conflict sets the artifact to `blocked`.

## Cleanup Evidence

Cleanup assertions must be supported by the source contract. Asynchronous
initiation does not imply a confirmed polling interval, timeout, terminal
status, or eventual response contract. When completion is not confirmed, test
only initiation and record the residual risk.

## Concision Rules

- Keep cases as the dominant part of the artifact.
- Cite evidence; do not retell source implementation.
- Define shared setup, response expectations, and cleanup once.
- Do not repeat complete assertions when a case only changes one dimension.
- Keep implementation handoff to reusable components, required changes, and
  verification commands.
- List approval scope as exact case IDs and parameter values.

### Completion Gate

Before status becomes `implemented`:

- approved cases can be traced to changed files;
- the smallest relevant verification has passed;
- skipped or deferred cases have recorded reasons;
- remaining risks are explicit.

## Material Changes

After approval, any change to the following requires renewed approval:

- in-scope or out-of-scope behavior;
- case inventory or its step sequence;
- expected results;
- a step's pass criteria (its API response contract);
- actor-target matrix or permissions;
- assertions;
- persistent data or cleanup;
- implementation constraints that change observable coverage.

Editorial corrections and implementation-path details that preserve approved
behavior do not require renewed approval.

## Portability Rules

The reusable template must not contain:

- repository-specific paths;
- framework-specific syntax;
- fixed roles, markers, fixtures, or environments;
- a universal source authority order;
- invented expected behavior.

Those values come from the connected project's context and evidence.

## Initial Compatibility

Existing project documents using `proposed`, `approved`, `implemented`, and
`blocked` do not need immediate migration. During adoption:

- `proposed` maps to `draft` or `awaiting-approval`, depending on readiness;
- `approved`, `implemented`, and `blocked` keep their meanings;
- approval evidence and stable case IDs must be added before new
  implementation begins.
