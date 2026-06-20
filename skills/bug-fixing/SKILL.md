---
name: bug-fixing
description: Reproduce, classify, and fix failures in QA automation workflows. Use when implemented tests, live QA execution, cleanup, clients, schemas, fixtures, factories, assertions, or framework commands fail and the result must be classified as framework bug, product bug, environment issue, or contract mismatch before repair. Preserve approved test intent, source-of-truth authority, cleanup safety, and verification evidence. Do not use to design new tests, broaden approved scope, or change expected behavior without source-of-truth and renewed approval.
---

# Bug Fixing

Repair failures without erasing the signal the failure exposed. Preserve the
approved contract, intended behavior, and cleanup guarantees unless
source-of-truth proves the contract must change.

## Required Input

Obtain:

- the target project and project context;
- failing command, log, stack trace, CI output, live-run result, or clear
  reproducible symptom;
- relevant Test Design Contract, approval record, and implementation section
  when the failure belongs to approved cases;
- source-of-truth verdicts or controlling sources for disputed expected
  behavior;
- changed files or recent implementation context;
- project-native verification and cleanup commands.

If the failure cannot be identified or reproduced from available evidence,
return a `missing failure evidence` blocker with the smallest command or log
needed next.

## Workflow

### 1. Scope The Failure

Record:

```text
Failure target:
Failing command or symptom:
Relevant artifact:
Approved case IDs and variants:
Environment class:
Last known passing evidence:
Cleanup exposure:
Allowed fix scope:
```

Do not broaden the task to unrelated failures. If multiple failures are
present, fix the first root cause that blocks the approved workflow unless the
user asks for a broader pass.

### 2. Reproduce Or Validate The Evidence

Prefer the smallest command capable of reproducing the failure:

1. static or syntax check for import/type/style failures;
2. collection or discovery for test definition failures;
3. one exact failing test variant for runtime failures;
4. broader run only when project context authorizes that scope.

Do not run production, destructive, or broader-suite checks unless explicitly
authorized by project context and the current request.

If the original evidence is already sufficient and rerun would be expensive or
unsafe, do not rerun. State that classification is based on supplied evidence.

### 3. Classify The Failure

Use exactly one primary classification:

- `framework bug`: test code, helper, client, schema, fixture, factory,
  assertion, marker, config, or cleanup implementation is wrong.
- `product bug`: deployed behavior conflicts with the controlling contract or
  source-of-truth.
- `environment issue`: credentials, service availability, test data, external
  dependency, object storage, network, clock, or sandbox prevents valid
  verification.
- `contract mismatch`: approved Test Design Contract conflicts with newer or
  higher-authority source evidence.
- `insufficient evidence`: the available data cannot distinguish the above.

Keep actual behavior separate from intended behavior. A runtime response can
show what happened, but it does not rewrite the approved expectation by itself.

If classification depends on intended behavior and the controlling source is
missing or conflicting, route the claim through `source-of-truth` before
changing expectations.

### 4. Fix Only When Allowed

Allowed direct fixes:

- framework bugs within project-configured support-code and test paths;
- cleanup ordering and safety defects that preserve approved cleanup intent;
- assertion implementation mistakes that restore the approved expectation;
- schema/client/factory/fixture bugs required by approved cases;
- environment guardrails that make the failure explicit without hiding it.

Stop instead of fixing when:

- the product appears wrong against the controlling contract;
- the approved contract must materially change;
- the fix would broaden approved scope, weaken assertions, or change expected
  behavior;
- cleanup cannot be performed safely;
- required secrets, credentials, or external systems are unavailable.

For product bugs, produce a concise bug handoff with observed behavior,
expected behavior, evidence, affected variants, and reproduction command.

For contract mismatch, return the artifact to the design workflow; do not
patch tests to match the new behavior without renewed approval.

### 5. Verify The Repair

Run the smallest sufficient verification sequence:

1. targeted static check for changed files;
2. target collection or discovery;
3. exact previously failing variant;
4. approved affected variants when project context authorizes autonomous QA
   execution;
5. cleanup verification or cleanup-result inspection when persistent data was
   created.

If verification fails again, repeat diagnosis only when new evidence suggests
a different root cause. Do not loop indefinitely on the same failure mode.

### 6. Update Evidence

Update only the relevant artifact sections when project policy expects durable
repair evidence:

- failure summary and classification;
- changed files;
- commands run and outcomes;
- affected case IDs and variants;
- cleanup result or remaining cleanup risk;
- product bug, environment blocker, or contract mismatch handoff.

Do not change Approval records. Do not mark an unverified fix as complete.

### 7. Return To The Orchestrator

Report:

```text
Classification:
Root cause:
Fix applied:
Changed files:
Verification:
Cleanup:
Artifact updates:
Remaining blocker or risk:
Next permitted transition:
```

## Guardrails

- Never weaken assertions to make a failing test pass.
- Never change expected behavior from runtime alone.
- Never hide a product bug as a framework fix.
- Never invent source evidence, credentials, services, or cleanup completion.
- Never leave persistent test data unmanaged when a created ID is available.
- Never perform unrelated refactors while fixing a failure.
- Never update approval records or expand approved variants during repair.
- Never claim a fix is complete when only collection passed for a runtime
  failure.
