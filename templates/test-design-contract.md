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
- When:
- Then:
  - 
- API response:
  - Status:
  - Body/schema:
  - Business assertions:
  - Headers: `not applicable` because ...
  - Error contract: `not applicable` because ...
  - Side effects:
- Cleanup:
- Evidence:

Repeat for each distinct behavior. Keep stable case IDs after approval.

For API cases, `Status` is mandatory. Every other API response field must have
a verified expectation or `not applicable` with a reason. Schema validation
does not replace assertions for business-significant values.

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
