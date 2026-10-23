---
name: requirement-grill
description: Interview the user relentlessly, one question at a time with a recommended answer for each, about one requirement-inventory unit (or a small related group) until requirement, inventory, code and expectation are aligned, then write a grill brief that the project's authoring skill takes as input. Use before admitting or claiming a new scenario, when a unit's expected behaviour, variants, cleanup or scope is unclear, or when a meeting transcript or requirement page must be turned into agreed cases. Never writes scenarios or tests.
---

# Requirement Grill

Reach a shared understanding of one unit before anything is claimed or
written. The output is not a plan; it is the agreed design of the cases,
including what is deliberately not claimed.

## Scope

Use this skill when:

- a unit chosen from `coverage-backlog` is about to be claimed;
- expected behaviour, variants, cleanup or scope of a unit is unclear;
- a requirement page or meeting transcript must become agreed cases.

Do not use it to write the scenario or the test (the authoring skill named in
`authoring.skill`), to resolve a factual conflict by itself
(`source-of-truth`), or to propose black-box additions (`blackbox-review`).

## Required Input

- the unit id(s) and the inventory entry, from `requirements.inventory_paths`;
- the requirement source, fetched as `requirements.source` describes;
- the backend code the inventory entry cites, read-only, from
  `backend.checkout`;
- `authoring.skill`, to shape the brief for it.

A missing key is a `missing context` blocker. A requirement or design
document that cannot be fetched is recorded under "Sources read" as
unavailable, never imagined; it is not a blocker by itself. Record both the
target sha and the backend checkout sha in the brief. If the checkout lacks
code the inventory cites, add "backend checkout may be stale" to Open
questions instead of reading another revision.

## Procedure

1. **Read first, ask second.** Read the inventory entry, the cited code and
   the requirement. Note every disagreement between them before the first
   question. If the coverage tool or the scenario files show the unit is
   already covered by an approved scenario, do not grill it as new: report the
   scenario id and offer two paths - grill only an uncovered variant or gap of
   it, or, only if the expected behaviour itself changed, prepare a successor
   scenario (the authoring skill decides ids).
2. **Interview.** Ask exactly one question per message. Every question carries
   your recommended answer and why. Prefer a short list of real alternatives.
   Use the platform's question tool when it exists; plain text otherwise.
3. **Walk the decision tree.** Resolve these branches, in this order, and
   follow any sub-branch an answer opens:
   1. the observable outcome - what exactly is asserted, and where a user or
      client would see it;
   2. disagreements - requirement vs inventory vs code. Route each through
      `source-of-truth`: record the conflict in the brief's Open questions and
      invoke that skill when it is available in the session, otherwise ask the
      user. While unresolved, the affected case stays open and the brief is
      marked not ready for the authoring skill. Never change an expectation to
      match the code; a known defect is recorded, not made green;
   3. actor, organisation set-up and variants;
   4. preconditions and test data, and how runs avoid colliding;
   5. waiting - what is polled, how often, the deadline and its start event;
   6. cleanup - what the case creates, how it is removed, how removal is
      proven;
   7. the failing run - what evidence a failure must record;
   8. what is **not** claimed, and options considered and rejected, with why.
4. **Stop when aligned.** Stop when every branch has an answer or an explicit
   open question. The user may also stop the interview; record what remains
   open.
5. **Write the brief.** Fill `assets/grill-brief.md`. Keep it in chat or in a
   scratch file outside the repository. It lives only until the claim: after
   that the scenario and its pull request are the record.

## Rules

- One question per message; always a recommendation.
- Never read a fact into the brief that no source showed; mark it open.
- The critical flag comes from the inventory entry or the coverage tool; if
  neither is readable, write "unknown".
- When the user accepts a recommendation, that is their answer; record it
  normally, with no separate marking.
- Never write repository files, scenarios, tests or approval records.
- The brief names units by their inventory ids exactly as the inventory spells
  them.

## Completion

Report the brief, the open questions and the sources read. Next permitted
action: `blackbox-review` in `proposed` mode on the brief, then the authoring
skill's claim with the brief as its input.
