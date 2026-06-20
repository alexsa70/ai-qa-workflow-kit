---
name: api-layered-architecture
description: Define, apply, and review a layered API test automation architecture. Use for API projects that should separate transport clients, service/resource clients, schemas, factories, assertion helpers, and scenario tests; for evaluating whether an API framework follows the layered pattern; and for guiding test-design, test-implementation, code-review, or bug-fixing work so new tests are built through the project-native layers instead of raw HTTP and inline payloads.
---

# API Layered Architecture

Use layered API architecture to keep tests scenario-focused and keep transport,
endpoint paths, schemas, payload construction, and reusable assertions in their
own layers.

## Core Pattern

The generic shape is:

```text
transport client
-> service/resource client
-> schemas
-> factories
-> assertion helpers
-> tests
```

Projects may name or group layers differently. Follow the names and paths in
project context, but preserve the separation of responsibilities.

## Layer Responsibilities

| Layer | Responsibility | Should not own |
|---|---|---|
| Transport client | Base URL, auth headers, sessions, retries/rate limits, common HTTP behavior | Endpoint-specific business methods |
| Service/resource client | One method per endpoint or resource action; endpoint paths and HTTP verbs | Test scenario decisions or generated payload content |
| Schemas | Request/response models and structured validation | HTTP calls or scenario control flow |
| Factories | Valid and invalid payload/test-data builders | Endpoint paths, assertions, or environment secrets |
| Assertion helpers | Reusable status/header/schema/business assertion helpers | Product expectations not provided by the contract |
| Tests | Scenario flow, actor/variant selection, business assertions, side-effect checks, cleanup orchestration | Raw transport details, duplicated endpoint paths, broad payload construction |

For small projects, a layer may be thin. Do not collapse responsibilities into
tests just because a helper is short.

## Required Project Context

For an API project, record:

```text
API automation architecture:
- Transport client:
- Service/resource clients:
- Schemas:
- Factories:
- Assertion helpers:
- Tests:
- Raw HTTP in tests:
- Inline payloads in tests:
- Endpoint path ownership:
- Cleanup ownership:
```

If the project intentionally uses a different architecture, record that
explicitly. Do not force this pattern onto non-API projects or API projects with
a documented alternative.

## Test Design Handoff

When creating a Test Design Contract for an API test, include a short layered
handoff:

```text
Reuse:
- transport:
- client:
- schema:
- factory:
- assertions:

Add or change:
- client methods:
- schemas:
- factories:
- assertion helpers:
- tests:
```

Expected behavior still comes from `source-of-truth`, not from the current
shape of the layers.

## Implementation Rules

- Reuse existing layers before adding new ones.
- Add endpoint-specific calls to the service/resource client, not directly to
  the test.
- Keep endpoint paths and HTTP verbs out of tests unless project context
  explicitly permits raw HTTP.
- Validate structured responses through schemas when a schema contract exists.
- Build request data through factories when the project has a factory layer.
- Keep business-significant assertions in tests or assertion helpers, not only
  in schemas.
- Register cleanup as soon as the created resource ID is available.
- Keep support changes in the smallest layer that owns the defect or missing
  capability.

## Review Checklist

Flag issues when:

- tests call the transport client directly despite an existing resource client;
- endpoint paths or HTTP verbs are duplicated in tests;
- payloads are built inline when a factory layer exists;
- schema validation is skipped for structured responses with known contracts;
- schema validation replaces business assertions;
- cleanup is registered after assertions that can fail;
- support code is added to the wrong layer;
- a layer invents product expectations that belong in the Test Design Contract
  or `source-of-truth`.

## Failure Routing

Route fixes to the owning layer:

| Symptom | Likely layer |
|---|---|
| Base URL, auth, session, retry, timeout, rate limit problem | Transport client |
| Wrong path, method, query, or endpoint-specific request wiring | Service/resource client |
| Response parse/validation mismatch | Schemas, after source-of-truth confirms contract |
| Invalid generated data or missing data variant | Factories |
| Repeated or weak checks | Assertion helpers or tests |
| Scenario order, actor, side effect, or cleanup timing | Tests |
| Runtime contradicts confirmed product contract | Product bug handoff, not layer rewrite |

Do not move expectations to match a failing runtime response without
`source-of-truth`.

## Output Format

For architecture evaluation, report:

```text
Pattern status:
Project layer map:
Conforming examples:
Layer violations:
Missing layers or gaps:
Recommended next action:
```

For handoff to another skill, report:

```text
Layered handoff:
Reuse:
Add or change:
Constraints:
Review focus:
```

## Guardrails

- Never treat this architecture pattern as product behavior evidence.
- Never force the API layered pattern onto UI, data, or non-API workflows.
- Never add abstraction only to satisfy the pattern when direct reuse is
  already project-native and clear.
- Never let tests pass only because schema validation is broad or business
  assertions are missing.
- Never hide transport, endpoint, schema, or factory defects inside test
  workarounds.
