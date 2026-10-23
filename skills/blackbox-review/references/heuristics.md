# Black-Box Heuristics - Kit Level

Generic heuristics for any product. Product-specific heuristics live in the
project heuristics file named by `heuristics.project_file`. No product,
service, environment or company names in this file.

Entry format:

```markdown
### H-<AREA>-<NN> - <short name>

- **Applies when:** <what in a requirement or case makes it relevant>
- **Try:** <the concrete probe or variation>
- **User expects:** <the black-box oracle, in user terms>
- **Typical failure:** <what usually goes wrong>
- **Technique:** <boundary | equivalence | state | decision-table | error-guessing | journey | concurrency | interruption | data | roles | recovery>
- **Source:** <mined: suite/file | interview: date | review finding: reference | seed>
```

### H-RETRY-01 - Retry after a timeout must not duplicate

- **Applies when:** a create or submit action can time out or the client retries.
- **Try:** send the same create twice with the same payload; repeat after an artificial client timeout.
- **User expects:** one resource, or a clear "already exists"; never two silent copies.
- **Typical failure:** duplicate records, or the second call fails with a raw server error.
- **Technique:** error-guessing
- **Source:** seed

### H-DATA-01 - Bidirectional and non-Latin text survives the round trip

- **Applies when:** a user-supplied name, title, filename or free text is stored and shown again.
- **Try:** right-to-left text, mixed right-to-left and left-to-right with digits, combining characters, emoji, leading and trailing spaces, the maximum length in multi-byte characters.
- **User expects:** the same text back, searchable, correctly ordered.
- **Typical failure:** reversed or truncated text, failed search, a length limit counted in bytes instead of characters.
- **Technique:** data
- **Source:** seed

### H-STATE-01 - Act on something another user just deleted

- **Applies when:** two actors can see the same resource.
- **Try:** actor A opens or lists the resource; actor B deletes it; A acts on it.
- **User expects:** a clear "no longer exists", nothing half-done.
- **Typical failure:** a server error, a ghost entry, or the action brings the resource back.
- **Technique:** concurrency
- **Source:** seed

### H-INTR-01 - Interrupted long operation

- **Applies when:** an upload, import, scan or any asynchronous job.
- **Try:** cancel or lose the connection midway; restart; repeat the operation.
- **User expects:** either a complete result or a clean failure with a way to retry.
- **Typical failure:** a stuck "in progress" state, or partial data shown as complete.
- **Technique:** interruption
- **Source:** seed

### H-ROLE-01 - Permission removed during a session

- **Applies when:** roles or sharing can change while a user is active.
- **Try:** revoke the user's permission while they hold an open view or a token; let them continue.
- **User expects:** the next action is refused with an understandable message.
- **Typical failure:** the old session keeps full access until the next sign-in.
- **Technique:** roles
- **Source:** seed

### H-BND-01 - Limits at, below and above

- **Applies when:** a documented size, count, length or rate limit.
- **Try:** limit minus one, the limit, limit plus one; zero; empty.
- **User expects:** the limit is enforced exactly as documented, with a message that names it.
- **Typical failure:** off-by-one, or a generic error that does not name the limit.
- **Technique:** boundary
- **Source:** seed

### H-ERR-01 - Error messages are actionable

- **Applies when:** any refusal the user can trigger.
- **Try:** each refusal path in the requirement.
- **User expects:** what went wrong and what to do next; no stack traces or internal ids.
- **Typical failure:** a generic "something went wrong", or leaked internals.
- **Technique:** error-guessing
- **Source:** seed

### H-CTRL-01 - Positive control before a negative

- **Applies when:** a case proves that someone or something is refused, hidden or excluded.
- **Try:** first run the same action as an allowed party on the same object and confirm it works; then run the refused variant.
- **User expects:** the refusal is real: the object is reachable by those allowed and only by them.
- **Typical failure:** the negative check passes only because the object never existed, was not yet processed, or was typed wrong.
- **Technique:** roles
- **Source:** mined: test plans, interview: 2026-10-23

### H-PERM-01 - Permission leak through derived data

- **Applies when:** a feature produces data from a protected item: translation, summary, keywords or tags, extracted text, snippet, preview, answer, count, saved link.
- **Try:** as a user without access, look for that derived data through every surface: search snippets, tags, counts, generated answers, translations, links saved earlier.
- **User expects:** a user who cannot open the item sees nothing derived from it, not even that it exists.
- **Typical failure:** the item is protected but its text, tags or counts show up in a side channel.
- **Technique:** roles
- **Source:** mined: test plans, mined: legacy API suite, interview: 2026-10-23

### H-PERM-02 - Roles by tenants matrix

- **Applies when:** a feature is reachable by more than one role or tenant.
- **Try:** table every role (including no token and an unknown token) against own tenant, other tenant and a spoofed tenant id, for read and for write; compare the refusal text for a missing and a forbidden object.
- **User expects:** each cell gives the documented allow or refusal; a refusal does not reveal whether the object exists.
- **Typical failure:** wrong refusal code, cross-tenant data, or a "not yours" answer that confirms existence.
- **Technique:** decision-table
- **Source:** mined: legacy API suite, mined: legacy UI suite, mined: test plans, interview: 2026-10-23

### H-PERM-03 - Access follows a move or a state change

- **Applies when:** an object can move between folders or owners, or change state such as pending, rejected or approved.
- **Try:** move or change state, then retry access through an old link, an old listing, search and download as users who gained or lost access.
- **User expects:** access matches the new location or state at once; links to a pending or rejected object stay closed.
- **Typical failure:** access persists after a move, or a pending object is searchable, shareable or downloadable.
- **Technique:** state
- **Source:** mined: legacy API suite, mined: legacy UI suite, interview: 2026-10-23

### H-PERM-04 - Run against every tenant type

- **Applies when:** the product has tenants of different kinds, for example public and private organisations.
- **Try:** repeat the main journey and the permission cases in each tenant type.
- **User expects:** the feature behaves as documented in each type, with no data crossing between them.
- **Typical failure:** a flow tested only in the default tenant type breaks or over-exposes data in the other.
- **Technique:** equivalence
- **Source:** mined: legacy API suite, interview: 2026-10-23

### H-PERSIST-01 - Persistence and a second look

- **Applies when:** a user creates, edits, deletes or counts something.
- **Try:** after the action reload, then look again as another user, from another feature surface, and compare counts before and after; verify deleted items stay gone and the list is still populated.
- **User expects:** the same state everywhere; no optimistic screen that lies.
- **Typical failure:** the change shows only in the current view, a deleted item returns, or counts differ between surfaces.
- **Technique:** state
- **Source:** mined: legacy UI suite, mined: test plans, interview: 2026-10-23

### H-ASYNC-01 - Search index drifts from the store

- **Applies when:** content is saved in one place and searched or answered from a derived index.
- **Try:** change, rename, move, re-permission and delete an item; then query by the new value, the old value and a planted unique word.
- **User expects:** search shows the current state only; the old name finds nothing; the new content is found.
- **Typical failure:** the index keeps ghosts of deleted items or misses new ones; old and new states both answer.
- **Technique:** state
- **Source:** mined: legacy API suite, mined: test plans, interview: 2026-10-23

### H-ASYNC-02 - Delete or change while the item is still being processed

- **Applies when:** an upload or import is followed by background processing.
- **Try:** delete, rename, move or re-permission the item at each processing stage, including right after the upload answer.
- **User expects:** the item ends up gone or in its latest state, with no ghost in lists, search or storage.
- **Typical failure:** processing finishes and brings the deleted item back, or leaves orphan data.
- **Technique:** concurrency
- **Source:** mined: legacy API suite, interview: 2026-10-23

### H-ASYNC-03 - Work continues after the first answer

- **Applies when:** a request returns success while the real work finishes later.
- **Try:** check the end result after the wait; make several edits in a burst; check too early and too late; poll with a time limit per kind of operation.
- **User expects:** the final state equals the last edit and appears within the documented time; early checks do not give false failures.
- **Typical failure:** the first answer was success but the follow-up work failed silently, or a slower earlier step overwrites a later edit.
- **Technique:** state
- **Source:** mined: legacy API suite, mined: test plans, interview: 2026-10-23

### H-SYNC-01 - Change at the external source

- **Applies when:** a connector or import mirrors content from an external account.
- **Try:** rename, move and delete items and folders at the source; rescan; search by old and new name.
- **User expects:** the product mirrors the source: renamed once, moved once, deleted gone, nothing duplicated.
- **Typical failure:** both names shown, the old name still finds the item, or deleted items stay.
- **Technique:** state
- **Source:** mined: test plans, interview: 2026-10-23

### H-SYNC-02 - Same item from two sources

- **Applies when:** an item can enter by upload and by a connector, or from two connectors.
- **Try:** add a twin with the same name and content from another source; search and filter by name, type, source and date; delete one.
- **User expects:** both are findable and distinguishable; a source filter returns only that source; deleting one leaves the other.
- **Typical failure:** the twin replaces or hides the original, or leaks into a filtered result.
- **Technique:** equivalence
- **Source:** mined: legacy API suite, mined: test plans, interview: 2026-10-23

### H-SYNC-03 - Credentials expire mid-sync

- **Applies when:** a connector authenticates to an external account with a token or grant.
- **Try:** let the grant expire or revoke it during a sync, then reconnect and rescan.
- **User expects:** a visible "reconnect" state; after reconnect, sync resumes without loss or duplicates.
- **Typical failure:** sync stays "in progress" forever, or reconnect re-imports everything twice.
- **Technique:** recovery
- **Source:** interview: 2026-10-23

### H-FAULT-01 - Kill the worker that holds the item

- **Applies when:** an item is processed by a background job or worker.
- **Try:** restart or kill the backend process while it processes the item; wait; check the item.
- **User expects:** processing resumes or fails cleanly with a retry; the user sees the real state.
- **Typical failure:** the item is lost, processed twice, or stuck "in progress" without an error.
- **Technique:** recovery
- **Source:** mined: test plans, interview: 2026-10-23

### H-FAULT-02 - Interrupt the request mid-flight

- **Applies when:** a request carries a large body or starts a multi-step operation.
- **Try:** drop the connection, close the tab or abort the call midway; then retry and list what exists.
- **User expects:** either complete or nothing; a retry works and does not leave a ghost item.
- **Typical failure:** a half-created item that cannot be completed, deleted or re-uploaded.
- **Technique:** interruption
- **Source:** mined: legacy API suite, mined: legacy UI suite, interview: 2026-10-23

### H-VOL-01 - Time to done at realistic volume

- **Applies when:** a feature ingests or processes a batch: a mailbox, a folder tree, bulk upload.
- **Try:** run a realistic production-sized batch, not a single file; record throughput and the time until the last item is usable; add parallel sessions and check p95.
- **User expects:** completion in a time the user can plan around, with visible progress.
- **Typical failure:** one file works, a thousand take many hours, or the queue starves other users.
- **Technique:** data
- **Source:** mined: legacy UI suite, mined: legacy API suite, interview: 2026-10-23

### H-VOL-02 - Nothing stays "in progress" forever

- **Applies when:** any status such as pending, processing or syncing.
- **Try:** induce a failure in each step; wait beyond the documented time; look at the status, the message and the retry option.
- **User expects:** a final state, success or failure, with a reason and a way to retry.
- **Typical failure:** the status spins indefinitely with no error and no retry.
- **Technique:** state
- **Source:** mined: legacy API suite, interview: 2026-10-23

### H-SRCH-01 - The user can find their own item

- **Applies when:** a new, renamed, moved or imported item should be searchable.
- **Try:** plant a unique made-up word in the name and content; find the item by name, content and filters through every search surface, as owner and as a second user.
- **User expects:** every surface finds it once, within the documented time.
- **Typical failure:** one surface misses it, or a pre-existing match hides the real miss.
- **Technique:** journey
- **Source:** mined: test plans, mined: legacy UI suite, interview: 2026-10-23

### H-FILE-01 - Awkward files and names

- **Applies when:** a user can upload or name a file.
- **Try:** zero-byte, corrupt, wrong extension, mixed scanned and text pages, blank pages, unsupported type, long and special names, emoji, composed and decomposed accents, right-to-left names.
- **User expects:** a clear refusal, or a result that is complete and flagged where content is missing; original preserved.
- **Typical failure:** "ready" with empty content, a blank viewer, or a valid file refused.
- **Technique:** data
- **Source:** mined: legacy API suite, mined: legacy UI suite, mined: test plans, interview: 2026-10-23

### H-PAGE-01 - Paging and result-count edges

- **Applies when:** a list or search returns pages or a capped number of results.
- **Try:** counts of 0, 1, cap-1, cap, cap+1; limit 0, non-numeric, out-of-range page, a bad cursor; walk all pages while data changes.
- **User expects:** no item skipped or repeated across pages; a known item is never cut off by a cap without notice.
- **Typical failure:** items lost at page seams, duplicates, or a hard error on an out-of-range page.
- **Technique:** boundary
- **Source:** mined: legacy API suite, mined: test plans
