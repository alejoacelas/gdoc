# Google Docs comments and suggestions preview

Google added native comment and suggestion writes to the Docs API on 7 July 2026.
The feature set is still in the
[Google Workspace Developer Preview Program](https://developers.google.com/workspace/preview).

This audit reflects the public API and `gdoc` `main` at commit `31b4309`
(`0.20.1`) on 25 August 2026.

## What Google added

The preview extends `documents.get` and `documents.batchUpdate`; it is not a new
service or OAuth scope. The existing `documents`, `drive`, or `drive.file` scopes
authorize `batchUpdate`.

| Capability | API shape | Important constraint |
| --- | --- | --- |
| Read native comment and suggestion threads | `documents.get?commentsViewMode=COMMENTS_VIEW_MODE_INCLUDED` returns `comments[]`, `suggestions[]`, and comment anchors | Preview-only. `suggestionsViewMode=SUGGESTIONS_INLINE` is the only read mode whose indexes are suitable for later writes. |
| Add an anchored or assigned comment | `insertComment {content, range, assigneeEmailAddress?}` | Comment text is plain text and limited to 2,048 UTF-8 code units. |
| Reply to a comment or suggestion | `addCommentReply {commentId|suggestionId, post}` | `post` can contain text, resolve/reopen action, or reassignment. |
| Edit a comment or reply | `updateCommentPost {commentId|suggestionId, postId, content}` | Only the author can edit it; a suggestion thread's generated head post cannot be edited. |
| Delete a comment thread | `deleteComment {commentId}` | Only its head-post author can delete it. |
| Delete a reply | `deleteCommentReply {commentId|suggestionId, postId}` | Only its author can delete it; action or assignment replies cannot be deleted. |
| Make edits as suggestions | Set `writeControl.writeMode` to `SUGGEST` on an ordinary `batchUpdate` | Every compatible request in that batch becomes a suggestion. Some tab, named-range, header/footer, table-column, and document-style requests are unsupported. |
| Accept, reject, or delete a suggestion | `acceptSuggestion`, `rejectSuggestion`, or `deleteSuggestion` with its `suggestionId` | Accept requires edit access. Reject also permits the suggestion author. Delete requires authorship. |
| Identify affected suggestions | Read `suggestionResponses[]` from `batchUpdate` | The array maps one-to-one to requests and reports created, updated, deleted, accepted, and rejected IDs. |
| Detect partial thread-save failure | Read `commentUpdateState` from `batchUpdate` | A text edit can commit while its comment or suggestion thread fails to save. A batch expected to save a comment or suggestion requires `ALL_SAVED`; `NO_UPDATES_REQUESTED` is normal for an ordinary edit batch. |

Google's complete announcement and request definitions are in the
[release notes](https://developers.google.com/workspace/docs/release-notes),
[comments and suggestions guide](https://developers.google.com/workspace/docs/api/how-tos/suggestions),
[`Request` reference](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/request),
and [`batchUpdate` reference](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/batchUpdate).

## What was already public

Do not count these as new preview functionality:

- `suggestionsViewMode` could already render existing suggestions inline, accepted,
  or rejected.
- Suggested insertions, deletions, and style changes already appeared in the document
  structure as `suggestedInsertionIds`, `suggestedDeletionIds`, and suggestion-state
  fields.
- The Drive API already listed, created, replied to, resolved, reopened, and deleted
  file comments. Its `quotedFileContent` was metadata, not a native highlighted anchor.

The preview matters because it adds native Docs threads, real anchors, suggestion
creation, and suggestion decisions.

## Current `gdoc` coverage

| Preview capability | `gdoc` status | Evidence |
| --- | --- | --- |
| Create a native anchored comment | **Implemented** | `gdoc comment DOC TEXT --quote TEXT` searches every tab, sends `insertComment`, pins the range to `requiredRevisionId`, checks `commentUpdateState`, and reports `anchored: true`. |
| Work without preview access | **Implemented** | The same command falls back to a Drive comment with quoted metadata and reports `anchored: false`. |
| Read suggestion-aware document structure | **Partial** | `gdoc structure --suggestions-view-mode ...` exposes raw suggested content and IDs, but there is no review-oriented suggestion-thread command. |
| Read native Docs comment/suggestion threads and anchors | **Missing** | `comments`, `comment-info`, awareness checks, and `cat --comments` use Drive v3. `documents.get` never requests `commentsViewMode`. |
| Create suggested edits | **Missing** | `edit` builds the right `batchUpdate` requests but never sets `writeControl.writeMode: SUGGEST`. |
| List suggestion threads | **Missing** | Raw structure may contain inline suggestion IDs, but `gdoc` does not expose `Document.suggestions[]` or thread posts. |
| Accept, reject, or delete a suggestion | **Missing** | No API wrappers or commands exist. |
| Reply to a suggestion thread | **Missing** | `reply` uses Drive `replies.create`, which only addresses Drive comment threads. |
| Assign/reassign comments | **Missing** | `comment` has no assignee option and Drive replies do not expose the new Docs-native assignment shape. |
| Edit a comment post | **Missing** | There is no command corresponding to `updateCommentPost`. |
| Delete an individual reply | **Missing** | `delete-comment` removes a whole Drive thread; no reply deletion command exists. |
| Native comment deletion | **Functionally covered** | `delete-comment` uses Drive v3. The preview request is unnecessary unless Docs-only post IDs or suggestion threads require it. |
| Resolve/reopen an ordinary comment | **Functionally covered** | Drive action replies already implement both. Native Docs replies are needed for suggestion threads and assignment. |

The important gap is larger than “suggest mode plus anchored comments.” Anchored comment
creation has shipped, while suggestion authoring and the native thread model have not.

## Preview hazards to preserve in the implementation

- A non-enrolled project can reject a preview field as unknown. Earlier builds also
  observed `No request set` after Google stripped an unrecognised request union member.
- `writeMode: SUGGEST` was previously observed being ignored by an unenrolled project,
  producing a direct edit. Never probe suggest mode on a document whose base content
  matters.
- A successful HTTP response is insufficient. Check `commentUpdateState`,
  `suggestionResponses`, and a follow-up `documents.get` read.
- Indices depend on the suggestion view. Read with `SUGGESTIONS_INLINE` immediately
  before any range-based update and retain `requiredRevisionId`.
- Preview schemas may change. Keep all preview request/response handling behind a
  small API boundary and test the raw JSON sent to Google.

See [the access experiment](02-access-tests.md) for the live project gate and
[the CLI design](03-cli-design.md) for the proposed implementation.
