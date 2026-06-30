# Companion Contract Spreadsheet Format

The `.xlsx` is a read-friendly projection of a Test Design Contract `.md`. Same
directory, same base name, `.xlsx` extension. The `.md` is the source of truth;
the spreadsheet is regenerated on every contract change. Generate it with
`scripts/contract_to_xlsx.py <contract.md>`.

## Workbook

Two sheets.

### Sheet 1 — `Test Cases`

One row per case (`TC-xxx`). Columns, in order:

| Column | Source in contract |
|---|---|
| `ID` | case id (`TC-001`) |
| `Name` | case title |
| `Priority` | `- Priority:` |
| `Request actor` | `- Request actor:` |
| `Target variants` | `- Target variants:` |
| `Preconditions` | `- Given:` |
| `Steps` | `- When:` |
| `Expected` | `- Then:` (joined with the API response status/assertions) |
| `API status` | `API response: Status` |
| `Business assertions` | `API response: Business assertions` |
| `Side effects` | `API response: Side effects` |
| `Cleanup` | `- Cleanup:` |
| `Evidence` | `- Evidence:` |

### Sheet 2 — `Contract`

Contract metadata as label/value rows: `Project`, `Status`,
`Requirement source`, `Scope`, `Exclusions`, `Next transition`.

## Formatting

- Bold header row, frozen (`freeze_panes` below the header).
- Wrap text in multi-line cells (Preconditions, Steps, Expected, etc.).
- Sensible column widths; auto-filter on the header row of `Test Cases`.
- Vertical-top alignment so multi-line rows read cleanly.

The script applies all of the above. Keep the column set stable so reviewers see
a consistent layout across contracts; extend it only via project context.
