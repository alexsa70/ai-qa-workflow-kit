# Project Heuristics - <project name>

Product-specific black-box heuristics for `blackbox-review`. Keep this file
next to the project context (untracked when the repository is shared) and set
`heuristics.project_file` to its path. Generic heuristics belong in the kit
file `skills/blackbox-review/references/heuristics.md`, not here.

Use the same entry format as the kit file. The example below is fictional.

### H-SYNC-01 - Source renamed between two syncs

- **Applies when:** a connector syncs files from an external storage account.
- **Try:** sync; rename a folder in the external account; sync again.
- **User expects:** the renamed folder appears once, under the new name, with its files.
- **Typical failure:** both names shown, or the files counted twice in search.
- **Technique:** state
- **Source:** interview: 2026-10-23

## Rejected findings

Findings the user turned down for one scenario, so `blackbox-review` does not
raise them again. One line each:
`- <scenario or case id> | <finding, short> | <why rejected> | <date>`

- CASE-01 | retry after timeout creates a duplicate | duplicates are merged by design (product decision) | 2026-10-24
