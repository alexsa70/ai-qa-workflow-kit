# Black-Box Findings - <scenario or domain>

- Mode: proposed | audit
- Requirement: <reference> (read | unavailable)
- Cases reviewed: <brief title | scenario ids>
- Heuristics files: kit references/heuristics.md; project <path | not set>
- Sources read: <requirement, scenario files, test classes, inventory titles>
- Heuristics applied: <ids; project ids prefixed P:>

| # | Category | Risk | Case or unit | User does | User would notice | Heuristic | Suggested addition |
|---|---|---|---|---|---|---|---|
| 1 | variant | high | <case id> | <...> | <...> | H-XXX-01 | <variant id and difference> |
| 2 | new-case-in-inventory | medium | <unit id> | <...> | <...> | - | <case title> |
| 3 | outside-inventory | medium | - | <...> | <...> | H-XXX-02 | <case title; outside-inventory reason> |
| 4 | question | - | <case id> | <...> | <...> | - | <question for the product owner> |

Heuristic column: one or more ids (kit bare, project `P:`-prefixed), or `-`.

Not raised (already covered): <case id - heuristic id> (one per line)
