# Bug draft - <one-line summary>

- Type: bug report draft
- Status: draft | approved by <who>, <date> | filed as <key>
- Project / area: <project>, <area>
- Verdict: product bug
- Next transition: user review -> separate approval + qa-review-gate -> filed

## Field map (tracker native fields)

| Field | Value |
|---|---|
| Summary | <area>: <observed deviation>, at most 255 characters |
| Parent | <bug.parent> |
| Priority | <value from bug.priorities> (score R x F x C = <n>) |
| Assignee | unassigned unless given |
| <other bug.native_fields> | ... |

Left empty on purpose: <bug.never_set>.

## Description body

### Impact
One or two sentences: what the user sees and what it costs them. No
hypothesis.

### Expected behaviour
One short paragraph in product language.

### Actual behaviour
- Concrete observed deviation, no speculation.

### Steps to reproduce
1. ...
2. ...

### Environment
- Environment / URL:
- Build or commit:
- Role:
- Client:

### Workarounds
N/A

### Other information
Affected ids, related tickets, attachments to add.

## Investigation evidence (first comment, not the body)

| Source | Location | Excerpt / result |
|---|---|---|
| Controlling source | <path or link, fetched date> | <verbatim excerpt> |
| Other sources consulted | ... | ... |
| Observed result | <test id, request or log, timestamp> | <verbatim> |

Root-cause hypothesis (not a confirmed fix): ...

Severity rationale: <Critical / High / Medium / Low> because ...

## Duplicates

Search: <query or "not searched - bug.duplicate_search is empty">

| Key | Title | Same root cause? |
|---|---|---|

## Suggested follow-ups

- Regression test for the expected behaviour once fixed.
- Test-case or document correction, if the investigation found one.
