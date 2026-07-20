---
name: destructive-safety
description: Guard destructive test actions during automated or autonomous QA runs by checking every delete/purge/reset-style call against a project denylist of protected, seeded, and shared identifiers before it executes, and by enforcing blast-radius invariants (create-capture-operate-cleanup, file-scoped invocation, protected-branch lockdown, post-run reconcile). Use before running tests that call destructive endpoints or fixtures, before authorizing an autonomous/headless run, or when defining which resources a run may create and remove. The denylist lives in the connected project and is read-only to the agent; extending it requires a human change.
---

# Destructive Safety

Prevent an automated QA run from deleting, resetting, or corrupting a protected
or shared resource. The signal a test suite exists to produce is worthless if a
run can also destroy seeded data, another actor's fixtures, or production-shaped
state. This skill gates destructive actions; it does not design or implement
tests.

## Scope

Use this skill when:

- a test or fixture calls a destructive operation (delete, drop, purge, wipe,
  reset, remove) against a live system;
- an autonomous or headless run must be authorized to create and clean up
  resources without a human watching each step;
- the set of resources a run may touch, and the cleanup it must perform, must
  be made explicit before execution.

Do not use this skill to design coverage (`test-design`), implement tests
(`test-implementation`), or decide whether an action is *permitted by contract*
(`source-of-truth`). This skill decides whether an action is *safe to execute in
this environment right now*.

## Required Input

- the target project and its non-production QA environment;
- the project denylist file (see Denylist Contract) and its location from
  project context;
- the exact destructive calls the run will make and the identifiers they target;
- the approved set of cases and their cleanup, when a contract exists.

If the denylist file is missing, stop with a `missing capability` blocker.
Do not proceed against a live system without one, and do not invent its
contents.

## Denylist Contract

The denylist is a machine-readable file in the connected project (a template
ships at `assets/seeded-ids.template.json`). It records:

- `protected_ids` — identifiers a run must never target with a destructive
  call: seeded accounts, shared orgs, reference fixtures, baseline data;
- `protected_logins` — literal credentials/usernames that must never be deleted,
  reset, or have passwords changed;
- `destructive_call_pattern` — a regex of operation names treated as destructive
  (default `^(delete_|drop_|purge_|wipe_|reset_|remove_)`);
- `fixture_allowlist_pattern` — a regex marking resources a run is allowed to
  create and then remove (default `^temporary_` / `^qa_ephemeral_`).

The agent reads this file. The agent never edits it. Extending the denylist is a
human change (a reviewed commit or PR) that also updates whatever tests or
scanner assertions depend on it — so the denylist can only ever get stricter
through a deliberate act, never looser through automation.

## Blast-Radius Invariants

Enforce all five before and during any run that touches a live system:

1. **Preflight scan.** Before execution, scan the run's destructive calls. Block
   the run if any destructive call (matching `destructive_call_pattern`) targets
   an identifier in `protected_ids`/`protected_logins`, or targets an identifier
   that is not traceable to a resource this run created under
   `fixture_allowlist_pattern`. A hardcoded ID in a destructive call is a block,
   not a warning.
2. **Create → capture → operate → cleanup-from-created-list.** A run deletes
   only what it created. Capture each created resource's ID at creation time and
   drive cleanup from that captured list — never from a query that could match
   pre-existing or another actor's resources.
3. **File-scoped invocation.** Run destructive tests by explicit file/case path,
   never by a marker-wide or wildcard selector that could sweep unrelated
   destructive cases into the same run.
4. **Protected-branch / environment lockdown.** Refuse to run against anything
   but the project-configured non-production QA environment. Never production.
5. **Post-run reconcile.** After the run, compare the resource count/state
   against the pre-run baseline. Halt and escalate on an unexplained delta
   (orphaned resource, unexpected deletion) instead of reporting success.

## Escalation

- A blocked destructive call → stop, name the offending call and identifier,
  and report it as a `failed verification` blocker. Do not soften the call to
  make it pass.
- An orphaned or unexpectedly deleted resource in reconcile → stop and escalate;
  do not clean up further blindly.
- A missing or unreadable denylist → `missing capability` blocker.

## Output

Report:

```text
Environment checked:
Denylist source:
Destructive calls scanned:
Preflight result (pass / blocked + reason):
Resources created / cleaned up:
Post-run reconcile (baseline vs after):
Blockers:
Next permitted action:
```

## Boundaries

- Read-only over the denylist; never edits it and never relaxes a pattern.
- Does not authorize production execution under any condition.
- Does not decide contract permission (route to `source-of-truth`) or design
  cleanup coverage (route to `test-design`).
- Approval of a contract's exact variants authorizes their cleanup as defined;
  it does not authorize destructive actions outside that cleanup.
