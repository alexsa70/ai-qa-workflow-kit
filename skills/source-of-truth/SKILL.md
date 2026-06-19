---
name: source-of-truth
description: Resolve an uncertain or conflicting project claim by identifying the exact question, consulting available sources in the project-defined authority order, checking freshness and directness of evidence, and returning a cited verdict with confidence and next action. Use before test design, implementation, review, or bug filing when expected behavior, API contracts, requirements, permissions, thresholds, configuration, or other project facts are unknown, ambiguous, stale, or contradictory.
---

# Source Of Truth

Resolve one factual project question without inventing missing behavior.

## Required Input

Obtain:

- one specific claim or question to resolve;
- the target project;
- the project context;
- the available source registry and authority order;
- any known freshness metadata or access limitations.

If the question contains multiple independently verifiable claims, split them
and resolve one at a time.

## Workflow

### 1. Scope The Claim

Record:

```text
Question:
Claim type:
Target area:
Decision blocked by this claim:
Required confidence:
```

Use a claim type such as:

- expected behavior;
- contract or schema;
- authorization or permissions;
- configuration or threshold;
- requirement or acceptance criterion;
- runtime behavior;
- test-management expectation.

Do not research a broad topic when the workflow needs one precise fact.

### 2. Load The Source Policy

Read the connected project's source registry and authority order.

For each source, identify:

- source name and type;
- location or access method;
- authority rank for this claim type;
- freshness signal when available;
- freshness check and update policy;
- whether it is direct evidence or an interpretation.

Do not use a universal authority order. Runtime evidence, product
requirements, implementation code, API contracts, and test cases may have
different authority depending on the question and project policy.

If no source policy exists, list the available sources and mark the result
`provisional`. Do not silently invent an authority hierarchy.

### 3. Verify Source Freshness

Before relying on a controlling source, apply its configured freshness policy.

For a Git source:

1. Inspect the working tree and current branch.
2. Run the configured fetch or remote-check command.
3. Compare the local revision with the configured remote branch.
4. Run the configured update command only when project policy allows it.
5. Record the revision and timestamp used for the verdict.

Do not update a dirty, divergent, or unexpected branch unless project policy
explicitly defines that case. Do not replace a configured safe update command
with a destructive operation.

Classify freshness as:

- `current`: the source matches its configured upstream or freshness signal;
- `stale`: a newer authoritative version is known;
- `unchecked`: the check was not configured, skipped, or unavailable;
- `blocked`: freshness cannot be established safely.

A controlling source with `stale`, `unchecked`, or `blocked` freshness cannot
produce `confirmed` with `high` confidence. Use `provisional` or `unresolved`
and explain the limitation.

### 4. Gather Evidence

Start with the highest-authority accessible source that can answer the claim.
Continue only when:

- the source does not answer the question;
- the source is stale or indirect;
- another relevant source may contradict it;
- the required confidence has not been reached.

For every consulted source, capture:

```text
Source:
Authority rank:
Freshness:
Revision or version:
Evidence:
Citation:
Supports:
```

Prefer exact file paths, sections, line references, URLs, versions, commit
identifiers, timestamps, or command results.

Treat existing tests as evidence of prior expectations, not automatically as
the product contract.

### 5. Compare Claims

Classify source relationships:

- `agreement`: sources state compatible facts;
- `higher-authority override`: a higher-ranked source resolves the conflict;
- `same-rank conflict`: sources at the same authority level disagree;
- `stale evidence`: an older source conflicts with a fresher source;
- `scope mismatch`: sources describe different versions, environments, roles,
  or conditions;
- `insufficient evidence`: no source directly resolves the claim.

Do not erase contradictions from the verdict even when an authority rule
resolves them.

### 6. Assign Status And Confidence

Use one status:

- `confirmed`: direct evidence from the controlling source resolves the claim;
- `provisional`: the best available evidence supports an answer, but freshness,
  access, or authority is incomplete;
- `unresolved`: evidence is missing or conflicting without a valid tie-breaker.

Use confidence:

- `high`: direct, current, controlling evidence with no unresolved conflict;
- `medium`: answer is supported but relies on indirect, older, or incomplete
  evidence;
- `low`: evidence conflicts, is inaccessible, or does not directly answer the
  claim.

An `unresolved` verdict must never be presented as authoritative.

### 7. Produce The Verdict

Use `assets/source-verdict.md` when the result must be persisted. Otherwise,
return the same fields in the conversation.

The verdict must contain:

- concise answer;
- status and confidence;
- controlling source and citation;
- freshness check, revision, and update result;
- evidence consulted;
- contradictions and how they were handled;
- access or freshness limitations;
- recommended next action;
- next permitted workflow transition.

## Actual Versus Intended Behavior

A failing test asks "what *should* happen", not "what *does* happen". Keep the
two separate.

- **Actual behavior** (runtime observation: a status code, a rendered screen, a
  stored value) tells you what the deployed system does now.
- **Intended behavior** (the contract: implementation code, authorization
  guard, spec, acceptance criterion) tells you what is correct.

When a project's authority order ranks the contract above runtime, a runtime
observation that conflicts with the contract is a **finding** (a bug or an
unannounced change), not a reason to conform the expectation to runtime. Resolve
the claim from the controlling contract source and report the divergence.

**Do not use the observation under question as its own corroboration.** If the
claim being resolved is "is this `200` correct?", that same `200` is not
independent evidence. It is the thing in dispute.

**Negative / permission asymmetry.** A successful result (`2xx`, no error,
action completed) is weak evidence for "permitted by design": a missing guard
and a deliberately open operation are indistinguishable at runtime. A *blocked*
result (`401/403`, rejection) is strong evidence that a guard exists. So:

- "Is this forbidden?" must be resolved from the access-control contract or the
  guard in code — never from a successful runtime response.
- Runtime can *refute* a "forbidden" expectation only when it returns the block;
  a success neither confirms nor refutes the design intent on its own.

## Transition Rules

- `confirmed`: allow the blocked workflow to continue within the resolved
  scope.
- `provisional`: continue only when the project's gate policy permits that
  confidence level; otherwise request stronger evidence.
- `unresolved`: stop the dependent workflow and request the missing source,
  owner decision, runtime observation, or project-specific clarification.

Do not automatically update documentation, tests, issue trackers, or external
systems. Return the verdict to the Orchestrator, which decides the next action.

## Guardrails

- Never invent an authority order, expected behavior, or missing evidence.
- Never equate implementation behavior with intended behavior unless project
  policy makes implementation authoritative for the claim.
- Never treat a runtime observation as corroboration of itself, and never treat
  a successful response as proof that an action is permitted by design (see
  `Actual Versus Intended Behavior`).
- Never treat a test case as the highest authority by default.
- Never hide source conflicts.
- Never use freshness alone to override a higher-authority source unless the
  project policy permits it.
- Never claim `confirmed/high` when controlling-source freshness is not
  `current`.
- Never run a source update command that is absent from project context.
- Never broaden the conclusion beyond the investigated environment, version,
  role, endpoint, or condition.
- Name inaccessible sources and explain how their absence affects confidence.
