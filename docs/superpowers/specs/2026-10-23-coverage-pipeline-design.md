# Coverage Pipeline — Design

- **Status:** awaiting-review
- **Date:** 2026-10-23
- **Scope:** `ai-qa-workflow-kit` only. Nothing is committed to any target repository.
- **Motivation:** Matt Pocock, "Full Walkthrough: Workflow for AI Coding" (AI Engineer):
  align before planning (grill), turn the destination into an independently grabbable
  backlog, keep the human in the loop for planning and QA, run implementation AFK in a
  fresh context per task, review in a fresh context.

## 1. Problem

The first consumer is a test repository whose active system is a *scenario catalog*:
reviewed YAML scenarios bound one-to-one to test classes, each case declaring which
units of a backend-generated *flow inventory* it covers. A central organisation skill
(the *authoring skill*) already owns the full procedure for writing one scenario: claim
via a draft PR, a confirmation checkpoint with the developer, the YAML, the test class,
driver methods, a live sandbox run, publication and self-review.

What is missing:

1. **No backlog view.** Coverage tools list uncovered inventory units, but nothing turns
   them into a prioritised board with blocking relationships and an AFK/HITL split.
2. **Shallow alignment before the claim.** The authoring skill's checkpoint confirms
   cases after the claim; there is no deep, one-question-at-a-time interview over a unit's
   requirement, inventory and code before a scenario is admitted.
3. **A white-box blind spot.** The inventory is derived from backend code, so the catalog
   verifies what the code does. Missing behaviour, user expectations (messages, retries,
   interruptions, cross-domain journeys, language and data variety) are not systematically
   proposed. The catalog already accepts such cases (`covers: []` plus an
   `outside_inventory:` explanation), but nothing generates them.
4. **No night shift.** Every confirmed scenario is implemented in an interactive session.

## 2. Decisions

| # | Decision | Rejected alternatives |
|---|---|---|
| D1 | The kit sits **above** the authoring skill. The kit never duplicates its rules; it prepares input for it and invokes it. | Kit replaces the authoring skill; kit edits the authoring skill. |
| D2 | Four separate skills plus one launcher script (approach A). | One umbrella skill (loads HITL procedure into the AFK prompt); extending `test-design` / `coverage-matrix` (second source of truth, different purpose). |
| D3 | The board is **computed, never stored**: recomputed from the coverage tool and open PRs on every run. Claims live in draft PRs, decisions in the YAML and PR. | Local markdown board (sync drift, doc rot); Jira issues (external write per unit). |
| D4 | A **label on the draft PR, applied by a human**, marks a scenario ready for the night shift. | Section in PR body (fragile parsing); explicit list at launch (fully manual). |
| D5 | Night shift runs **sequentially, fresh context per PR**: one git worktree and one headless session per PR. | Parallel worktrees (shared cluster and sandbox, driver conflicts); one session with subagents (context drift into the dumb zone). |
| D6 | A **black-box review** skill that deliberately does not read product code, fed by kit-level and project-level heuristics. | Adding a lens to `qa-review-gate` (gate returns a verdict, not proposals). |
| D7 | Heuristics are seeded by **mining the user's legacy suites and test plans, then a grill interview**. Generic heuristics go into the kit; product-specific ones stay in an untracked project file. | Interview only; generic techniques only. |

## 3. Architecture

```
                 project-context.md  ("Coverage pipeline" section)
                          │ commands, labels, authoring skill, limits, heuristics path
 ┌────────────────────────┼──────────────────────────────────────────────────┐
 │ DAY (HITL)             ▼                                                   │
 │ coverage-backlog → requirement-grill → blackbox-review → authoring skill    │
 │  (read-only,          (one unit,          (proposed mode,   (claim draft PR │
 │   computed board)      grill brief)        no code)          + checkpoint)  │
 │                                                                │ human     │
 │                                                                ▼ labels PR │
 ├────────────────────────────────────────────────────────────────┼───────────┤
 │ NIGHT (AFK)     bin/qa-night → per labelled PR, one at a time:            │
 │                 worktree on its branch + headless session + night-shift    │
 │                 (authoring skill phases after the checkpoint → safe checks │
 │                  → destructive-safety → live sandbox run → self-review →   │
 │                  commit + push to the PR branch → report comment →         │
 │                  done/blocked label)                                       │
 ├───────────────────────────────────────────────────────────────────────────┤
 │ MORNING (HITL)  human reads reports, QAs, reviews, marks ready, merges.   │
 │                 blackbox-review (audit mode) on finished scenarios;        │
 │                 outside-inventory findings feed coverage-backlog.          │
 └───────────────────────────────────────────────────────────────────────────┘
```

Boundaries:

- **The kit stays project-agnostic.** Every path, command, label, environment and skill
  name comes from the project context. A missing key is a `missing context` blocker.
- **The authoring skill is the only writer of scenarios and tests.** `requirement-grill`
  and `blackbox-review` produce input for it; `night-shift` invokes it.
- **The night shift never touches approval.** It does not record approval, merge, mark a
  PR ready, publish to a CI (non-sandbox) project, or go beyond the confirmed scope. On
  any deviation it stops, labels the PR blocked and asks in a PR comment.

## 4. Components

All skills follow the kit layout: `skills/<name>/SKILL.md` with `name` and `description`
frontmatter, plus `skills/<name>/agents/claude.yaml` and `openai.yaml`.

### 4.1 `coverage-backlog` (read-only, HITL)

- **Input:** the project's coverage command(s), open PRs (`gh`), outside-inventory
  findings supplied by the user or quoted from PR comments.
- **Procedure:**
  1. Collect uncovered units; exclude units claimed by an open PR or covered by a twin
     in another domain (as reported by the project's tools).
  2. Prioritise: units the inventory marks critical → unmarked units → outside-inventory
     findings.
  3. Derive blocking relationships: a missing driver/client method, a missing org
     profile, capability or actor role, a shared fixture, a twin to automate elsewhere.
  4. Propose a label per unit: **AFK candidate** (known patterns, existing driver
     support, no consent flow or manual step, cleanup provable) or **HITL** (new
     infrastructure, destructive action outside the denylist's comfort zone, external
     account, disputed requirement).
  5. Recommend the next N units for a day shift (N from project context, default 3).
- **Output:** a board table in chat, optionally a scratch file outside the repository.
  Columns: unit, priority, blocked-by, AFK/HITL with reason, suggested scenario grouping.
- **Never:** writes files in the repository, opens PRs, claims units.

### 4.2 `requirement-grill` (HITL)

- **Input:** one unit or a small related group, the requirement source (e.g. an Outline
  page), the inventory entry, the backend code it cites.
- **Procedure:** one question at a time, each with a recommended answer, walking the
  decision tree until shared understanding. Branches that must be resolved:
  1. what exactly is asserted (observable outcome);
  2. requirement vs inventory vs code — any disagreement is routed through
     `source-of-truth`; an expectation is never changed to match code;
  3. actor, organisation profile, variants;
  4. preconditions and test data, collision avoidance;
  5. waiting and tolerances;
  6. cleanup and how deletion is proven;
  7. what a failing run records;
  8. explicitly **not** claimed (out of scope) and rejected alternatives with reasons.
- **Output:** a *grill brief* (markdown, chat or scratch file) shaped as input for the
  authoring skill's first phases: the scenario's three questions, provenance, cases with
  variants, out of scope, rejected options, open questions. It lives only until the claim;
  afterwards the YAML and the PR are the record (no doc rot).

### 4.3 `blackbox-review` (HITL generator, never reads product code)

- **Modes:** `proposed` (a grill brief or draft YAML before the claim) and `audit`
  (finished scenarios and test classes of a domain).
- **Input:** the requirement source and the cases. Product source code is out of bounds
  by design: independence from the implementation is the point.
- **Procedure:** apply test-design techniques (equivalence classes, boundaries, state
  transitions, decision tables, error guessing, cross-domain user journeys, interruption,
  retry and idempotency, concurrency, roles from the user's perspective, data variety
  including bidirectional text, recovery) and every heuristic from
  `skills/blackbox-review/references/heuristics.md` and from the project heuristics file
  named in the project context whose trigger matches.
- **Output:** findings, each with category, risk, and why a user would notice:
  1. `variant` — extend an existing case with a new variant;
  2. `new-case-in-inventory` — a new case that covers an existing unit from another angle;
  3. `outside-inventory` — a new case with `covers: []` and an `outside_inventory`
     reason; becomes a backlog unit;
  4. `question` — the requirement is silent; routed to the product owner via
     `source-of-truth`, never turned into an assumed expectation.
- **Never:** writes tests or scenarios, reads product code, approves anything.

### 4.4 `night-shift` (AFK) and `bin/qa-night`

`night-shift` skill, run inside one headless session per PR:

- **Preconditions** (any missing → blocked, no workaround): the PR carries the ready
  label applied by a human; the session runs in a worktree on the PR's branch; the
  project preflight passes; the `destructive-safety` denylist exists.
- **Steps:** read the PR, the scenario and the confirmed checkpoint record → run the
  authoring skill's phases that follow its confirmation checkpoint → safe checks → live
  run in the sandbox environment → the project's self-review command → commit and push
  to the PR branch → report comment (passed / failed / not verified, with evidence) →
  swap the ready label for done or blocked.
- **Hard stops:** any departure from the confirmed cases; a new fixture, probe or runner
  flag; a destructive action not cleared by `destructive-safety`; a file also touched by
  another open PR; budget exceeded.

`bin/qa-night`:

```text
qa-night <target-path>            # every PR with the ready label, one at a time
qa-night <target-path> --once <PR>  # one PR, for tuning the prompt
qa-night <target-path> --dry-run    # list what would run, start nothing
```

Per PR: verify the label event's actor is a human (`gh api .../issues/<n>/events`), skip
otherwise → `git worktree add` on the PR branch → `claude -p` with the night-shift prompt,
`--permission-mode` and `--allowedTools` from project context, `--max-turns` and a
timeout → log to a run directory → remove the worktree only after a successful push; on
failure keep it and name it in the log. A rerun resumes: the label is still present and
earlier commits are on the branch.

### 4.5 Project context: new "Coverage pipeline" section

Added to `templates/project-context.md`; all keys are required for the skill that reads
them.

| Key | Used by | Example meaning |
|---|---|---|
| `coverage.uncovered_command` | backlog | command listing uncovered units (critical first) |
| `coverage.detail_command` | backlog | per-scenario coverage detail |
| `coverage.day_batch_size` | backlog | N units recommended per day |
| `requirements.source` | grill, blackbox | where requirement pages live and how to fetch them |
| `requirements.inventory_paths` | backlog, grill | where the flow/guarantee inventories live |
| `backend.checkout` | grill | backend repository path (read-only) |
| `authoring.skill` | grill, night-shift | the authoring skill's name |
| `authoring.after_checkpoint_phases` | night-shift | which authoring phases the night shift runs |
| `checks.safe` | night-shift | commands with no product contact |
| `checks.preflight` | night-shift | environment/session preflight command |
| `run.live_sandbox` | night-shift | live run command, sandbox only |
| `review.command` | night-shift | self-review command and level |
| `labels.ready` / `labels.done` / `labels.blocked` | qa-night, night-shift | PR labels |
| `night.permission_mode` / `night.allowed_tools` | qa-night | headless session permissions |
| `night.max_turns` / `night.timeout_minutes` | qa-night | per-PR budget |
| `heuristics.project_file` | blackbox | path to the untracked project heuristics |

### 4.6 Orchestrator

`agents/qa-orchestrator.md` gains a task type `coverage-planning` and four routing rules
(when to use each skill and what each must not do), in the same style as existing rules.
`README.md`, `bin/qa-kit` and `docs/kit-only-mode.md` list the new skills (enforced by
existing kit tests). `docs/component-inventory.md` gains the four entries.

## 5. Heuristics files

Two files share one entry format.

- **Kit-level, tracked:** `skills/blackbox-review/references/heuristics.md` — generic,
  product-agnostic heuristics. No product, service, environment or company names.
- **Project-level, untracked:** e.g. `<target>/ai-workflow/heuristics.md`, path given by
  `heuristics.project_file`. Product-specific defect patterns and journeys.
- **Template:** `templates/project-heuristics.md` — the format plus clearly fictional
  examples, copied by the user next to the project context.

### 5.1 Entry format

```markdown
### H-<AREA>-<NN> — <short name>

- **Applies when:** <trigger: what in a requirement or case makes this heuristic relevant>
- **Try:** <the concrete probe or variation>
- **User expects:** <the black-box oracle, in user terms>
- **Typical failure:** <what usually goes wrong>
- **Technique:** <boundary | equivalence | state | decision-table | error-guessing |
  journey | concurrency | interruption | data | roles | recovery>
- **Source:** <mined: suite/file | interview: date | review finding: PR>
```

### 5.2 Seed examples for the kit-level file

```markdown
### H-RETRY-01 — Retry after a timeout must not duplicate

- **Applies when:** a create/submit action can time out or the client retries.
- **Try:** send the same create twice with the same payload; repeat after an
  artificial client timeout.
- **User expects:** one resource, or a clear "already exists"; never two silent copies.
- **Typical failure:** duplicate records, or the second call fails with a raw 500.
- **Technique:** error-guessing
- **Source:** seed

### H-DATA-01 — Bidirectional and non-Latin text survives the round trip

- **Applies when:** any user-supplied name, title, filename or free text is stored
  and shown again.
- **Try:** right-to-left text, mixed RTL/LTR with digits, combining characters,
  emoji, leading/trailing spaces, the maximum allowed length in multi-byte characters.
- **User expects:** the same text back, searchable, correctly ordered.
- **Typical failure:** reversed or truncated text, failed search, length limit
  counted in bytes instead of characters.
- **Technique:** data
- **Source:** seed

### H-STATE-01 — Act on something another user just deleted

- **Applies when:** two actors can see the same resource.
- **Try:** actor A opens or lists the resource; actor B deletes it; A acts on it.
- **User expects:** a clear "no longer exists", nothing half-done.
- **Typical failure:** 500, a ghost entry, or the action resurrects the resource.
- **Technique:** concurrency
- **Source:** seed

### H-INTR-01 — Interrupted long operation

- **Applies when:** upload, import, scan or any asynchronous job.
- **Try:** cancel or lose the connection mid-way; restart; repeat the operation.
- **User expects:** either a complete result or a clean failure with a way to retry.
- **Typical failure:** a stuck "in progress" state, partial data shown as complete.
- **Technique:** interruption
- **Source:** seed

### H-ROLE-01 — Permission removed during a session

- **Applies when:** roles or sharing can change while a user is active.
- **Try:** revoke the user's permission while they hold an open view or a token;
  let them continue.
- **User expects:** the next action is refused with an understandable message.
- **Typical failure:** the old session keeps full access until re-login.
- **Technique:** roles
- **Source:** seed

### H-BND-01 — Limits at, below and above

- **Applies when:** any documented size, count, length or rate limit.
- **Try:** limit − 1, limit, limit + 1; zero; empty.
- **User expects:** the limit is enforced exactly as documented, with a message that
  names the limit.
- **Typical failure:** off-by-one, or a generic error without the limit.
- **Technique:** boundary
- **Source:** seed

### H-ERR-01 — Error messages are actionable

- **Applies when:** any refusal the user can trigger.
- **Try:** each refusal path in the requirement.
- **User expects:** what went wrong and what to do next; no stack traces or internal ids.
- **Typical failure:** a generic "something went wrong", leaked internals.
- **Technique:** error-guessing
- **Source:** seed
```

### 5.3 Example for the project template (fictional product)

```markdown
### H-SYNC-01 — Source renamed between two syncs

- **Applies when:** a connector syncs files from an external storage account.
- **Try:** sync; rename a folder in the external account; sync again.
- **User expects:** the renamed folder appears once, under the new name, with its files.
- **Typical failure:** both names shown, or the files counted twice in search.
- **Technique:** state
- **Source:** interview 2026-10-23
```

### 5.4 Seeding procedure (part of implementing `blackbox-review`)

1. **Mine** the user's legacy API and UI suites and their test plans (read-only): extract
   recurring checks that are not derivable from code — negative inputs, data variety,
   repeated actions, role combinations, journeys. Each pattern becomes a candidate entry
   with `Source: mined: <file>`.
2. **Split** candidates: generic → kit file; product-specific → project file draft.
3. **Interview** the user with the grill procedure over gaps: "where do bugs usually hide",
   "what do you never forget to check", areas the mining did not cover.
4. **Review** both files with the user before they are committed (kit) or handed over
   (project file).

## 6. Errors and safety

| Situation | Response |
|---|---|
| Project-context key missing | `missing context` blocker naming the key |
| Authoring skill or `gh` unavailable | `missing capability` blocker |
| Requirement, inventory and code disagree | grill routes through `source-of-truth`; expectations never follow code |
| Requirement silent on a black-box finding | `question` finding, never a test |
| Ready label applied by a bot or by the night shift | PR skipped |
| Preflight fails | `blocked: environment`; no "not verified but green" |
| Denylist missing | no live run; safe checks only; PR labelled blocked |
| Budget exceeded | `blocked: budget`; partial work stays committed on the branch |
| Script crashes mid-PR | worktree kept and logged; rerun resumes |

Night-shift permissions: never `bypassPermissions` by default; forbidden actions are
merge, marking ready, recording approval, force-push and pushing to the default branch.
Every night-shift commit and comment carries a `night-shift run <id>` marker.

## 7. Verification

- **Kit tests** (`tests/test_kit_quality.py`): the four skills have valid metadata and
  consistent platform files; README, launcher and kit-only docs list them; the
  orchestrator routes them; the project-context template contains every key in 4.5; a new
  check that kit skills and the kit heuristics file contain no project-specific names
  from a deny-list kept in the test.
- **`bin/qa-night`:** shell syntax check, `--help`, `--dry-run` selection logic
  (human label vs bot label) against recorded `gh` JSON fixtures.
- **Skill behaviour:** `superpowers:writing-skills` pressure tests (with and without the
  skill) for each skill.
- **Manual acceptance on the first consumer** (on the work machine): backlog for one
  domain matches the coverage tool; grill one unit; black-box in both modes (one
  proposed brief, one finished scenario); one `qa-night --once` on a test draft PR.

## 8. Delivery order

1. `coverage-backlog` + project-context section + orchestrator routing.
2. `requirement-grill`.
3. `blackbox-review`, heuristics template, mining, interview, seeded kit file.
4. `night-shift` + `bin/qa-night`.

Each step is independently useful; 1–3 do not depend on 4.

## 9. Out of scope

- Changes to the authoring skill or to any target repository.
- Parallel night shifts.
- Storing the board anywhere.
- An architecture-deepening audit skill (candidate for a later iteration).
- Creating PR labels in the target repository (done by the user).
