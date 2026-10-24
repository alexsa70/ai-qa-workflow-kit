# Black-Box Findings - <scenario or domain>

- Mode: proposed | audit
- Requirement: <reference> (read | unavailable)
- Cases reviewed: <brief title | scenario ids>
- Heuristics files: kit references/heuristics.md; project <path | not set>
- Sources read: <requirement, scenario files, test classes, inventory titles>
- Heuristics applied: <ids; project ids prefixed P:>
- Inventory: <read | unavailable - all new cases classified outside-inventory>
- Not examined: <scenarios or areas skipped, or none>
- Flags: <#row> may be influenced by code notes; <#row> no automation; <#row> depends on stand-in requirement

| # | Category | Risk | Case or unit | User does | User would notice | Heuristic | Suggested addition |
|---|---|---|---|---|---|---|---|
| 1 | variant | high | <case id> | <...> | <...> | H-XXX-01 | <difference from the existing case; id assigned by the authoring skill> |
| 2 | new-case-in-inventory | medium | <unit id> | <...> | <...> | H-XXX-03 | <case title> |
| 3 | outside-inventory | medium | - | <...> | <...> | H-XXX-02 | <case title; outside-inventory reason> |
| 4 | question | medium | <case id> | <...> | <...> | - | <question for the product owner> |

Heuristic column: one or more ids (kit bare, project `P:`-prefixed), or `-` only for findings that came from modelling the user without a heuristic. Risk for a `question` is the risk of the behaviour it asks about.

Not raised (already covered): <case id - heuristic id> (one per line)

Not raised (previously rejected): <rejected-finding reference> (one per line)
