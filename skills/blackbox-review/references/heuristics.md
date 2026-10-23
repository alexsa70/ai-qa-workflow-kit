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
