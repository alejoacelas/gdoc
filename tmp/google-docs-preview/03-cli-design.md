# Add the remaining preview features to `gdoc`

Ship suggestion authoring first. It is the user-visible gap, and the current `edit`
pipeline already solves matching, tabs, UTF-16 indexes, Markdown parsing, conflict
detection, and output modes. Add native thread management in a second PR rather than
mixing two API models into one review.

## Design rules already present in `gdoc`

The proposed surface follows these existing choices:

- Commands are flat and task-named: `edit`, `comment`, `reply`, `resolve`, not a deep
  resource hierarchy.
- Document arguments accept URLs or IDs through `_resolve_doc_id`.
- `terse`, `plain`, and `json` output are stable interfaces; errors go to stderr.
- API modules are thin boundaries that translate `HttpError`; CLI handlers own
  validation, awareness, and presentation.
- A read precedes range writes, indexes use UTF-16 code units, and
  `requiredRevisionId` prevents stale-coordinate writes.
- Preview absence is an expected capability result, not an authentication failure.
- Destructive operations require explicit confirmation or `--force`.
- Multi-account service caches key on the resolved account and token-file identity.

Those rules argue for a sibling `suggest` command rather than making `edit` silently
change semantics based on account or document permissions.

## PR 1: create suggested edits

### CLI

```bash
gdoc suggest DOC OLD NEW
gdoc suggest DOC OLD NEW --all
gdoc suggest DOC OLD NEW --tab "Draft"
gdoc suggest DOC --old-file before.md --new-file after.md
gdoc suggest DOC OLD '**formatted replacement**' --json
```

`suggest` should initially accept the text-oriented `edit` flags:

- `--all`
- `--case-sensitive`
- `--normalize`
- `--old-file` and `--new-file`
- stdin `-`
- `--tab`
- `--quiet`

Support plain text and inline emphasis, strike, and links first. Do not support
`--cell` or structural Markdown (headings, lists, horizontal rules, or tables) in the
first PR. `replace_formatted` handles tables and some heading cleanup through later
read/write batches; suggest mode changes the read-back structure and every later batch
would also have to remain in suggest mode. Fail before the API call with a specific
usage error. Add each structural form only after a live fixture proves its API shape.

Fetch the document with `SUGGESTIONS_INLINE` before matching. If any chosen range
intersects an existing suggested insertion, deletion, or style map, fail with a
specific overlap error in v1. Google may merge a new change into the author's existing
suggestion; that can be supported later behind an explicit option after its behavior
is tested. The default must not modify an existing review thread accidentally.

Keep `edit --suggest` as a compatibility alias only if maintainers ask for it. A verb
is clearer in agent traces:

```text
gdoc edit     # committed mutation
gdoc suggest  # reviewable mutation
```

### Internal shape

Extract the shared front half of `cmd_edit` instead of copying it. One workable split:

```python
def _prepare_text_replacement(args) -> ReplacementPlan:
    # resolve files/stdin, pre-flight, tab, revision, matches, parsed markdown

def cmd_edit(args):
    return _apply_replacement(args, write_mode="EDIT")

def cmd_suggest(args):
    return _apply_replacement(args, write_mode="SUGGEST")
```

Do not route suggest mode through `replace_formatted`'s cleanup and table phases.
Extract its request builder, then execute the supported requests once through a small
`apply_replacement_requests` helper. The suggest body is:

```python
body = {
    "requests": all_requests,
    "writeControl": {
        "requiredRevisionId": revision_id,
        "writeMode": write_mode,
    },
}
```

Never send an empty `requiredRevisionId`. Google documents `revisionId` as available
only to users with edit access, while a commenter can suggest in the Docs UI. For the
first PR, require a non-empty revision ID and report that API suggestion writes need
edit access. Before merge, add a commenter-role live fixture: if Google accepts
`writeMode: SUGGEST` without exposing a revision ID, decide explicitly whether to
support an unlocked request. The safer default is to refuse it; a collaborator can
change range coordinates between the read and write.

Return a result object rather than only the replacement count:

```python
@dataclass
class ReplacementResult:
    occurrences: int
    created_suggestion_ids: list[str]
    updated_suggestion_ids: list[str]
    comment_update_state: str
```

Flatten and deduplicate both `createdSuggestionIds` and
`updatedSummarySuggestionIds`. Google can merge a new edit into an existing open
suggestion by the same author, so a correct request need not create a new ID. For
suggest mode, require all of the following:

- HTTP success;
- `commentUpdateState == "ALL_SAVED"`;
- at least one created or updated suggestion ID for a non-empty request; and
- a follow-up `documents.get` with `SUGGESTIONS_INLINE` and included suggestion
  threads that contains every affected ID.

If the server rejects or ignores `writeMode`, fail loudly. Never fall back to `edit`.
The response should make the review object explicit:

```text
OK suggested 1 occurrence (#suggest.abcd)
```

```json
{
  "ok": true,
  "suggested": 1,
  "suggestionIds": ["suggest.abcd"],
  "createdSuggestionIds": ["suggest.abcd"],
  "updatedSuggestionIds": []
}
```

State tracking should record the post-command Drive version but must not advance the
last-read baseline. Like `edit`, this is a partial write; the rest of the document may
contain unseen changes.

### Failure taxonomy

Add a preview error path that preserves the reason:

- unknown `writeMode`, `suggestionResponses`, or request field: project lacks preview;
- HTTP 403: distinguish document permission from preview access where the message
  permits, otherwise report both possibilities;
- `ALL_FAILED_UNKNOWN_REASON`: the document model may have changed; read back and
  report whether a direct mutation occurred;
- no created or updated suggestion IDs: refuse to report success and verify the base
  content;
- revision mismatch: tell the caller to reread and retry, never replay automatically
  against new indexes.

`insertComment` currently converts several failures into a transparent Drive fallback.
That policy is correct for comments but wrong for suggestions: a fallback direct edit
would violate the command's contract.

### Tests

Add focused tests before the live smoke test:

- parser parity between `edit` and `suggest`;
- exact `writeControl` with both `requiredRevisionId` and `writeMode`;
- one, multiple, and duplicate IDs across created and updated responses;
- a request merged into an existing suggestion;
- `commentUpdateState` partial failure;
- preview-unavailable 400 variants and 403;
- a 200 response with no suggestion IDs;
- read-back missing an ID;
- multi-tab `tabId` propagation and UTF-16 ranges;
- match rejection when any range overlaps an existing content or style suggestion;
- editor and commenter permissions, including a missing `revisionId` that never sends
  `requiredRevisionId: ""`;
- inline Markdown style requests stay inside the same suggest batch;
- headings, lists, horizontal rules, tables, and `--cell` fail before a write;
- terse, plain, and JSON output;
- state update does not advance `last_read_version`.

Run:

```bash
uv run pytest tests/test_suggest.py tests/test_edit.py tests/test_api_docs.py -v
uv run pytest tests/ -v
uv run ruff check gdoc/ tests/
bash scripts/check-no-stubs.sh
```

Live-test only with registered project `122477011422` and a scratch document. Confirm
in the API and Docs UI that the base text remains pending, the suggestion has an
accept/reject control, its author is correct, and Markdown styles are suggested rather
than directly applied.

## PR 2: list and decide suggestion threads

### CLI

```bash
gdoc suggestions DOC
gdoc suggestion-info DOC SUGGESTION_ID
gdoc accept-suggestion DOC SUGGESTION_ID
gdoc reject-suggestion DOC SUGGESTION_ID
gdoc delete-suggestion DOC SUGGESTION_ID [--force]
```

Use explicit verbs to match `comment-info`, `resolve`, `reopen`, and
`delete-comment`. `delete-suggestion` is destructive and authorship-limited, so reuse
`confirm_destructive`. Accept and reject change document content but are review
decisions, not permanent deletion; report the affected ID and status without a prompt.

Add `get_document_threads` in `gdoc/api/docs.py`:

```python
documents.get(
    documentId=doc_id,
    includeTabsContent=True,
    suggestionsViewMode="SUGGESTIONS_INLINE",
    commentsViewMode="COMMENTS_VIEW_MODE_INCLUDED",
)
```

Return the native `suggestions[]` model without coercing it into Drive comments.
`SuggestionThread` supplies ID, status, author, timestamps, summary/head-post text, and
replies; it does not directly supply affected ranges. Build ranges separately by
walking every tab's inline content and collecting spans and style maps keyed by
suggestion ID. Keep that derived location map separate from the raw thread in JSON
until the preview schema stabilizes.

Decision wrappers should each send one request with `requiredRevisionId`, inspect the
corresponding `suggestionResponses`, then verify that the thread moved to the requested
state. Do not accept a list of IDs in the first PR; one ID per command keeps failures
atomic and auditable.

## PR 3: complete native comment threads

Anchored comment creation already works. Add only preview behavior that the Drive API
cannot express:

```bash
gdoc comment DOC TEXT --quote TEXT --assign EMAIL
gdoc reply DOC THREAD_ID TEXT --suggestion
gdoc reply DOC COMMENT_ID TEXT --reassign EMAIL
gdoc edit-comment DOC COMMENT_ID POST_ID TEXT
gdoc edit-suggestion-reply DOC SUGGESTION_ID POST_ID TEXT
gdoc delete-reply DOC COMMENT_ID POST_ID [--force]
gdoc delete-suggestion-reply DOC SUGGESTION_ID POST_ID [--force]
```

The separate `--suggestion` flag avoids guessing the ID namespace and keeps the current
`reply DOC COMMENT_ID TEXT` contract intact. If native IDs prove self-identifying in
live responses, this can later become automatic. `comment --assign` creates an assigned
thread through `insertComment.assigneeEmailAddress`; `reply --reassign` is only for a
thread that already has an assignee, because Google's `Post.assigneeEmail` rejects an
unassigned parent. Read the native thread and fail before writing when that precondition
is absent.

Keep Drive as the default read and mutation path for ordinary comments until the
native endpoint has equivalent pagination, tombstone, and change-detection behavior.
Use native Docs threads when a command needs assignment, suggestion replies, post
editing, or reply deletion. A wholesale migration would risk the awareness system,
which currently depends on Drive `startModifiedTime`, reply actions, and resolved
state.

Native comment reads can later improve `cat --comments`: join `CommentAnchor.ranges`
to each thread by `anchorId` instead of matching `quotedFileContent` back to exported
Markdown. That should be a separate change because Docs indices do not map directly to
Markdown line offsets, especially across tables, tabs, and formatting markers.

## Pull-request sequence

1. Open an issue that links Google's 7 July release and this capability matrix.
2. PR `suggest`: text replacements only, with hard failure on missing preview.
3. PR suggestion listing and accept/reject/delete.
4. PR native comment assignment and post operations.
5. Consider native anchor reads and awareness integration after the write surface is
   stable.

For each PR:

- branch from the current `origin/main`;
- keep preview JSON in `gdoc/api/docs.py` and CLI behavior in `gdoc/cli.py`;
- update README, CHANGELOG, `pyproject.toml`, `gdoc/__init__.py`, and `uv.lock` only when
  the maintainer's release convention requires it;
- include mock-schema tests plus one registered and one unregistered live result;
- state that the unregistered project is `856825977485` and that no suggest-mode write
  was attempted there;
- run the full test, lint, and stub gates; and
- request review from Luca and the maintainers who reviewed anchored-comment PR
  [#40](https://github.com/LucaDeLeo/gdoc/pull/40).

See [the API inventory](01-preview-api.md) and
[the access experiment](02-access-tests.md).
