# Docs read retries

The user wanted transient Docs read failures retried without retrying mutations.

- Added failing tests for exact read parameters, transport recovery and exhaustion,
  post-write reads, and exact non-retried edit and suggestion request bodies.
- Enabled two generated-client retries on every Docs document GET and reused the
  read wrappers after writes; exhausted reads retain the existing error behavior.
- All 1,572 tests and the no-stubs gate pass. Ruff still reports the same 196
  violations as base commit `dbfa4c3`, with no new violations; repository-wide lint
  cleanup remains outside this change.
- The live edit read path recovered after one injected disconnect and two transport
  attempts on one synthetic document. No edit was issued; the document was trashed.
- Committed locally without pushing or opening a pull request.

Agent session 01a070b6-163b-7f01-b21a-99985daa2388 · Commits b69bd3a, 5504542
