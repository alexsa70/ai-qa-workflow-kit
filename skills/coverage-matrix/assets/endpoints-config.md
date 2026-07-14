# `endpoints.json` — endpoint list format

The builder reads a JSON array where each entry is a 3-tuple describing one
endpoint, in **documentation order**:

```json
[
  ["/api/agents/create",   "Create Agent",              "POST"],
  ["/api/agents/get",      "Get Agent",                 "POST"],
  ["/api/agents/get_all",  "Get All Agents",            "POST"]
]
```

| Position | Field         | Notes |
|----------|---------------|-------|
| 0        | `path`        | Must match what the API client actually requests. |
| 1        | `section_title` | Human title from the API doc; becomes the sheet name (truncated to 31 chars, Excel limit). |
| 2        | `method`      | `POST` / `GET` / …; shown in the sheet header `METHOD /path`. |

## Rules of thumb

- **Path must match the client, not just the doc.** The builder maps a test to an
  endpoint via the client method's request path. If the client builds an f-string
  path (e.g. `f"/api/files/{file_id}"`), the config `path` must be
  `"/api/files/{file_id}"` — not a prettified doc form like
  `"/api/files/{file_id}?token="`. The builder reconstructs f-strings keeping
  `{placeholders}`.
- **Per-provider / templated endpoints:** if the client uses
  `f"/api/{connector_type}_connector/get_scan_tasks"`, use that exact templated
  string as the `path`.
- **Include zero-test endpoints.** Every endpoint the service exposes should be
  listed; empty sheets are how gaps stay visible.
- **Order matters** only for readability (sheets are emitted in list order).
- **Section titles should be distinct** within a service (they are sheet names).

## Source of truth

Pull the endpoint set from the project's authoritative API documentation
(Outline/Confluence page, OpenAPI/Swagger spec) — not from memory. Reconcile with
the code: if the docs list a removed endpoint, drop it; if the client exposes one
the docs omit, add it and flag the doc gap. Keep the resulting `endpoints.json`
files with the project (or its context), not in this skill.
