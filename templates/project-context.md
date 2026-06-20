# Project Context

## Identity

- Project name:
- Repository root:
- Project purpose:
- Current phase:

## Technology

- Language:
- Test framework:
- API or UI libraries:
- Schema or validation library:
- Reporting:

## Paths

- Application source:
- Tests:
- Test design:
- API clients:
- Schemas:
- Fixtures:
- Generated artifacts:

## Commands

- Install:
- Static checks:
- Test collection:
- Smallest test verification:
- Full test suite:

## External Sources

- Backend repository:
- API documentation:
- Test management system:
- Requirements documentation:

## Source Registry

List only sources available to this project.

| Source name | Type | Location or access | Freshness signal |
|---|---|---|---|
| | | | |

## Source Freshness And Update Policy

Define how freshness is checked separately from how a source may be updated.
Commands are project configuration consumed by workflow skills.

| Source | Freshness check | Current when | Update command | Automatic update allowed | Block conditions |
|---|---|---|---|---|---|
| | | | | | |

For Git sources, prefer a non-destructive sequence:

1. inspect status and branch;
2. fetch the configured remote;
3. compare local and remote revisions;
4. update only with the configured fast-forward command;
5. stop on dirty state or divergence unless explicitly configured otherwise.

## Authority Policy

Define authority by claim type. Do not assume one global order fits every
question.

| Claim type | Authority order, highest first | Tie-break rule |
|---|---|---|
| Expected behavior | | |
| API contract or schema | | |
| Authorization or permissions | | |
| Configuration or threshold | | |
| Runtime behavior | | |
| Test-management expectation | | |

## Workflow Rules

- Allowed test markers:
- Environment policy:
- Secret handling:
- Data cleanup policy:
- Public or internal API policy:
- Required approval gates:

## API Automation Architecture

- Architecture type:
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

## Available Roles And Skills

- Available specialist agents:
- Available skills:
- Required artifacts:

## Test Implementation Policy

- Approved design status required:
- Approval evidence format:
- Allowed test and support-code paths:
- Required static checks:
- Required collection or discovery:
- Autonomous non-production execution:
- Separate execution approval required for:
- Traceability format:
- Artifact update rule:

## Code Review Policy

- Required review targets:
- Review evidence:
- Allowed review commands:
- Stack-specific review adapters:
- Findings format:
- Review completion rule:

## Bug Fixing Policy

- Allowed fix paths:
- Reproduction commands:
- Autonomous rerun scope:
- Product bug handoff:
- Environment blocker handling:
- Contract mismatch handling:
- Cleanup repair policy:
- Artifact update rule:

## Known Constraints

- None recorded.
