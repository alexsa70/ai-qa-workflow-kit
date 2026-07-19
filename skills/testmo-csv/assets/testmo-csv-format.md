# Testmo Import CSV Format

The column set proven to import into Testmo. Header, in this exact order:

```text
Name,Automated,Description,Expected,Folder,Pre-conditions,State,Steps,Tags
```

## Cell Rules

- **Encoding:** UTF-8, comma-delimited, `\n` line endings.
- **Quoting:** wrap a cell in double quotes if it contains a comma, a double
  quote, or a newline. Escape an inner `"` by doubling it: `""`.
- **Multi-line cells:** `Description`, `Pre-conditions`, `Steps`, and `Expected`
  may span multiple lines inside one quoted cell. This is expected and correct.
- One data row per test. Keep a stable order (file, then definition order).

## Value Rules

| Column | Value |
|---|---|
| `Name` | Test title (human-readable). |
| `Automated` | `Yes`. |
| `Description` | 1–2 sentences on the behavior under test. |
| `Expected` | Asserted outcome: status code(s), response fields, side effects. |
| `Folder` | `test_<snake>.py` → Title Case of `<snake>`. Optionally service-prefixed (`Service Name/Folder`) when project context says so. |
| `Pre-conditions` | Required state before the action (role, owned resource, seeded data). |
| `State` | `Active`. |
| `Steps` | Numbered list: `1. …` newline `2. …`. **Each step ends with the endpoint(s) it exercises**, appended as ` -> METHOD /path` (chain multiple with ` -> `), e.g. `2. Create a folder with image_id. -> POST /api/folders/create`. A non-request step (a pure wait/assert with no call) needs no endpoint. |
| `Tags` | Comma-separated in one cell: `api-automation` + `positive` or `negative`. |

## Folder Derivation

```text
test_conversation_editing.py   -> Conversation Editing
test_edit_possible_words.py     -> Edit Possible Words
test_positive_login.py          -> Positive Login
```

Strip the leading `test_` and the `.py`, split on `_`, Title-Case each word,
join with spaces.

## Tag Polarity

- `positive` — the test asserts a success (typically `2xx`).
- `negative` — the test asserts a rejection (typically `4xx`/`5xx`) or an error
  contract.

Decide from the actual assertion, not the test name. Use the `positive` /
`negative` pytest marker when present; otherwise infer from the asserted status.

## Worked Example (one row)

Header + one row, showing quoting and multi-line cells:

```text
Name,Automated,Description,Expected,Folder,Pre-conditions,State,Steps,Tags
"Edit possible words — regular user forbidden (401/403)",Yes,"A regular (non-admin) user calling edit_possible_words on a real rule must be rejected.","HTTP 401 or 403 — auth enforced on a real rule_id.","Edit Possible Words","Admin and a regular user are authenticated. An agent with a word_count rule exists (admin-owned).",Active,"1. Create agent with a word_count rule as admin to get a real rule_id. -> POST /api/agents/create
2. GET the agent to extract rule_id and org_id. -> POST /api/agents/get
3. Call edit_possible_words with regular-user credentials against the real rule_id. -> POST /api/agents/edit_possible_words
4. Assert the response is 401 or 403.","api-automation,negative"
```
