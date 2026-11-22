---
name: feature-stp
description: Write a product-facing Software Test Plan (STP) for one feature as a Markdown file, from its product spec and its design document. Mapping is mandatory - product spec to requirements, design to implementation decisions, test cases only from those two lists - and the cases are few, readable by a tester from the title, and free of internal plumbing. Use when the user asks for an STP, a feature test plan, or "what should we test" for a new feature, for readers outside the automation team (lead, product, manual tester). Do not use for an automation contract (test-design), for writing tests (test-implementation), or for publishing the plan anywhere.
---

# Feature STP

Turn a feature's product spec and design into a short test plan a person can
run. The plan is a Markdown file; this skill never publishes it and never
writes tests or test-management cases.

A worked example of the shape lives in
[assets/worked-example.md](assets/worked-example.md); the file skeleton in
[assets/stp-template.md](assets/stp-template.md).

## Scope

Use this skill when:

- a new feature needs a test plan before any automation or case fan-out;
- a draft plan reads like the backend contract and must become product-facing;
- someone asks "what do we test for this feature" and the answer must survive
  the conversation.

Route elsewhere:

| Need | Skill |
|---|---|
| Automation scope, actors, assertions, cleanup | `test-design` |
| Unknown or conflicting behaviour | `source-of-truth` |
| One unit's cases agreed question by question | `requirement-grill` |
| User-side gaps in finished cases | `blackbox-review` |

## Required Input

From the user: the feature name and, when the project uses one, its issue key.

From `ai-workflow/project-context.md`, section `Feature STP`:

- `stp.spec_source` - where and how the product spec is fetched;
- `stp.design_source` - where and how the design document is fetched;
- `stp.output_dir` - where the Markdown file is written;
- `stp.style_guide` - optional; the project's guide for reader-facing prose;
- `stp.handoff_skill` - optional; who turns the approved STP into cases
  (default `test-design`).

An empty `stp.output_dir` is a `missing context` blocker. A spec or design that
cannot be opened is reported as such, never paraphrased from memory.

## Hard Rules

1. **Two layers, then tests.** Product spec gives requirements; design gives
   implementation decisions. Cases come from those two lists only.
2. **Product wording stays product wording.** What this release actually builds
   (which fields, which languages, off by default) goes in the "This release"
   column, never into the requirement cell.
3. **A tester understands the case from its title.** Describe what a person
   does and sees. No identifiers, endpoints or field names in titles. Follow
   `stp.style_guide` when set.
4. **Few cases.** A simple feature is a handful of cases. Combinations (type x
   language x source) are a matrix inside one case, not one case per cell.
5. **Do not invent surfaces.** Only controls, languages and fields the release
   ships. A spec item the build skipped stays a requirement marked "not in
   this release"; it does not become a case.
6. **Do not test plumbing.** Protocols, request validation, storage pointers,
   sequence numbers and schema extras belong to developer tests.
7. **Out of scope needs a why.** "Covered by the existing permission tests" is
   a why. Silence is not. When you cut a requirement because something else
   covers it, name what would have to be wrong for the cut to be wrong.
8. **Talk before growing the plan.** Propose cases, then wait. Propose extras
   after the first draft, then wait. Never add cases unprompted.
9. **Plan ids never collide with spec numbers.** R7 in the plan is not item 7
   of the spec; the spec number goes in its own column. Value-proposition rules
   cite "Value proposition", not an invented requirement number.
10. **Never claim to have read what you could not open.** Ask for a local copy
    of a gated design, or stop. Product source code is a last-resort stand-in
    and is labelled as such in Sources.

## Procedure

### Phase 0 - Locate sources

1. Fetch the product spec as `stp.spec_source` says.
2. Fetch the design as `stp.design_source` says; if it is missing, ask for it
   (a local HTML, PDF or path is fine). Keep only decisions a tester would see;
   endpoint shapes are evidence for a decision, not cases.
3. Note any checks the user already expects. They limit volume; they do not
   replace the two layers.

If either source is missing after asking, stop and say which.

### Phase 1 - Product spec to requirements

List every functional requirement the spec states, in the spec's own product
language, including value-proposition rules a person can observe (for example
"at the moment of need" means existing items are not processed until someone
asks). Keep a row even when the build skipped it. Non-functional items sit under
the table, not as cases, unless the user asks.

### Phase 2 - Design to implementation decisions

Number them D1, D2, ... One row per choice that changes what a tester sees:
what is actually built, which language or format pairs, what a switch hides
versus what it starts, cache or reuse scope, same-value / empty / names
behaviour, and anything a tester would otherwise mark as a failure.

### Phase 3 - Mapping table (show before any case)

| ID | Spec | Product requirement | This release | Test |
|---|---|---|---|---|
| R1 | 1 | spec wording | Yes / No, with D-refs | TC-0N, "existing <area> tests", or "out of scope" |

Then the Design table (D1...), then Out of scope with a why for each row. The
user reviews this before cases exist.

### Phase 4 - Propose cases (gate)

Collapse the Test column to the smallest set that still protects every row in
this release. Recurring shapes: the happy path as a matrix, a feature switch
off then on, reuse across people, existing items waiting until someone asks,
and access to anything derived from a protected item.

Show the list and wait. If the user rejects a case, keep the requirement, move
its Test cell to the covering tests or "out of scope", and write the why.

### Phase 5 - Write the STP file

Write `<stp.output_dir>/<feature-slug>[-<issue-key>]-stp.md` from
[assets/stp-template.md](assets/stp-template.md). Order: header, Sources, What
the feature is, Requirements, Design, Out of scope, Shared setup (once),
Cases, Traceability.

Each case: a title a tester can run from; Protects (R and D ids); one line
"what you are checking"; short preconditions; a step table of action and
expected result. A design nuance that would cause a false failure goes into
the expected result.

When the file already exists and a person may have edited it, read it first
and change only what this run owns; never overwrite it wholesale.

Do not publish the file, create test-management cases or write tests.

### Phase 6 - Close

- Re-read the Requirements table: is each requirement cell still product
  wording, and are plan ids clear of spec numbers?
- Ask whether any other functional case is worth adding; add nothing until the
  user says so.
- If cases or automation are wanted next, hand the approved STP to
  `stp.handoff_skill` (default `test-design`) as its requirement source. Do
  not re-derive the plan from the backend contract.

## Output

- the STP file path and its status (`draft` or `approved by <who>`);
- open questions and any source that could not be opened;
- the next permitted transition (user review, then handoff).
