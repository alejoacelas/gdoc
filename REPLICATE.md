# Suggested replacement styles

The user wanted suggested replacements to preserve the target's direct text style while allowing explicit replacement Markdown to override it.

- Added seven failing tests for exact suggestion batches and CLI style context, then passed the searched body through to the replacement builder and applied a named-field baseline over only the inserted UTF-16 range.
- All 1,570 unit tests and the no-stubs check pass. Full Ruff checking reports the same 196 findings as the starting revision; this change adds none, and the API module and suggestion test file pass Ruff.
- In one synthetic throwaway document, the accepted projection had an empty direct replacement style, the rejected projection retained the original synthetic text and expected styles, adjacent styles matched across projections, and one review object remained. The document was trashed.
- The pre-write snapshot failed because the rejected projection enum was invalid. Later inspection used `PREVIEW_WITHOUT_SUGGESTIONS`; byte-identical comparison against a saved original snapshot remains unverified. Mixed-style replacement semantics remain outside this change.

Agent session 01a070b6-12ea-7012-bc49-6936ce98c93e · Commits 45d557e, 26a00d2
