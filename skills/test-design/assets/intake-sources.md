# Requirement Intake Sources

Reference for turning a requirement source into normalized, attributed evidence
during `test-design` Step 1. A source states *what to cover*; it never proves
*how the product behaves*. Confirm asserted behavior through `source-of-truth`
against the project authority order before a case leaves `draft`.

## Per-Source Handling

### Outline document link

- Retrieve the page only through a project-authorized Outline connector,
  command, or local export path. If none is configured, ask the user to paste
  the page body and record access as `user-provided`.
- Keep the page URL (and revision/updated date when available) for traceability
  and freshness.
- Treat narrative description as requirement context; treat any stated API
  status codes, payloads, roles, or thresholds as `unverified` claims.

### Jira issue

- Accept an issue key (e.g. `KS-2846`) or URL. Retrieve through an authorized
  Jira connector; otherwise ask for pasted content.
- Separate **acceptance criteria** (the requirement) from **comments,
  estimates, and speculation** (context only).
- Preserve the issue key for the handoff and for linking the contract back to
  the ticket.
- A linked sub-task or epic is additional context, not automatic scope. Confirm
  scope with the user when an epic spans multiple features.

### Testmo case or run

- Accept a case ID, suite, or run reference. Treat existing steps and expected
  results as **prior design**, not confirmed product behavior.
- Reconcile each Testmo expected result with the controlling source before
  reuse. If they disagree, route through `source-of-truth` and prefer the
  controlling source.
- Preserve the Testmo case ID and carry it into each generated case so the
  contract and the implemented test stay traceable to Testmo.
- When the request is to *extend* Testmo coverage, list which existing case IDs
  are reused unchanged, which are revised, and which are net-new.

### Free text

- Restate the requirement back in normalized form so scope is explicit before
  approval.
- Extract any implied expected behavior into discrete `unverified` claims.
- Ask one consolidating question only when scope, actors, or intended behavior
  cannot be derived safely.

## Mixed Sources

When more than one source is supplied (for example a Jira issue that links an
Outline page and references a Testmo run):

- Record `Source type: mixed` and list every reference.
- Establish one controlling requirement; treat the others as supporting context.
- Resolve any cross-source contradiction through `source-of-truth` before
  building cases. Do not silently choose one wording.

## Claim Ledger

Maintain a short ledger so verification status stays visible:

| Claim | Source | Status | Controlling source | Resolution |
|---|---|---|---|---|
| e.g. POST returns 201 with body | JIRA KS-1234 | unverified | backend route | confirmed via source-of-truth |

A case whose expected result is still `unverified` cannot move to
`awaiting-approval`.
