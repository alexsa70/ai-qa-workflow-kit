# Test Design: <feature or target>

## Contract

- Type: `test-design`
- Status: `draft`
- Project:
- Requirement source: `<outline url | jira key | testmo id | free-text | none>`
- Scope:
- Exclusions:
- Evidence:
- Open decisions: `none`
- Next transition:

Statuses: `draft`, `awaiting-approval`, `approved`, `implemented`, `blocked`,
`superseded`.

Use short evidence citations. Keep detailed research in a separate
`source-of-truth` verdict when it must remain auditable.

## Coverage

| Dimension | Selected values | Excluded values and reason |
|---|---|---|
| Request actor | | |
| Target role/state | | |
| Input or state partition | | |

For permission-dependent behavior, always separate the request actor from the
target entity and its assigned role/state. List every required actor-target
combination. Parameterize combinations with identical expected behavior.

- Independent dimensions:
- Required combinations:
- Omitted combinations:
- Reduction evidence and accepted residual risk: `not applicable`

Do not omit an independent combination without evidence that the reduced
matrix preserves the intended coverage.

## Shared Rules

- Preconditions:
- Test data:
- Response or observable-result rules:
- Cleanup:
- Constraints:

Cleanup must contain only confirmed initiation or completion behavior. Do not
invent polling, retries, timeouts, or terminal states.

## Cases

### TC-001: <case name>

- Priority:
- Request actor:
- Target variants:
- Given:

#### Steps

1. <action performed in this step>
   - Request: `<METHOD> <path>` (omit for a non-request step, e.g. a UI action
     or a pure precondition)
   - Example payload: `<minimal illustrative payload>` or `not applicable`
   - Pass criteria:
     - Status: `<code>` (mandatory whenever the step issues a request)
     - Message: `<verified response message or key body field>` or
       `not applicable` because ...
     - Value checks: `<field> = <value>`; repeat per field, or
       `not applicable`
     - Schema: `not applicable` because ... (name it when a contract applies)
     - Headers: `not applicable` because ...
     - Error contract: `not applicable` because ... (negative steps only)
     - Side effects: `<observable state change>` or `not applicable`
2. <next step, if the case needs more than one action to prove the behavior>
   - ...
- Cleanup:
- Evidence:

Repeat for each distinct behavior. Keep stable case IDs after approval. A
single-action case is still a one-step list; add steps only when more than one
request or observable action is needed to prove the behavior (e.g. create,
then fetch, to verify persisted state).

For every request step, `Status` is mandatory. Every other pass-criteria field
must have a verified expectation or `not applicable` with a reason. Schema
validation does not replace assertions for business-significant values.
Example payloads illustrate shape, not proof of behavior: build them from a
confirmed schema, fixture, or evidence already cited for the case, and mark
illustrative placeholders (e.g. `<uuid>`, `"example"`) clearly instead of
presenting an invented value as confirmed.

## Handoff

- Reuse:
- Add or change:
- Verification:
- Risks:

## Approval

- Decision: `pending`
- Approved case IDs and variants:
- Conditions:
- Approved by:
- Date:
- Evidence:

Implementation is allowed only when the decision and artifact status are
`approved`. A material change to scope, case inventory, actor-target matrix,
expected results, assertions, or cleanup returns the artifact to
`awaiting-approval`.

Unless Conditions restrict execution, approval of the exact variants also
authorizes implementation, execution in the project-configured non-production
QA environment, and the cleanup defined by this contract. Production,
additional variants, broader suites, and destructive actions outside approved
cleanup require separate approval.

List every approved case and exact parameter set. Do not use shorthand such as
`all variants above`.

## Implementation

- Implemented case IDs and variants:
- Traceability:
- Changed files:
- Static verification:
- Collection or discovery:
- Live execution: `pending`; governed by project context
- Deferred cases:
- Remaining risks:

Set status to `implemented` only after approved cases are implemented and
verified, or explicitly deferred by a recorded user decision.
