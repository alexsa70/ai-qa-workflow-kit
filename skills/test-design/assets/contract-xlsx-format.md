# Companion Contract Spreadsheet Format

The `.xlsx` is a read-friendly projection of a Test Design Contract `.md`. Same
directory, same base name, `.xlsx` extension. The `.md` is the source of truth;
the spreadsheet is regenerated on every contract change. Generate it with
`scripts/contract_to_xlsx.py <contract.md>`.

## Workbook

Three sheets.

### Sheet 1 — `Test Cases`

One row per case (`TC-xxx`), case-level fields only. Per-step detail lives on
the `Steps` sheet. Columns, in order:

| Column | Source in contract |
|---|---|
| `ID` | case id (`TC-001`) |
| `Name` | case title |
| `Priority` | `- Priority:` |
| `Request actor` | `- Request actor:` |
| `Target variants` | `- Target variants:` |
| `Preconditions` | `- Given:` |
| `Cleanup` | `- Cleanup:` |
| `Evidence` | `- Evidence:` |

### Sheet 2 — `Steps`

One row per step, so reviewers can scan the example request/payload and pass
criteria for each step without opening the `.md`. Columns, in order:

| Column | Source in contract |
|---|---|
| `Case ID` | the enclosing case id (`TC-001`) |
| `Step #` | position in the numbered `Steps` list |
| `Action` | the numbered step's leading line |
| `Request` | `- Request:` |
| `Example payload` | `- Example payload:` |
| `Status` | `Pass criteria: Status` |
| `Message` | `Pass criteria: Message` |
| `Value checks` | `Pass criteria: Value checks` |
| `Schema` | `Pass criteria: Schema` |
| `Headers` | `Pass criteria: Headers` |
| `Error contract` | `Pass criteria: Error contract` |
| `Side effects` | `Pass criteria: Side effects` |

### Sheet 3 — `Contract`

Contract metadata as label/value rows: `Project`, `Status`,
`Requirement source`, `Scope`, `Exclusions`, `Next transition`.

## Formatting

- Bold header row, frozen (`freeze_panes` below the header), on every sheet.
- Wrap text in multi-line cells (Preconditions, Example payload, Value checks,
  etc.).
- Sensible column widths; auto-filter on the header row of `Test Cases` and
  `Steps`.
- Vertical-top alignment so multi-line rows read cleanly.

The script applies all of the above. Keep the column set stable so reviewers see
a consistent layout across contracts; extend it only via project context.
