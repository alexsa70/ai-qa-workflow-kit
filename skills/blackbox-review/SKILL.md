---
name: blackbox-review
description: Review proposed or finished test cases from the user's side only - the requirement and the cases, never the product code - and propose black-box additions (variants, new cases for an inventory unit, outside-inventory cases, and questions for the product owner) using test-design techniques and the kit and project heuristics files. Use after requirement-grill and before a scenario is claimed (proposed mode), or over finished scenarios of a domain (audit mode), when coverage derived from code may miss what users actually do. Never writes tests or scenarios.
---

# Black-Box Review

Coverage derived from code verifies what the code does. This review asks what
a user will do, expect and notice - including behaviour the code never
implemented. Independence from the implementation is the point: do not read
product source code during this review.

## Scope

Use this skill when:

- `proposed` mode: a grill brief or draft scenario exists and is not claimed;
- `audit` mode: finished scenarios and their tests of a domain are reviewed
  for user-side gaps.

Do not use it to decide a verdict on a transition (`qa-review-gate`), to
resolve a disputed fact (`source-of-truth`), or to write the additions (the
authoring skill named in `authoring.skill`).

## Required Input

- the mode: `proposed` or `audit`;
- the requirement, fetched as `requirements.source` describes;
- the inventory location, `requirements.inventory_paths`;
- the cases: a grill brief, or scenario files and their test classes;
- heuristics: `references/heuristics.md` in this skill, and the file named by
  `heuristics.project_file` when the key is set. If the key is set and the
  file is missing, say so and continue with the kit file only.

Out of bounds: product source code, configuration, inventory `src` citations,
code comments. Requirement and design documents count as requirements even
when they live in the backend repository. Test code is read only for what it
asserts, not for how the product works. Scenario files may carry provenance,
code citations or defect notes that point at code: skip those fields, and if
they were seen, mark the affected findings "may be influenced by code notes".

If the requirement is unavailable, use the scenario's own stated outcome and
preconditions as a stand-in, say so in the report header, and mark findings
that depend on it.

## Procedure

1. **Model the user.** From the requirement only: who the users are, what each
   wants, which journeys pass through this feature before and after it, which
   states the visible objects go through.
2. **Apply techniques** to every case and to the gaps between cases:
   equivalence classes and boundaries; state transitions (including invalid
   ones); decision tables over roles and settings; error guessing; journeys
   across features; interruption and recovery; retry and idempotency;
   concurrency between two actors or two sessions; data variety (languages,
   right-to-left text, sizes, empty, special characters); roles as the user
   experiences them.
3. **Apply heuristics.** For each heuristic whose "Applies when" matches, try
   its probe against the cases. Cite the heuristic id on every finding it
   produced: kit ids bare (`H-PERM-02`), project ids with a `P:` prefix
   (`P:H-FAULT-01`), because ids may repeat across the two files.
4. **Classify each finding:**
   - `variant` - an existing case gains a variant;
   - `new-case-in-inventory` - a new case for a unit already in the inventory
     (to tell it from `outside-inventory`, read inventory unit titles and
     descriptions, never their source citations);
   - `outside-inventory` - behaviour no inventory unit describes; a new case
     with an empty coverage list and an outside-inventory reason, and a P2
     backlog unit;
   - `question` - the requirement is silent or ambiguous. Never turn a
     question into an assumed expectation; route it through `source-of-truth`
     to the product owner.
5. **Rank.** Risk is high when a user would lose data, see another user's data,
   be blocked on the main path, or get a silent wrong result; medium when the
   user is confused or must retry; low otherwise. For a `question`, rate the
   risk of the behaviour the question is about.
   For back-end or API scenarios the "user" is the API client or the person
   using the product through it; "user would notice" means what that client
   observes in responses, later reads or search results.
6. **Report** with `assets/findings.md`.

## Rules

- Never read product source code in this review.
- In audit mode, a case with no test class is reviewed from its scenario text
  only and noted "no automation".
- Never write scenarios, tests, heuristics files or approval records.
- Every finding states what the user does and what the user would notice.
- Do not repeat what a case already checks; cite the case id when close.
- Prefer ten sharp findings over forty generic ones.

## Learning loop

When the user accepts or rejects a finding for a reason that generalises, offer
a new heuristic entry in the format of `references/heuristics.md` - generic
ones for the kit file, product-specific ones for the project file. Write it
only when the user asks.

## Completion

Report the mode, the sources read, the findings table and the heuristics
applied. Next permitted action: accepted `variant` and `new-case-in-inventory`
findings go into the grill brief or the scenario through the authoring skill;
`outside-inventory` findings go to `coverage-backlog`; `question` findings go
to `source-of-truth`.
