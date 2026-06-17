# Test Implementation

## Purpose

`test-implementation` translates an approved Test Design Contract into
project-native automated tests and narrowly required support code.

The approved design remains the controlling workflow artifact. Implementation
updates that artifact instead of creating a separate report by default.

## Entry Gate

Implementation may begin only when:

- the artifact status is `approved`;
- the approval record names exact case IDs and parameter variants;
- expected behavior, assertions, cleanup, and constraints are explicit;
- project context provides implementation and verification rules.

Conversational approval is insufficient when the durable artifact still says
`pending`.

An `implemented` artifact may re-enter only to complete pending live
verification for the exact recorded variants under an autonomous project
execution policy.

## Scope Lock

Implementation may adapt code structure to current project conventions, but it
must not change:

- approved case inventory or parameter matrix;
- expected results;
- request actors or target roles/states;
- response assertions;
- persistent side effects or cleanup.

A material change returns the design to `awaiting-approval`.

## Traceability

Every approved case and variant must map to:

- a test or parameterized test variant;
- changed support code when applicable;
- a verification result.

Traceability belongs in the Test Design Contract implementation record. Test
names do not need artificial IDs when local conventions provide a better name.

## Verification Layers

Report separately:

```text
static or syntax checks
collection or discovery
isolated execution
full or live execution
```

Static success and collection are sufficient to complete a non-live
implementation phase when project policy allows it. They do not prove runtime
behavior.

Approval of the exact contract variants also authorizes their execution and
approved cleanup in a project-configured non-production QA environment when
project context enables autonomous execution. Production, broader scope, and
destructive actions outside approved cleanup require separate approval.

## Completion Gate

Artifact status may become `implemented` when:

- every approved case and variant exists in code;
- traceability is complete;
- required static checks pass;
- target collection or discovery passes;
- deferred work and skipped live checks are explicit.

When project context enables autonomous QA execution, runtime verification is
part of the same transition and must be attempted before the implementation
workflow returns. An unavailable environment is reported as a blocker, not as
a request for duplicate approval.
