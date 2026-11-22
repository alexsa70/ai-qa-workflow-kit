---
name: bug-report
description: Investigate one observed product deviation and write a lean, tracker-ready bug draft as a Markdown file - verdict against the project's authority order first, then reproduction, severity and priority, duplicate search, a short description body, a field map for the tracker's native fields, and the investigation evidence kept apart for a first comment. Use when a test, a live run or a person observed behaviour that may be a product bug, or when bug-fixing classified a failure as a product bug. Never files, comments on or edits a ticket; a test-case or documentation mismatch is routed elsewhere, not drafted as a bug.
---

# Bug Report

Turn an observation into either a reasoned "this is not a bug" or a bug draft
a person can file in one step. The draft is a Markdown file; this skill never
writes to the tracker.

The file skeleton lives in [assets/bug-draft.md](assets/bug-draft.md).

## Scope

Use this skill when:

- `bug-fixing` classified a failure as `product bug`;
- a live run or a person observed behaviour that looks wrong;
- a suspected bug needs a verdict before anyone spends time on a ticket.

Route elsewhere:

| Need | Skill |
|---|---|
| Fix a failing test, client, schema or fixture | `bug-fixing` |
| Sources disagree and the controlling one is unclear | `source-of-truth` |
| The test case or scenario expectation is wrong | `test-design` |

## Required Input

From the user or the caller: what was observed, where, as whom, and the
command, request or steps that showed it.

From `ai-workflow/project-context.md`:

- the authority order and source registry (existing sections);
- section `Bug Report`:
  - `bug.output_dir` - where drafts are written (required);
  - `bug.tracker` - tracker and project the draft is meant for;
  - `bug.parent` - parent issue or epic new bugs go under;
  - `bug.priorities` - allowed priority values, highest first;
  - `bug.native_fields` - values that live in tracker fields, never in the body;
  - `bug.never_set` - fields left empty unless the user gives a value;
  - `bug.duplicate_search` - how to search open bugs (read-only query or
    command).

An empty `bug.output_dir` is a `missing context` blocker. An empty
`bug.duplicate_search` is not: record "duplicates not searched" in the draft.

## Hard Rules

1. **A bug is runtime behaviour that contradicts a confirmed controlling
   source.** A wrong test case, a stale document or an unclear source is not a
   product bug and never becomes a bug draft.
2. **Verdict before draft.** Run the decision below even for an "obvious" bug.
3. **Evidence, not memory.** The draft cites the controlling source (location
   and excerpt) and the observed result (how it was obtained, verbatim).
   Missing either one means `insufficient evidence`.
4. **Native fields stay in fields.** Summary, priority, parent, assignee and
   every value in `bug.native_fields` go in the field map, never in the body.
   Values in `bug.never_set` and the assignee stay empty unless the user gives
   them.
5. **Lean body.** Impact, Expected, Actual, Steps, Environment, Workarounds,
   Other. No hypothesis, authority chain or duplicate list in the body.
6. **Investigation evidence is a separate section** meant for the ticket's
   first comment.
7. **Never write to the tracker** - no create, comment, edit or transition.
   Reading for duplicates is allowed when `bug.duplicate_search` says how.
8. **No blanket test markers.** Do not suggest marking tests that were passing
   before as expected failures; a regression must stay visible.

## Procedure

### 1. Intake

Collect the observation, area, actor or role, environment, and the exact
reproduction artefact (failing test id and assertion, request and response, or
UI steps). Ask only for what is missing.

### 2. Verdict

Read the sources in the project's authority order and record every lookup.

| Situation | Verdict | Next |
|---|---|---|
| Behaviour matches the controlling source | `not a bug` | Explain what was checked; stop |
| Controlling source agrees with runtime; the test case expects otherwise | `test-case mismatch` | Route to `test-design`; stop |
| Two documents disagree and runtime matches the higher one | `stale documentation` | Note which document to fix; stop |
| Behaviour contradicts the controlling source | `product bug` | Continue |
| Controlling source missing, unreadable or contested | `insufficient evidence` | List what is missing; route conflicts to `source-of-truth`; stop |

Every verdict other than `product bug` still gets a short note in the output;
only `product bug` gets a draft file.

### 3. Reproduction

Write a minimal, deterministic recipe: request and expected versus actual
response for an API, or numbered steps with expected versus actual for a UI.
Include the exact test command and assertion text when a test showed it.

### 4. Severity and priority

Severity is the impact on the user:

| Severity | Meaning |
|---|---|
| Critical | Data loss, security breach, cross-tenant exposure, crash on a primary path |
| High | Primary journey broken, no workaround |
| Medium | Secondary feature broken, or primary degraded with a workaround |
| Low | Cosmetic, wording, edge case only |

Priority is urgency: score Risk, Frequency and Criticality as H=3, M=2, L=1
and multiply (max 27). Propose a value from `bug.priorities` - roughly the top
value for 18 and above, then descending bands at 12, 8 and 4 - and state the
score. If the band has no allowed value, propose the nearest one and say so.
The user decides at the gate.

### 5. Duplicate search

Run `bug.duplicate_search` with two to four keywords (area, operation, status
code or surface). List open matches with key, title and why each might or might
not be the same root cause. If a likely duplicate exists, stop and ask: draft a
new bug, or add context to the existing one instead.

### 6. Write the draft

Write `<bug.output_dir>/<yyyy-mm-dd>-<short-slug>-bug.md` from
[assets/bug-draft.md](assets/bug-draft.md): header, field map, description
body, investigation evidence, duplicates, suggested follow-ups.

### 7. Gate and close

Show the summary, field map and body. Revise until the user approves. Then the
status becomes `approved` and the user or a project tool files it; this skill
does not. If the user later gives the ticket key, record it in the header as
`filed as <key>` and suggest the follow-ups (a regression test for the fixed
behaviour, a test-case correction, a document fix).

An external write later made from this draft goes through `qa-review-gate`
with the `pre-external-write` lens.

## Output

- the verdict and the sources checked;
- for `product bug`: the draft path and status (`draft` or `approved`);
- open questions, unreadable sources and whether duplicates were searched;
- the next permitted transition.
