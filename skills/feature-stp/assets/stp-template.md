# STP - <Feature name> (<issue key, if any>)

- Type: Software Test Plan
- Status: draft | approved by <who>, <date>
- Project / scope: <project>, <feature>
- Next transition: user review -> handoff to <stp.handoff_skill>

## Sources

| Source | Location | Read |
|---|---|---|
| Product spec | <link or path> | yes / could not open |
| Design | <link or path> | yes / could not open / stand-in: product source |

## What the feature is

Two or three sentences in the reader's words: who uses it, what they do, what
they get.

## Requirements

| ID | Spec | Product requirement | This release | Test |
|---|---|---|---|---|
| R1 | 1 | <spec wording> | Yes (D1, D2) | TC-01 |
| R2 | Value proposition | <rule a person can observe> | Yes (D4) | TC-04 |
| R3 | 5 | <spec wording> | Not in this release | Out of scope |

Non-functional notes (not cases): ...

## Design decisions

| ID | Decision a tester will see |
|---|---|
| D1 | ... |

## Out of scope (and why)

| Item | Why |
|---|---|
| R3 | Not built in this release (D2). |
| <plumbing item> | Developer tests; no person-visible effect. |

## Shared setup

Written once; every case refers to it.

## Cases

### TC-01 <What a person does and sees>

- Protects: R1, D1, D2
- Checking: <one line>
- Preconditions: <short, beyond Shared setup>

| # | Action | Expected |
|---|---|---|
| 1 | ... | ... |

Matrix (when the case covers combinations):

| Type | Language | Expected |
|---|---|---|
| ... | ... | ... |

## Traceability

| Requirement / decision | Case(s) |
|---|---|
| R1 | TC-01 |
