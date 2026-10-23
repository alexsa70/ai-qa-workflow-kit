---
name: night-shift
description: Implement one human-confirmed scenario pull request without a human present - run the project's authoring skill for the phases after its confirmation checkpoint, the safe checks, a destructive-safety gate, a live run in the sandbox environment and a self-review, then push to the pull request's branch, comment a report and swap the ready label for done or blocked. Use only inside a headless session started by bin/qa-night in a worktree of a draft pull request that carries the ready label. Never asks questions, approves, merges or widens scope.
---

# Night Shift

The day shift (a human with `coverage-backlog`, `requirement-grill`,
`blackbox-review` and the authoring skill) claimed the scenario and confirmed
its cases. The night shift implements exactly that, proves it, and leaves a
report for the morning. Nobody is watching: when in doubt, stop.

## Preconditions

Check all before any edit. Any failure: stop, mark blocked (see Stop).

1. The session runs in a git worktree of the target on the pull request's
   branch (`git branch --show-current` equals the branch in the prompt).
2. The pull request is an open draft and carries `labels.ready`, and carries
   neither `labels.done` nor `labels.blocked`
   (`gh pr view <n> --json isDraft,state,labels`).
3. The confirmed cases are recorded: the scenario file on the branch and the
   confirmation the authoring skill's checkpoint left in the pull request
   (description or comments). No confirmation found: stop.
4. Every key used below exists in the project context's "Coverage Pipeline"
   section (read the file named in the prompt, not the worktree).
5. The `destructive-safety` denylist exists. Missing: safe checks only, no
   live run, then stop as blocked.

## Procedure

1. **Read.** The pull request (`gh pr view <n> --comments`), its diff against
   the default branch, the scenario and the confirmation. List the confirmed
   cases and the files the pull request may touch.
2. **Implement.** Invoke the skill named by `authoring.skill` and run only the
   phases listed in `authoring.after_checkpoint_phases`. Follow that skill's
   rules; this skill never overrides them.
3. **Safe checks.** Run every command in `checks.safe`. Fix only what your own
   change broke. Repeat until clean or until the change would leave the
   confirmed scope.
4. **Destructive gate.** Run `destructive-safety` over every destructive call
   the new tests make. A call it does not clear: stop.
5. **Preflight.** Run `checks.preflight`. A failure is `blocked: environment`,
   never "not verified" reported as success.
6. **Live run.** Run `run.live_sandbox`, sandbox target only. Publish what the
   command publishes; never another target.
7. **Self-review.** Run `review.command`. Fix findings that change a verdict;
   record why for the rest. Repeat until it reports nothing you act on.
8. **Commit and push.** Commit with explicit paths. Every commit message ends
   with `night-shift run <run id>`. Push with `git push origin HEAD:<branch>`.
9. **Report.** Comment on the pull request with the template below, then
   `gh pr edit <n> --remove-label <labels.ready> --add-label <labels.done>`.

## Stop

Stop at once - no workaround - when:

- the work would depart from the confirmed cases (a new case, a changed
  expectation, a dropped variant) - the authoring skill's "ask again" point;
- it needs a new fixture, probe, runner flag or anything that skill reserves
  for a human;
- a file outside the listed scope must change, or another open pull request
  also changes it;
- a destructive call is not cleared, the preflight fails, or the budget runs
  out.

To stop: commit and push whatever is finished and consistent, comment the
report with status `blocked` and the exact question a human must answer, then
`gh pr edit <n> --remove-label <labels.ready> --add-label <labels.blocked>`.

## Never

- ask a question inside the session; the question goes into the report;
- add the ready label, mark the pull request ready (`gh pr ready`), merge,
  record approval, or edit approval fields;
- force-push, push to the default branch, or rewrite earlier commits;
- run with `bypassPermissions`, or publish to a non-sandbox target;
- change an expectation to match what the product does.

## Report template

```markdown
### Night shift - night-shift run <run id>

**Status:** done | blocked
**Cases:** <case id - passed | failed | not verified> (one per line)
**Live run:** <command>, <environment>, <sandbox link or run id>
**Evidence:** <failing step, expected vs actual, resource ids - for every non-pass>
**Self-review:** <level, findings fixed, findings left with reason>
**Commits:** <short sha - subject>
**Blocked on:** <the exact question for a human, or "-">
```
