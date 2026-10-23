---
name: coverage-backlog
description: Compute a prioritised coverage backlog that is never stored, from the project's coverage tool and its open pull requests, as a kanban board with blocking relationships and an AFK or HITL label per unit. Use when choosing what to cover next, planning a day of scenario work, checking which uncovered requirement units are free to claim, or turning outside-inventory findings into backlog units. Read-only - it never writes repository files, opens pull requests or claims units.
---

# Coverage Backlog

Turn "what is not covered yet" into "what to do next, in which order, and who
must be present". The board is recomputed on every run from live sources, so
it never drifts from the repository and never rots.

## Scope

Use this skill when:

- the user asks what to cover next, or plans a day shift of scenario work;
- uncovered requirement units must be checked against open claims;
- black-box `outside-inventory` findings must join the backlog.

Do not use it to design a case (`requirement-grill`, then the project's
authoring skill), to build an endpoint coverage workbook (`coverage-matrix`),
or to claim a unit (the authoring skill's claim step).

## Required Input

From the project context, section "Coverage Pipeline":

- `coverage.uncovered_command` - lists uncovered units, critical first;
- `coverage.detail_command` - coverage detail for named scenarios;
- `coverage.day_batch_size` - how many units to recommend (default 3);
- `requirements.inventory_paths` - where the requirement inventories live.

Also: the open pull requests of the target repository
(`gh pr list --state open --limit 200 --json number,title,body,headRefName,isDraft,labels,files`),
and any `outside-inventory` findings the user supplies or points to.

A missing key is a `missing context` blocker naming the key. Never substitute
a command of your own.

When the user names one or more domains, filter the board to them and say so
in the header.

## Procedure

1. **Collect.** Run `coverage.uncovered_command` from the target root. Record
   the exact command and `git rev-parse --short HEAD`. It is read-only. If it
   fails for any reason (network, credentials, missing dependency, non-zero
   exit), stop, report the exact command and error, and produce the blocked
   output. Never guess units. If it lists only critical units, write "P1 not
   computed by the configured command" in the header instead of reporting zero.
   If the open-PR listing fails, still compute the board, write "open pull
   requests not checked - claims may be missing" in the header, label every
   unit HITL and give no recommendation.
2. **Exclude what is taken.** A unit is taken when the coverage tool reports a
   claim, or an open pull request names the unit id in its title, body or
   changed scenario files. A unit the tool reports as a twin of another
   domain's unit is excluded with the note "automate in <domain>". Rely only on
   what the coverage tool prints or the PR list shows; if the tool output has
   no claim or twin information, write "claims/twins: not reported by the tool".
3. **Tier.** P0: units the inventory marks critical. P1: other inventory
   units. P2: `outside-inventory` findings. Inside a tier, group by domain.
4. **Find blockers.** Read each candidate's inventory entry only far enough to
   name what must exist first:
   - `infra:driver` - a product call the test layer does not offer yet;
   - `infra:profile` - an organisation profile, capability or actor role;
   - `infra:fixture` - shared data or setup used by several units;
   - `<unit id>` - another unit whose scenario must exist first.
   Mark a blocker only when the inventory or the test layer shows it; never guess.
5. **Label AFK or HITL.**

   | AFK candidate - all must hold | HITL - any one is enough |
   |---|---|
   | the test layer already offers every product call | needs new infrastructure (`infra:*`) |
   | no consent flow, external account or manual step | needs an external account, consent or manual step |
   | cleanup can be proven by the product | destructive action on shared or standing data |
   | the requirement, inventory and code agree | requirement, inventory and code disagree |
   | an existing scenario shows the pattern | a new pattern for this domain |

   When unsure, label HITL. AFK here means "may be implemented by the night
   shift once a human has confirmed the cases", never "may skip confirmation".
6. **Group.** Units that share actor, preconditions and observable outcome
   become one suggested scenario with several cases.
7. **Recommend.** Pick `coverage.day_batch_size` units: highest tier first,
   unblocked. Tie-break: unblocks most other units, then highest tier, then
   the order the tool printed.

## Output

```text
Backlog - <target> @ <short sha>, command: <exact command>
Counts: P0 <n> open / P1 <n> / P2 <n>; excluded: <n> claimed, <n> twins

| Unit | Tier | Domain | Blocked by | Label | Why | Suggested scenario |
|---|---|---|---|---|---|---|

Next <N> for the day shift:
1. <unit> - <one line why now>

Blockers to raise: <infra items with the units they hold back>
```

When the collect step fails, output only:

```text
Backlog blocked - <target> @ <sha>
Command: <exact command>
Error: <first relevant lines>
Next: <what the user must fix>
```

Write the board to chat. Write it to a file only when the user asks, and then
outside the repository (for example the session scratch directory).

## Rules

- Never write repository files, open or edit pull requests, add labels or
  claim units.
- The board is not a record. Re-run the skill instead of editing an old board.
- Never mark a P0 unit as done or skippable; a P0 unit that cannot be covered
  stays on the board with its blocker.
- Report the exact commands run; do not report coverage numbers you did not
  read from the tool.

## Completion

Report the command and commit, tier counts, the board, the recommendation and
the blockers. Next permitted action: `requirement-grill` on a recommended
unit, or the authoring skill directly for a unit the user already understands.
