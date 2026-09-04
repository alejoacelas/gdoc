# gdoc test suite

What every test group in this repo protects, in two suites: the offline pytest suite under
`tests/`, and the live fidelity suite under `fidelity-tests/` that runs agents against real
Google Docs. Written 2026-09-04 from the `fidelity-tests` branch. Class-level lines below
describe what a group guarantees, not how it is written; open the file when you need the how.

## At a glance

| | pytest (`tests/`) | fidelity (`fidelity-tests/`) |
|---|---|---|
| What it exercises | every CLI command, API wrapper and helper, with Google mocked | a fresh agent holding only `gdoc`, editing a copy of a hand-built messy doc |
| Size | 55 files, 334 classes, 1563 tests | 5 built fixtures, 47 tasks, 98 judged runs |
| Runtime | 31 s, no network | one run is minutes of agent time plus a browser for screenshots |
| Passes today | 1563/1563 | agent track: completion 46/92, safety 57/92 (see below) |
| Run it | `uv run pytest tests/ -v` | `fidelity-tests/bin/gdt …` from the `gdoc-fidelity-test` skill |

There is no CI configuration in the repo. The only automated gate besides pytest is
`scripts/check-no-stubs.sh`, which fails if any `return 4  # STUB` line remains under `gdoc/`.

The two suites do not overlap. Pytest asserts what request gdoc *sends* to Google and how it
handles what comes back; it cannot see what Docs *does* with that request. Every COLLATERAL
verdict in the fidelity suite is Docs behaviour (a one-word `edit` rewriting a whole
paragraph's styles) that no mock models, which is why the pytest suite is green while the
fidelity safety rate sits near 60%.

## How the pytest suite is built

- **Mocking boundary.** Command tests (`cmd_*` handlers in `gdoc/cli.py`) patch the
  functions in `gdoc/api/*` plus `pre_flight`, `load_state` and `save_state`. API-layer tests
  patch one level lower, at `get_docs_service` / `get_drive_service`, and inspect the exact
  `batchUpdate` or `files().*` call. Nothing in `tests/` touches the network.
- **conftest.py** has two fixtures: an autouse one that deletes the five `GDOC_*` auth
  environment variables so a developer's credentials never leak into a test, and `doc_mime`,
  which pins Drive mime detection to a Google Doc so spreadsheet routing stays on the Docs path
  when `pre_flight` is mocked away.
- **Recurring class shapes.** Most command files repeat the same six groups, so their
  one-liners below are short: `Terse` / `Verbose` / `Json` / `Plain` (the four output modes,
  mutually exclusive), `Awareness` (the command calls `pre_flight`, honours `--quiet`, and
  updates per-doc state afterwards), `Errors` (bad doc reference exits 3, `GdocError` exits
  1, `AuthError` exits 2), and for writing commands `Conflict` (version tracking blocks a
  stale write unless `--force`).
- **Exit codes** are the suite's main contract: 0 success, 1 API or unexpected error, 2 auth,
  3 usage or validation. `test_cli.py` also pins that no code-4 stub paths remain.

Layer map, in the order the catalogue below follows:

| Layer | Files |
|---|---|
| CLI commands | `test_cat*`, `test_cli`, `test_comments_cmd`, `test_anchored_comment`, `test_diff`, `test_diff_rev_cmd`, `test_drive_mgmt`, `test_edit`, `test_edit_cell`, `test_export`, `test_file_mgmt`, `test_find`, `test_image_edit`, `test_images`, `test_info`, `test_insert`, `test_ls`, `test_new_file`, `test_page_mode`, `test_pull`, `test_push`, `test_revisions_cmd`, `test_sheets_cmd`, `test_structure`, `test_suggest`, `test_table_insert`, `test_tabs_cmd`, `test_toc`, `test_write` |
| API wrappers and auth | `test_api_docs`, `test_api_drive`, `test_api_revisions`, `test_comments_api`, `test_docs_batch`, `test_sheets_api`, `test_tabs_api`, `test_account_context`, `test_auth` |
| Awareness and state | `test_state`, `test_notify`, `test_pull_hook`, `test_sync_hook` |
| Parsing, formatting, diffing | `test_format`, `test_annotate`, `test_mdparse`, `test_mdimport`, `test_frontmatter`, `test_diffrender`, `test_revdiff`, `test_util` |
| MCP server | `test_mcp` |
| Self-update | `test_update`, `test_update_version` |

## Catalogue of pytest groups

Counts in parentheses are test functions in the class; a parametrized function counts once (1523 functions collect as 1563 tests).

### CLI commands

#### `tests/test_cat.py` — `gdoc/cli.py` (`cmd_cat`, `_truncate_bytes`), `gdoc/api/drive.py` (`export_doc`)
Mocking: Patches Drive export, comment listing, and awareness boundaries; `_make_args` builds namespaces and an autouse `doc_mime` fixture keeps tests on Docs.
- **TestCatMarkdown** (2) — `cat` exports Markdown by default, prints it unchanged, and resolves full Google Docs URLs to document IDs.
- **TestCatPlain** (1) — `cat --plain` exports `text/plain` and prints the returned text unchanged.
- **TestCatJson** (1) — `cat --json` returns the exported content in the stable `{"ok": true, "content": ...}` envelope.
- **TestCatComments** (6) — `cat --comments` fetches anchored comment data, optionally includes resolved threads, annotates output, supports JSON, succeeds, and updates awareness state.
- **TestCatErrors** (3) — `cat` rejects empty or malformed document IDs with exit code 3 and propagates API-level document errors.
- **TestCatPlainCommentsConflict** (1) — `cat --plain --comments` is rejected as mutually exclusive.
- **TestCatAwareness** (6) — `cat` performs pre-flight before export, honors `--quiet`, updates state only after success, and applies the same lifecycle with comments.
- **TestTruncateBytes** (8) — Byte truncation treats nonpositive limits as unlimited and never returns partial UTF-8 characters.
- **TestCatMaxBytes** (4) — `cat --max-bytes` bounds text and JSON content by UTF-8 bytes while zero or oversized limits preserve content.
- **TestCatNoImages** (5) — `cat --no-images` removes Markdown images before annotation and truncation, works in JSON, and leaves image-free content unchanged.

#### `tests/test_cat_tabs.py` — `gdoc/cli.py` (`cmd_cat` tab branches)
Mocking: An autouse `doc_mime` fixture keeps Docs routing active; Docs tab/text APIs, pre-flight, state, and a Drive-export sentinel are patched.
- **TestCatTab** (9) — `gdoc cat --tab` prefers case-insensitive title over ID, uses Docs tab text, emits JSON, and selects Markdown unless `--plain`.
- **TestCatAllTabs** (3) — `--all-tabs` concatenates labeled tab sections, supports JSON, and emits nothing for an empty tab list.
- **TestCatTabMutualExclusivity** (2) — `--tab` and `--all-tabs` each reject combination with `--comments`.
- **TestCatTabAwareness** (2) — Single-tab and all-tab reads perform pre-flight and update successful `cat` state.

#### `tests/test_cat_revision.py` — `gdoc/cli.py` (`cmd_cat`, `cmd_pull`), `gdoc/api/revisions.py`
Mocking: Patches pre-flight, revision listing/export, file metadata, and state updates; argument helpers model `cat` and `pull`, with Docs MIME pinned by fixture.
- **TestCatRevision** (7) — `cat --revision` resolves selectors, chooses Markdown or plain export, identifies JSON revisions, preserves baselines, and rejects incompatible or unknown selections.
- **TestPullRevision** (4) — `pull --revision` writes non-pushable source frontmatter, reports revision metadata, preserves baselines, while ordinary pull keeps live `gdoc` frontmatter.

#### `tests/test_cli.py` — `gdoc/cli.py` (argument parser, `main`)
Mocking: No API boundary is patched; `run_gdoc` invokes `python -m gdoc` in a subprocess against the repository.
- **TestExitCode3OnUsageErrors** (3) — Missing commands, unknown flags, and absent required arguments exit 3, not argparse's default 2.
- **TestExitCode4OnStubs** (5) — Implemented `edit`, `write`, `new`, `cp`, and `share` commands never return the former stub exit code 4.
- **TestMutuallyExclusiveFlags** (8) — `--json` and `--verbose` work before or after subcommands but combinations consistently fail as usage errors.
- **TestHelpText** (3) — Top-level help lists core commands, auth help documents `--no-browser`, and `--version` matches both package and project metadata.
- **TestPlainFlag** (4) — `--plain` works before or after subcommands and conflicts with both `--json` and `--verbose` using exit 3.
- **TestAllowCommands** (4) — `--allow-commands` and `GDOC_ALLOW_COMMANDS` block unlisted commands with exit 3 while listed or empty allowlists do not.
- **TestCommentInfoSubcommand** (2) — `comment-info --help` documents `comment_id`, while omitting its required arguments exits 3.
- **TestResolveMessageFlag** (1) — `resolve --help` exposes both `--message` and `-m`.
- **TestDeleteCommentForceFlag** (1) — `delete-comment --help` exposes `--force`.
- **TestErrorFormat** (2) — Runtime and usage failures write stderr messages prefixed with `ERR: `.
Notes: `TestExitCode4OnStubs` retains its historical name but now protects against regression to stub behavior.

#### `tests/test_comments_cmd.py` — `gdoc/cli.py` (comment CRUD handlers), `gdoc/api/comments.py`
Mocking: Tests patch comment and Drive API wrappers plus pre-flight/state hooks, with shared argument and Drive-comment dictionary builders.
- **TestCmdComment** (5) — comment creation formats terse and JSON success, propagates API/auth failures, and records the new comment ID and Drive version.
- **TestCmdReply** (3) — replies expose comment and reply IDs in terse/JSON output and add the parent comment ID to tracked state.
- **TestCmdResolve** (3) — resolve creates an action reply, emits resolved output, and tracks the comment as both known and resolved at the returned Drive version.
- **TestCmdReopen** (3) — reopen creates an action reply, emits reopened output, and removes the comment from tracked resolved IDs.
- **TestCmdComments** (14) — comments defaults to open threads, `--all` includes resolved threads, and terse/plain/JSON output preserves authors, replies, anchors, and empty results.
- **TestCmdDeleteComment** (8) — deletion requires confirmation or `--force`, formats success, removes tracked IDs, propagates API errors, and refuses unattended deletion without force.
- **TestCmdResolveMessage** (3) — resolve sends `--message` as reply content, otherwise sends empty content, and `--plain` reports ID and resolved status.
- **TestCmdCommentInfo** (5) — comment-info renders summary, full timestamps and replies, JSON, and plain fields while propagating not-found errors.
- **TestCommentCommandsPlainOutput** (5) — `--plain` gives stable tab-separated records for listing, creating, replying, and reopening, with no output for an empty list.

#### `tests/test_anchored_comment.py` — `gdoc/api/docs.py` (`insert_comment`, `find_text_in_document`), `gdoc/cli.py` (`_try_anchored_comment`, `cmd_comment`)
Mocking: Patches Docs batch updates, document retrieval, Drive comment creation, versions, and awareness; helpers build HTTP errors, services, tabs, and arguments.
- **TestInsertComment** (11) — Anchored insertion sends range, tab, and revision controls, returns the thread ID, translates auth/not-found errors, and distinguishes preview unavailability from invalid requests.
- **TestTryAnchoredComment** (5) — Anchoring finds the first quote across tabs, tolerates smart-quote differences, and returns empty when unmatched or Developer Preview insertion is unavailable.
- **TestUtf16Offsets** (2) — Text matches convert Python character positions to Docs API UTF-16 start and end indexes around emoji.
- **TestCmdCommentAnchored** (6) — `comment --quote` prefers true anchored insertion, falls back to Drive quoted content, reports anchoring in outputs, and tracks the created comment ID.
Notes: Fallback tests preserve `--quote` behavior for projects outside the Docs API Developer Preview and users with comment-only access.

#### `tests/test_diff.py` — `gdoc/cli.py` (`cmd_diff`)
Mocking: Patches pre-flight, Drive export/service/version, and state updates; helpers construct parsed arguments and version responses.
- **TestDiffIdentical** (2) — Identical local and remote content exits 0 and reports an empty diff in terse and JSON modes.
- **TestDiffDifferent** (2) — Differences exit 1 and expose a standard remote-to-local unified diff in terminal and JSON output.
- **TestDiffPlainText** (2) — `--plain` exports `text/plain`; the default comparison exports `text/markdown`.
- **TestDiffErrors** (2) — Missing local files and invalid document IDs fail with usage exit 3.
- **TestDiffAwareness** (3) — Diff forwards `--quiet` to pre-flight and records the fetched Drive version under command `diff`.

#### `tests/test_diff_rev_cmd.py` — `gdoc/cli.py` (`cmd_diff`, `_diff_revisions`)
Mocking: `_patches` replaces pre-flight, revision listing/export, file metadata, and state updates; comments are patched only for comment-inclusive output.
- **TestRevSelection** (4) — `--rev` and `--since` choose the intended retained revisions; changed diffs return 1 and identical revisions return 0.
- **TestRevOutput** (7) — Revision diffs support plain markers, ANSI color, JSON models, comment attachment, HTML files, machine confirmations, and exit-code-3 write failures.
- **TestRevValidation** (11) — Conflicting inputs and incompatible format/output/comment combinations fail with exit code 3, with invalid selectors rejected before API calls.

#### `tests/test_drive_mgmt.py` — `gdoc/api/drive.py`, `gdoc/cli.py` (Drive-management handlers)
Mocking: Patches `get_drive_service` for API wrappers and wrapper functions for CLI handlers; `_http_error` and `_make_args` build shared failures and namespaces.
- **TestCreateFolderAPI** (2) — Folder creation sends the Google folder MIME type and includes a parent only when supplied.
- **TestMoveFileAPI** (4) — Moving replaces old parents, avoids redundant updates, retains an existing destination parent, returns numeric versions, and translates 404 failures.
- **TestRenameFileAPI** (1) — Renaming sends only the new name and returns the Drive version as an integer.
- **TestListSharedDrivesAPI** (1) — Shared-drive listing follows `nextPageToken` until every page is collected.
- **TestListFilesCorpora** (3) — `list_files(..., all_drives=True)` requests `corpora=allDrives`, omits it otherwise, and warns when Drive reports an incomplete search.
- **TestCreatePermissionTargets** (3) — Permission creation builds correct domain or anyone bodies, including discoverability, and rejects calls without a target.
- **TestCmdMkdir** (3) — `mkdir` resolves parent folder URLs and returns the created folder in terse or JSON output.
- **TestCmdMv** (3) — `mv` resolves folder URLs, reports new parents, and records the post-move version as a metadata-only write.
- **TestCmdRename** (2) — `rename` reports the new title and records its returned version as a metadata-only write.
- **TestCmdDrives** (4) — `drives` lists IDs and names in terse, plain, or JSON formats and handles an empty account clearly.
- **TestCmdFindRaw** (3) — `find --raw` sends Drive query syntax verbatim across all drives, rejects `--title`, and leaves normal searches on `search_files`.
- **TestCmdShareTargets** (8) — `share` accepts a user email, `--domain` or `--anyone` target, keeps the terse/JSON schemas, and rejects invalid target and discovery combinations with exit 3.

#### `tests/test_edit.py` — `gdoc/cli.py` (`cmd_edit`), `gdoc/api/docs.py` (`find_text_in_document`, `replace_formatted`)
Mocking: Tests patch the Docs and Drive API wrappers plus pre-flight/state hooks, using namespace, document, version, and match-list builders.
- **TestEditBasic** (4) — edit resolves document URLs, honors `--case-sensitive`, replaces one match with formatted text, and reports one successful occurrence.
- **TestEditAll** (2) — `--all` replaces every match, while zero matches raises a usage error with exit code 3.
- **TestEditPrecheck** (3) — edit proceeds for one case-insensitive match but exits 3 before mutation when matches number zero or exceed one without `--all`.
- **TestEditNormalize** (4) — `--normalize` matches smart punctuation; exact misses suggest normalization or identify whitespace differences, all before mutation.
- **TestEditJson** (2) — `--json` returns exactly the success flag and replacement count for single and `--all` edits.
- **TestEditConflict** (2) — edits proceed despite stale-read conflicts, emitting a warning only when the current version differs from the last-read version.
- **TestEditAwareness** (5) — edit runs pre-flight with `--quiet`, records the resulting Drive version after success, and never updates state after failed matching or mutation.
- **TestEditErrors** (4) — invalid IDs exit 3, while document-not-found, permission, and authentication errors retain their API-boundary error types and messages.
- **TestEditFileInput** (7) — `--old-file` and `--new-file` override positionals, trim one trailing newline, support deletion, and reject missing, unreadable, or invalid file combinations.
- **TestEditValidation** (2) — without file flags, both positional `old_text` and `new_text` are mandatory; omissions exit 3.
- **TestEditHelpText** (1) — edit help directs users to `cat --plain` because matching uses raw text while replacement accepts Markdown formatting.
- **TestEditFormatted** (2) — Markdown replacement text and the document's revision ID reach the formatted replacement request unchanged.
- **TestEditPlain** (2) — `--plain` emits tab-separated document ID and updated status for single and `--all` edits.
- **TestEditTab** (4) — `--tab` resolves a tab title, searches only that body, supplies its tab ID, and preserves tab-fetch errors.
- **TestEditStdin** (3) — `-` reads either search or replacement text from stdin, but using it for both arguments exits 3.

#### `tests/test_edit_cell.py` — `gdoc/api/docs.py` (`resolve_cell_range`), `gdoc/cli.py` (`cmd_edit`)
Mocking: Patches pre-flight, document reads, formatted replacement, Drive version, and state update; helpers build table cells, documents, arguments, and versions.
- **TestParseCoord** (2) — Cell coordinates accept whitespace around two integers and reject labels or incomplete coordinate syntax.
- **TestCellTextRange** (4) — Editable cell ranges exclude final paragraph marks, handle empties and multiple paragraphs, and count non-BMP characters in UTF-16 units.
- **TestResolveCellRange** (8) — Cell selection supports labels, coordinates, column/table overrides, normalized typography, empty targets, first-match precedence, and out-of-range misses.
- **TestCmdEditCell** (4) — `edit --cell` replaces the resolved range from one positional value and returns exit 3 for missing cells or replacement text.

#### `tests/test_export.py` — `gdoc/api/drive.py` (`export_doc_bytes`), `gdoc/cli.py` (`cmd_export`)
Mocking: Patches Drive service or byte export plus state updates; helpers construct command arguments and Google API HTTP errors.
- **TestExportDocBytes** (2) — Byte export sends file ID and MIME type unchanged, returns binary data verbatim, and translates Drive 404 responses.
- **TestCmdExport** (13) — `export` validates or infers formats, requires paths for binaries, writes bytes or stdout, formats four output modes, handles writes, and updates state.

#### `tests/test_file_mgmt.py` — `gdoc/cli.py` (`cmd_new`, `cmd_cp`, `cmd_share`), `gdoc/api/drive.py` (`create_doc`, `copy_doc`, `create_permission`)
Mocking: CLI tests patch Drive wrappers and awareness hooks; API tests patch the Drive service, while an autouse fixture disables page-mode application.
- **TestCmdNew** (12) — new resolves optional folder IDs, emits terse/verbose/JSON output, seeds integer-version state, skips pre-flight, and propagates validation, API, and auth errors.
- **TestCmdCp** (12) — cp resolves the source, pre-flights and records it, seeds copy state, preserves title/version, formats output, and propagates validation/API/auth errors.
- **TestCmdShare** (10) — share defaults to reader, supports writer/commenter, pre-flights and records state, formats terse/JSON output, and preserves validation/API/auth errors.
- **TestCreateDocAPI** (6) — create_doc sends Google Docs MIME type and optional parent, normalizes version to integer, and translates 404 and 401 responses.
- **TestCopyDocAPI** (4) — copy_doc sends source file ID and destination title, normalizes version to integer, and translates a 404 to document-not-found.
- **TestCreatePermissionAPI** (6) — `create_permission` sends the user role and email, returns the permission ID, and translates 401, 403 and 404 responses.
- **TestPlainOutput** (3) — `--plain` emits stable tab-separated IDs for new/cp and email plus role for share.

#### `tests/test_find.py` — `gdoc/cli.py` (`cmd_find`)
Mocking: Patches Drive service access and `search_files`; `_make_args` supplies command defaults and `MOCK_FILES` supplies mixed Docs/Sheets results.
- **TestFindBasic** (2) — `find` passes the query to Drive, returns tab-separated matches, and prints `No files.` for empty terse results.
- **TestFindOutputFormat** (3) — Find output is three-column terse, four-column verbose, or a successful JSON envelope with complete file objects.
- **TestFindSpecialChars** (2) — Queries containing apostrophes or backslashes reach the Drive search boundary unchanged.
- **TestFindTitleOnly** (4) — `--title` controls title-only search, while empty verbose and JSON results retain their mode-specific representations.
- **TestFindPlain** (2) — Plain mode emits ID, name, and MIME type as TSV and emits nothing for no matches.

#### `tests/test_image_edit.py` — `gdoc/cli.py` (`cmd_insert_image`, `cmd_replace_image`), `gdoc/api/docs.py` (image wrappers), `gdoc/api/drive.py` (`upload_temp_image`)
Mocking: API tests patch Docs/Drive services; CLI tests patch document, image, version, state, upload, and cleanup wrappers, using tab-document and HTTP-error builders.
- **TestInsertInlineImage** (5) — insertInlineImage sends location, optional tab/revision/point dimensions, returns object ID, and translates stale revisions and missing documents clearly.
- **TestReplaceImage** (2) — replaceImage uses `CENTER_CROP` and includes tab/write-control fields only when supplied.
- **TestFindObjectTab** (4) — object lookup finds inline or positioned images across top-level and nested tabs, returning `None` when absent.
- **TestCmdInsertImage** (19) — insert-image validates location, tabs, dimensions, and local formats; resolves anchors/end indexes; reports JSON; and always cleans temporary uploads.
- **TestUploadTempImageCleanup** (1) — a failed public-read permission deletes the newly uploaded Drive image instead of orphaning it.
- **TestCmdReplaceImage** (6) — replace-image finds the owning tab or legacy body, rejects absent objects, reports JSON, and cleans local-image uploads after success or failure.

#### `tests/test_images.py` — `gdoc/api/docs.py` (`list_inline_objects`, `download_image`), `gdoc/cli.py` (`cmd_images`, `build_parser`)
Mocking: Patches the Docs document boundary, image downloader or `urlopen`, awareness hooks, and defines builders for arguments, documents, objects, and body references.
- **TestListInlineObjectsTabs** (2) — Image discovery traverses every top-level and child tab and labels each object with its owning tab ID.
- **TestListInlineObjects** (7) — Object listing classifies images, drawings, charts, and positioned objects, returns their metadata, preserves document order, and deduplicates repeated references.
- **TestDownloadImage** (1) — `download_image` writes the exact response bytes to the requested destination.
- **TestCmdImages** (5) — `images` reports all objects in terse, verbose, plain, or JSON output and prints a clear empty result.
- **TestCmdImagesFilter** (2) — An image ID limits output to that object; an unknown ID raises a usage error.
- **TestCmdImagesDownload** (4) — `images --download` creates directories, downloads exportable selections as PNG, and warns while skipping drawings without content URIs.
- **TestCmdImagesParser** (4) — The parser accepts `images DOC [IMAGE_ID]`, `--download`, and `--json` with the expected parsed fields.

#### `tests/test_info.py` — `gdoc/cli.py` (`cmd_info`)
Mocking: Drive metadata/export, service acquisition, pre-flight, and state updates are patched; `_make_args` and metadata helpers define common command inputs.
- **TestInfoTerse** (2) — Default `gdoc info` prints title, owner, ten-character modified date, and integer word count, then returns 0.
- **TestInfoVerbose** (2) — `--verbose` includes full timestamps, last editor, MIME type, size, and words, rendering absent size as `N/A`.
- **TestInfoJson** (2) — `--json` emits a successful structured record with full modified timestamp and an integer `words` value.
- **TestInfoOwnerFallback** (2) — Owner display falls back from display name to email, then to `Unknown` when metadata has no owners.
- **TestInfoNonExportable** (2) — Non-Docs files remain inspectable when Markdown export is unsupported, reporting `Words: N/A` or JSON `words: "N/A"`.
- **TestInfoErrors** (5) — Invalid IDs use exit code 3, while metadata, permission, authentication, and generic export failures propagate instead of becoming `N/A`.
- **TestInfoPlain** (1) — `--plain` emits tab-separated `title`, `owner`, `modified`, and `words` fields.
- **TestInfoAwareness** (5) — Info forwards `--quiet`, records the metadata version after success even when quiet, and never updates state after failure.

#### `tests/test_insert.py` — `gdoc/cli.py` (`cmd_insert`)
Mocking: Patches pre-flight, tab insertion, Drive version, and state update; helpers create arguments, insertion results, and conflict-free awareness data.
- **TestInsertBasic** (3) — `insert` reads local Markdown, forwards start/end position, reports terse or JSON tab metadata, and captures the resulting Drive version.
- **TestInsertFrontmatterStrip** (1) — Inserted content excludes local frontmatter and sends only the Markdown body.
- **TestInsertFileErrors** (2) — Missing files and files empty after frontmatter removal fail with usage exit 3.
- **TestInsertConflict** (2) — Remote changes block insertion unless `--force` is supplied.

#### `tests/test_ls.py` — `gdoc/cli.py` (`cmd_ls`)
Mocking: Patches Drive service access and `list_files`; `_make_args` supplies defaults and `MOCK_FILES` provides mixed file types.
- **TestLsTerse** (3) — Default `ls` queries non-trashed root children and emits ID, title, and date, with a human-readable empty result.
- **TestLsTypeFilter** (3) — `--type docs` and `--type sheets` add exact MIME filters; `--type all` adds none.
- **TestLsFolderFilter** (2) — `--folder-id` accepts bare IDs or Drive folder URLs and replaces the default root parent clause.
- **TestLsVerbose** (1) — Verbose listing emits ID, title, full timestamp, and MIME type.
- **TestLsJson** (2) — JSON listing returns a successful envelope containing complete files or an empty list.
- **TestLsPlain** (2) — Plain listing emits ID, title, and MIME type as TSV and emits nothing when empty.

#### `tests/test_new_file.py` — `gdoc/cli.py` (`cmd_new`, `_cmd_new_from_file`, `_insert_images`)
Mocking: An autouse fixture disables page-mode writes; Drive/Docs creation, image, version, and state boundaries are patched around temporary local files.
- **TestNewFromFile** (7) — `gdoc new --file` reads Markdown, honors `--folder`, rejects missing or traversing image paths, formats output, and seeds created-document state.
- **TestNewFromFileWithImages** (4) — Local images use temporary Drive uploads with cleanup, remote URLs insert directly, and state prefers the post-image version with safe fallback.
Notes: Page-mode behavior is deliberately excluded and covered by `tests/test_page_mode.py`.

#### `tests/test_page_mode.py` — `gdoc/api/docs.py` (`set_page_mode`), `gdoc/util.py`, `gdoc/cli.py`
Mocking: Patches Docs and Drive API boundaries, config paths, and page-mode helpers; `_http_error`, `_call_body`, `_new_args`, and `_BLANK_RESULT` supply shared inputs.
- **TestSetPageModeAPI** (4) — Page-mode writes use `updateDocumentStyle.documentFormat.documentMode` with `PAGELESS` or `PAGES` and translate 401 and 404 responses.
- **TestPageModeConfig** (6) — Page-mode configuration persists `pageless` or `paged`, preserves unrelated keys, treats absent or invalid stored values as unset, and rejects invalid writes.
- **TestApplyPageMode** (9) — Explicit flags override configuration; unset preferences do nothing; successful writes return refreshed versions; all post-creation failures remain nonfatal and warn.
- **TestCmdConfig** (5) — `config` reads or sets `page_mode`, emits capturable TSV by default, honors JSON, and reports successful changes on stderr.
- **TestCmdNewAppliesPageMode** (6) — Blank and Markdown-imported `new` documents apply flags or configured defaults, skip unset preferences, and seed state with the post-write version.
- **TestParserWiring** (6) — `new` makes `--pageless` and `--paged` mutually exclusive; `config --page-mode` validates choices and dispatches both set and show forms.

#### `tests/test_pull.py` — `gdoc/cli.py` (`cmd_pull`)
Mocking: Drive export/metadata/service, pre-flight, and state updates are patched; `tmp_path` supplies writable destinations and `_make_args` shared inputs.
- **TestPullBasic** (4) — `gdoc pull` accepts IDs or URLs, exports Markdown, writes `gdoc`/title frontmatter, and confirms the destination path.
- **TestPullOutput** (2) — JSON reports a successful pull and title, while verbose output includes title and document ID.
- **TestPullAwareness** (3) — Pull forwards `--quiet` to pre-flight and records the fetched Drive version as a successful read baseline.
- **TestPullErrors** (2) — Invalid document IDs fail with exit code 3, and unwritable destinations raise `cannot write file`.
- **TestPullPlain** (1) — `--plain` emits the destination as a tab-separated `path` field.

#### `tests/test_push.py` — `gdoc/cli.py` (`cmd_push`), `gdoc/api/drive.py`, `gdoc/api/docs.py` (`count_document_tabs`)
Mocking: Patches Drive writes, exports, versions, awareness state, and tab counts; `_make_args` and frontmatter constants build inputs, with single-tab behavior autoused.
- **TestPushBasic** (4) — `push` reads the frontmatter document reference, strips frontmatter, replaces content, accepts document URLs, and reports success in text or JSON.
- **TestPushConflict** (2) — `push` exits 3 without writing when remote content differs and the read baseline is stale or absent.
- **TestPushInSync** (4) — Matching remote content makes `push` a successful no-op despite version drift; JSON and state show synchronization, while `--force` permits replacement.
- **TestPushQuiet** (3) — `push --quiet` checks stored versus current versions without pre-flight; mismatches block, while `--force` skips every conflict check.
- **TestPushAwareness** (1) — A successful full-document push records the returned version and advances awareness as a full-document write.
- **TestPushErrors** (5) — `push` exits 3 for missing files, absent or invalid `gdoc` frontmatter, revision snapshots, and malformed document IDs.
- **TestPushPlain** (1) — `push --plain` emits tab-separated document ID and updated status fields.
- **TestPushCollapseSafety** (2) — `push` refuses to collapse multi-tab documents without `--force-collapse-tabs`; explicit opt-in bypasses counting and permits the destructive write.

#### `tests/test_revisions_cmd.py` — `gdoc/cli.py` (`cmd_revisions`)
Mocking: Patches pre-flight, revision listing, and state update; `_make_args` supplies defaults and `REVS` provides ordered author, retention, and export metadata.
- **TestRevisionsOutput** (5) — `revisions` renders terse, verbose, plain, and JSON forms, marks pinned revisions, and applies `--limit` to the newest entries.
- **TestRevisionsEmpty** (1) — Empty terse output says `No revisions retained.` and exits successfully.
- **TestRevisionsAwareness** (1) — Revisions forwards `--quiet` to pre-flight and records command `revisions` in document state.

#### `tests/test_sheets_cmd.py` — `gdoc/cli.py` (sheet formatting, `cmd_cat`, `cmd_tabs`, `cmd_cells`), `gdoc/api/sheets.py`
Mocking: Patches Sheets metadata, read, batch-read, and write boundaries plus awareness; an autouse fixture forces spreadsheet MIME detection and a post-write version.
- **TestFormatters** (5) — Sheet helpers quote apostrophes, emit rectangular clean TSV, and format escaped, padded Markdown tables with the first row as headers.
- **TestCatSheet** (11) — Spreadsheet `cat` reads selected sheets or ranges, supports IDs and all tabs, formats Markdown, TSV, or JSON, and rejects unsupported option combinations.
- **TestCatDocRangeRejected** (1) — `cat --range` is rejected for Google Docs because ranges are spreadsheet-only.
- **TestTabsSheet** (3) — Spreadsheet `tabs` lists sheet IDs, titles, and dimensions in terse or JSON output, with a reduced plain format.
- **TestCells** (12) — `cells` accepts one value source, parses row, TSV, or CSV data, supports append and user-entered modes, warns on conflicts, and records versions.

#### `tests/test_structure.py` — `gdoc/api/docs.py` (`get_document_structure`, `resolve_raw_tab`), `gdoc/cli.py` (`cmd_structure`)
Mocking: Patches the Docs service, structure API, state update, and selectively pre-flight; helpers construct arguments, tabs, documents, and HTTP errors.
- **TestGetDocumentStructureAPI** (3) — Structure reads request tab content, forward field masks and suggestion view modes, return raw JSON, and translate 404 responses.
- **TestResolveRawTab** (5) — Tab resolution searches nested tabs, matches titles case-insensitively before IDs, and returns `None` when no tab matches.
- **TestCmdStructure** (9) — `structure` emits compact, indented, or enveloped JSON; narrows by tab; forwards view options; updates state; and rejects sheets or missing tabs.

#### `tests/test_suggest.py` — `gdoc/cli.py` (`cmd_suggest`), `gdoc/api/docs.py` (suggestion helpers), `gdoc/mdparse.py`, `gdoc/mcp.py`
Mocking: Docs and Drive API wrappers, OAuth sessions, state, and pre-flight checks are patched; helpers build HTTP errors, service responses, document structures, matches, and arguments.
- **TestSuggestRequestShape** (19) — suggested replacements use revision-pinned SUGGEST batches, UTF-16 tab ranges, safe match ordering, inline styles, enrollment gating, and stable account identity.
- **TestSuggestResponseIds** (11) — successful writes require saved suggestion IDs verified by SUGGESTIONS_INLINE read-back, with deduplication and actionable errors for partial or unverifiable outcomes.
- **TestSuggestErrors** (15) — API, transport, refresh, enrollment, permission, revision, and unsupported-Markdown failures receive accurate retry guidance, exit classification, and mutation-outcome wording.
- **TestCheckInlineOnly** (3) — suggestion replacements accept plain multi-paragraph and inline Markdown but reject structural formatting with exit code 3 before writing.
- **TestFindSuggestionsInRange** (11) — overlap detection finds text, paragraph, section-break, table-cell, and TOC suggestions only when their half-open ranges intersect the proposed edit.
- **TestPreviewGate** (12) — the preview enrollment probe requires the echoed comments field, fails closed on network errors, and classifies HTTP and credential failures accurately.
- **TestTokenIdentity** (1) — token identity reads client and refresh-token values while treating missing, malformed, or non-object token files as unavailable.
- **TestTableContainerSuggestions** (4) — table-, row-, and cell-level suggestions block edits inside their ranges without contaminating edits in later rows.
- **TestCollectSuggestionIds** (3) — suggestion-ID collection recursively recognizes ID lists and change maps, including positioned-object maps, and handles empty documents.
- **TestSuggestionResult** (1) — `SuggestionResult.suggestion_ids` preserves first-seen order while deduplicating created and updated IDs.
- **TestSuggestParser** (3) — `suggest` mirrors `edit` options except cell mode, parses matching, tab, quiet, and output flags, and rejects `--cell` with exit 3.
- **TestCmdSuggest** (29) — `cmd_suggest` validates inputs and conflicts, targets tabs, preserves saved IDs across post-write failures, formats output, and records partial-write state safely.
- **TestMcpExposure** (1) — MCP marks `suggest` as mutating, hides local file parameters, and supplies command-specific description notes.
Notes: Several classes use parametrization to cover Markdown forms once per test function; counts therefore do not equal the number of executed cases.

#### `tests/test_table_insert.py` — `gdoc/api/docs.py` and `gdoc/cli.py` (`_find_table_cell_indices`, `_insert_table`, `cmd_edit`)
Mocking: Docs service chains and edit preparation/replacement boundaries are patched; `_make_document_with_table` creates indexed table bodies for deterministic placement.
- **TestFindTableCellIndices** (4) — Cell-index discovery returns a correctly shaped, increasing grid for the nearby table and an empty list when none exists.
- **TestInsertTable** (3) — Native insertion creates the table, reads cell positions, populates nonempty cells in a later batch, and skips empty cell text.
- **TestEditTableRestriction** (1) — `gdoc edit --all` rejects a table-bearing replacement when multiple matches exist.
- **TestFindTableCellIndicesBody** (2) — Cell-index discovery accepts an explicit tab body without a document and returns empty when neither source exists.
- **TestInsertTableTabId** (1) — Tab-scoped table insertion includes `tabId` in the Docs API insertion location.

#### `tests/test_tabs_cmd.py` — `gdoc/cli.py` (`cmd_tabs`, `cmd_add_tab`)
Mocking: An autouse `doc_mime` fixture keeps Docs routing active; Docs tab APIs, Drive versions, pre-flight, and state updates are patched.
- **TestTabsTerse** (4) — `gdoc tabs` lists IDs and titles, indents nested tabs, and reports `No tabs.` for an empty document.
- **TestTabsJson** (2) — `--json` exposes tab identity, order, and nesting without leaking document body content.
- **TestTabsVerbose** (1) — `--verbose` appends each tab's index and nesting level.
- **TestTabsPlain** (2) — `--plain` emits tab-separated ID/title rows and stays silent when no tabs exist.
- **TestTabsErrors** (1) — An invalid document identifier fails validation with exit code 3.
- **TestTabsAwareness** (1) — Successful tab listing performs pre-flight and records `command="tabs"` state.
- **TestAddTab** (6) — `gdoc add-tab` returns ID, title, index, and clickable URL across modes, records the post-write version, and propagates API errors.

#### `tests/test_toc.py` — `gdoc/cli.py` and `gdoc/api/docs.py` (`cmd_toc`, `get_document_headings`)
Mocking: Docs tab/heading APIs, service acquisition, pre-flight, and state updates are patched; `_make_args` and `_headings` build shared inputs.
- **TestTocBasic** (3) — `gdoc toc` renders nested Markdown deep links, prints nothing without headings, and `--no-links` removes URLs.
- **TestTocMaxDepth** (1) — `--max-depth N` excludes headings deeper than level N.
- **TestTocOutputModes** (3) — JSON exposes heading records and links, plain mode is tab-separated, and verbose mode appends the heading count.
- **TestTocTab** (4) — `--tab` resolves a tab, extracts headings from its body, and builds links with the exact tab ID before the heading fragment.
- **TestTocAwareness** (2) — TOC runs pre-flight with the requested quiet setting and records successful command state.
- **TestGetDocumentHeadings** (5) — Heading extraction returns nonempty `HEADING_1`–`HEADING_6` paragraphs with IDs, concatenating text runs and ignoring normal, empty, or unlinked headings.

#### `tests/test_write.py` — `gdoc/cli.py` (`cmd_write`), `gdoc/api/drive.py` (`update_doc_content`)
Mocking: CLI boundaries for Drive, Docs, awareness, and state are patched; `_make_args` supplies parser-shaped arguments and an autouse fixture defaults documents to one tab.
- **TestWriteBasic** (4) — write accepts IDs or URLs, uploads the complete file contents, returns success, and emits terse or JSON output with the resulting version.
- **TestWriteFileErrors** (3) — missing or unreadable files fail before upload with usage errors, while an empty file validly replaces the document with empty content.
- **TestWriteConflictNormal** (5) — ordinary writes require a matching prior-read Drive version and otherwise fail with exit 3 and explicit `--force` guidance.
- **TestWriteInSync** (2) — full-document version conflicts become successful no-ops when exported content already matches, but tab writes remain blocked.
- **TestWriteConflictForce** (3) — `--force` permits writes despite version drift or no baseline while still running normal pre-flight awareness unless quiet.
- **TestWriteQuietNoForce** (6) — `--quiet` skips full pre-flight but still requires stored read state and an exact live Drive version match.
- **TestWriteQuietForce** (2) — combining `--quiet --force` bypasses pre-flight, state loading, and version lookup while still uploading content.
- **TestWriteAwareness** (5) — successful writes record the returned version and full-document scope; conflicts and file failures never advance state.
- **TestWriteErrors** (3) — invalid document references produce exit 3, while Drive API and authentication errors retain their original error classifications.
- **TestWritePlain** (1) — `--plain` reports the document ID and updated status as tab-separated fields.
- **TestWriteFrontmatterStrip** (1) — full-document writes remove gdoc YAML frontmatter before uploading the Markdown body.
- **TestWriteCollapseSafety** (3) — full-document writes refuse multi-tab documents unless `--force-collapse-tabs`; single-tab documents pass and explicit opt-in skips counting.
- **TestWriteTabScoped** (4) — `--tab` replaces only the selected tab through Docs API, strips frontmatter, avoids Drive upload, and preserves the whole-document read baseline.

### API wrappers and auth

#### `tests/test_api_docs.py` — `gdoc/api/docs.py` (Docs API wrappers and request builders)
Mocking: `get_docs_service` supplies mocked Docs resources and responses; shared helpers construct `HttpError` instances and capture every `batchUpdate` body.
- **TestTranslateHttpError** (4) — Docs HTTP 401, 403, 404, and server failures become authentication, permission, not-found, and status-bearing API errors respectively.
- **TestReplaceAllText** (9) — `replace_all_text` sends the exact case-sensitivity request, returns changed-occurrence counts including empty responses, and translates Docs API errors.
- **TestGetDocsServiceCaches** (1) — the underlying per-account Docs service factory remains LRU-cached.
- **TestGetDocumentWithTabs** (3) — tab-aware document reads request `includeTabsContent=True`, return the complete response, and translate authentication and not-found failures.
- **TestBuildCleanupRequests** (6) — cleanup transfers an empty heading’s style to the preceding paragraph then deletes it, respecting tab IDs and ignoring non-applicable structures.
- **TestReplaceFormattedCleanupPositions** (5) — formatted replacement cleanup positions account for descending multi-match length drift, same-length edits, tables, and UTF-16 emoji width.
- **TestFindTextBody** (7) — text search returns Docs indices across paragraphs and nested tables, supports quote normalization, and never creates matches spanning table cells.
- **TestDiagnoseNoMatch** (4) — no-match diagnostics recommend `--normalize` for quote variants, identify whitespace differences, and avoid irrelevant advice.
- **TestAddTab** (4) — tab creation sends `addDocumentTab`, returns its properties, translates auth and not-found errors, and rejects malformed success responses.
- **TestCountDocumentTabs** (3) — tab counting includes nested child tabs and requests complete tab content without a fields mask.
- **TestZeroWidthReplace** (1) — zero-width formatted replacements emit a pure `insertText` request because Docs rejects empty delete ranges.
- **TestInsertMarkdownIntoTab** (5) — tab insertion and replacement choose correct body indices, pin the revision, include tab IDs, avoid empty deletes, and reject unknown tabs.

#### `tests/test_write_tab_terminal_bullet.py` — `gdoc/api/docs.py` (`insert_markdown_into_tab`, replace path)
Mocking: Patches `get_document_with_tabs` with a tab body whose terminal empty paragraph carries a bullet, and `get_docs_service` to capture the batch.
- **TestReplaceTabWithBulletedTerminalParagraph** (2) — `write --tab` must clear the bullet on the surviving terminal paragraph before inserting (fails until LucaDeLeo/gdoc#59 is fixed), and must add no such request when the terminal paragraph is plain.

#### `tests/test_api_drive.py` — `gdoc/api/drive.py` (Drive wrappers and error translation)
Mocking: `get_drive_service` or `list_files` is patched with chained `MagicMock` requests; `_make_http_error` constructs status-specific Google API failures.
- **TestTranslateHttpError** (5) — HTTP 401 becomes `AuthError`; 403, 404, and 500 become specific `GdocError` messages, including the non-exportable Docs case.
- **TestEscapeQueryValue** (4) — Drive query literals escape backslashes before single quotes without altering ordinary text.
- **TestExportDoc** (6) — Document export decodes UTF-8 for Markdown or plain text and translates not-found, authentication, permission, and non-exportable failures.
- **TestListFiles** (3) — Drive file listing combines every response page and returns an empty list when no files match.
- **TestSearchFiles** (5) — Search builds escaped, non-trashed Drive queries over title plus full text by default, or title alone with `title_only=True`.
- **TestGetFileInfo** (2) — File metadata is returned unchanged, while Drive 404 responses become `Document not found` errors.
- **TestUpdateDocContent** (5) — Markdown overwrite returns the integer Drive version, requests Google Docs MIME conversion, and translates 401, 403, and 404 failures.

#### `tests/test_api_revisions.py` — `gdoc/api/revisions.py`
Mocking: Patches the authorized revisions session for downloads and the Drive service for listings; `_response` builds HTTP response doubles.
- **TestExportRevision** (6) — Revision export prefers Markdown with timeout, warns on plain-text fallback, and maps 401, 403, and pruned 404 responses correctly.
- **TestListRevisions** (1) — Revision listings are sorted oldest-first by `modifiedTime`, independent of Drive's response order.

#### `tests/test_comments_api.py` — `gdoc/api/comments.py` (Drive comments wrappers)
Mocking: Every class patches `get_drive_service` with chained `MagicMock` comment/reply requests; `_make_http_error` supplies status-specific API failures.
- **TestListComments** (5) — Comment listing combines pages, handles empty results, and exercises both incremental and full-history request paths.
- **TestCommentsErrors** (3) — Listing translates HTTP 401 to `AuthError`, 403 to permission denial, and 404 to document-not-found.
- **TestListCommentsFiltering** (4) — `include_resolved=False` filters resolved threads client-side, while `include_anchor` controls whether `quotedFileContent(value)` is requested.
- **TestCreateComment** (3) — Comment creation returns created content and translates authentication and missing-document failures.
- **TestCreateReply** (4) — Replies send either `content` or a `resolve`/`reopen` action without the other field, and translate authentication failures.
- **TestDeleteComment** (3) — Comment deletion returns `None` on success and translates authentication or missing-document failures.
- **TestGetComment** (3) — Single-comment lookup returns full thread data and translates authentication or missing-document failures.
Notes: The incremental-list tests only verify that a request occurs, not the exact presence or omission of `startModifiedTime`.

#### `tests/test_docs_batch.py` — `gdoc/api/docs.py` (`get_document`, `find_text_in_document`, `replace_formatted`)
Mocking: Patches the Docs service factory; `_mock_document`, `_mock_document_multi_para`, and `_docs_chain` build minimal API documents and service chains.
- **TestGetDocument** (3) — Document reads pass `documentId`, return the API body unchanged, and translate 404 to `GdocError` and 401 to `AuthError`.
- **TestFindTextInDocument** (9) — Text matching returns correct Docs indexes across runs and paragraphs, supports case sensitivity, multiple matches, misses, and empty documents.
- **TestReplaceFormatted** (6) — Formatted replacement uses revision-controlled, last-to-first batch updates, rejects overlaps with exit 3, emits styles, and translates API failures.

#### `tests/test_sheets_api.py` — `gdoc/api/sheets.py`
Mocking: Patches the Sheets service factory; `_mock_service` and `_make_http_error` provide service doubles and status-specific Google API failures.
- **TestTranslateHttpError** (6) — Sheets errors map 401 to auth exit 2, invalid ranges to exit 3, and other statuses to specific user-facing errors.
- **TestGetSpreadsheetMeta** (2) — Metadata reads normalize spreadsheet title and sheet grid properties, and translate HTTP failures at the API boundary.
- **TestGetValues** (2) — Value reads preserve returned range and ragged rows while representing an absent `values` field as an empty list.
- **TestWriteValues** (3) — Writes choose update or append, use `RAW` or `USER_ENTERED`, send values correctly, and normalize updated range, row, and cell counts.
- **TestBatchGetValues** (1) — Multiple ranges use one `batchGet`, preserve request order, and normalize missing values to empty lists.

#### `tests/test_tabs_api.py` — `gdoc/api/docs.py` (tab flattening, text rendering, lookup)
Mocking: Patches only `get_docs_service` for document-fetch tests; local `_run` and `_para` helpers build styled Docs API paragraphs.
- **TestExtractParagraphsText** (6) — Paragraph extraction concatenates text runs in order while ignoring tables, inline objects, and missing content.
- **TestFlattenTabs** (6) — Tab flattening preserves preorder and body metadata, computes nesting levels recursively, and supplies safe defaults for missing properties.
- **TestGetDocumentTabs** (5) — Tab retrieval requests `includeTabsContent=True`, returns a flattened hierarchy, handles emptiness, and translates 401 and 404 API errors.
- **TestGetTabText** (12) — Tab text renders paragraphs, tables, and mixed content; optional Markdown adds heading prefixes while plain mode keeps headings bare.
- **TestGetTabTextInlineMarkdown** (7) — Markdown rendering preserves bold, italic, combined emphasis, strike, links, and marker-adjacent spaces; plain mode strips styling.
- **TestGetTabTextListMarkdown** (6) — Markdown rendering emits nested bullet and ordered lists with independent counters and resets; plain mode omits list markers.
- **TestResolveTab** (7) — Tab lookup matches titles case-insensitively before IDs and raises exit-code-3 errors when no tab matches.

#### `tests/test_account_context.py` — `gdoc/api/__init__.py`, `gdoc/api/docs.py`, `gdoc/api/revisions.py`, `gdoc/util.py`, `gdoc/cli.py`
Mocking: Autouse isolation clears service caches and removes the default account; `_fake_services` patches credentials and service construction to record account ownership.
- **(module-level)** (10) — Concurrent commands isolate credentials, cache services by account and token identity, restore contexts, validate names, and pin each non-MCP invocation consistently.

#### `tests/test_auth.py` — `gdoc/auth.py`, `gdoc/util.py` (account configuration), `gdoc/cli.py` (`cmd_auth` integration)
Mocking: Tests patch OAuth factories, token/config paths, environment variables, URL fetching, refresh transport, and filesystem calls; one subprocess exercises the real CLI boundary.
- **TestAuthenticate** (5) — authenticate supports browser and headless OAuth, reports missing configuration/exchange failures, and stores named-account tokens while establishing the first default.
- **TestClientConfigSources** (9) — OAuth client configuration comes from environment pairs, credential paths, or setup URLs, validating content, failures, precedence, persistence, and mode 0600.
- **TestAuthHints** (3) — `--domain` or `GDOC_AUTH_DOMAIN` supplies Google's `hd` hint in browser and headless authorization flows.
- **TestGetCredentials** (5) — cached credentials return directly; expired tokens refresh and save, revoked tokens require authentication, while transport failures remain exit-code-1 network errors.
- **TestDefaultAccount** (5) — configured defaults select named tokens, explicit accounts override them, nonexistent defaults fail, and account listings display the default alias.
- **TestLoadToken** (3) — missing, corrupt, or structurally invalid token files return no credentials, with corrupt JSON removed.
- **TestSaveToken** (3) — token writes are atomic and mode 0600 from creation, including overwrites of loosely permissioned files.
- **TestCmdAuthIntegration** (1) — invoking `python -m gdoc auth` without client credentials exits 2 and explains that `credentials.json` is missing.

### Awareness and state

#### `tests/test_state.py` — `gdoc/state.py` (`DocState`, `load_state`, `save_state`, `update_state_after_command`)
Mocking: Patches `STATE_DIR` to `tmp_path`; both update classes define `_make_change_info` helpers for pre-flight-like objects.
- **TestDocState** (2) — `DocState` initializes every awareness field predictably and accepts persisted version, timestamp, and comment-ID values.
- **TestSaveLoadState** (7) — State files round-trip atomically, create their directory, tolerate missing, corrupt, or forward-version JSON, and use `<doc_id>.json` paths.
- **TestUpdateStateAfterCommand** (22) — Command completion advances seen, version, read-baseline, and comment-check fields only when full-document knowledge or reliable version evidence permits.
- **TestCommentStatePatch** (12) — Comment mutations add, resolve, reopen, or delete IDs without duplicates while preserving quiet-mode comment-check timestamps and merging pre-flight state first.
Notes: `TestUpdateStateAfterCommand` covers both read commands and write-specific baseline rules despite its broad name.

#### `tests/test_notify.py` — `gdoc/notify.py` (`ChangeInfo`, `pre_flight`, `_format_time_ago`)
Mocking: Drive metadata/version, comments, persisted state, and the clock are patched; `TestPreFlightChanges._make_state` builds shared `DocState` baselines.
- **TestChangeInfo** (10) — Change and conflict properties distinguish edits or comment activity from clean state, comparing current version against the last-read version.
- **TestPreFlightQuiet** (2) — `--quiet` makes `pre_flight` return `None` before loading state or calling Drive and comments APIs.
- **TestPreFlightFirstInteraction** (3) — First contact reports title, owner, version, open/resolved counts, and seeds all known and resolved comment IDs.
- **TestPreFlightChanges** (10) — Later checks report version edits and new, resolved, reopened, or replied comment threads without misclassifying old or action-only replies.
- **TestFormatTimeAgo** (7) — ISO timestamps become seconds, minutes, hours, or singular/plural days ago; empty and invalid values produce no label.

#### `tests/test_pull_hook.py` — `gdoc/cli.py` (`cmd_pull_hook`)
Mocking: Patches Drive export, metadata/version lookup, service access, and state persistence; helpers create hook arguments and JSON stdin payloads.
- **TestPullHookBasic** (3) — `_pull-hook` refreshes stale or untracked Markdown, preserves `gdoc` frontmatter, reports the pulled version, and records pull state.
- **TestPullHookSkips** (7) — `_pull-hook` exits 0 without pulling for matching versions, irrelevant or missing files, absent metadata, or incomplete stdin payloads.
- **TestPullHookErrorHandling** (2) — Malformed JSON and API failures are swallowed so the pre-tool hook always returns 0.

#### `tests/test_sync_hook.py` — `gdoc/cli.py` (`cmd_sync_hook`)
Mocking: Autouse fixture patches tab count to one; tests patch Drive writes/service and state, with helpers for hook arguments and JSON stdin.
- **TestSyncHookBasic** (3) — `_sync-hook` strips frontmatter, pushes the Markdown body, reports the document, and records a full-document push with returned version.
- **TestSyncHookSkips** (6) — `_sync-hook` exits 0 without writing for irrelevant or missing files, absent metadata, empty stdin, or payloads lacking a path.
- **TestSyncHookErrorHandling** (2) — Malformed JSON and API failures are swallowed so the post-tool hook never blocks the caller.
- **TestSyncHookMultiTabSafety** (1) — Multi-tab documents are skipped with a stderr warning, preventing the automatic full-document write from flattening tabs.

### Parsing, formatting, diffing

#### `tests/test_format.py` — `gdoc/format.py`
Mocking: No boundary is patched; each function is exercised directly with `SimpleNamespace` arguments and parsed JSON output.
- **TestGetOutputMode** (5) — Output mode selects `json`, `verbose`, `plain`, or defaults to `terse` when flags or attributes are absent.
- **TestFormatSuccess** (3) — Success messages remain plain in terse and verbose modes, while JSON mode returns `{"ok": true, "message": ...}`.
- **TestFormatJson** (3) — JSON formatting always adds `ok: true` and preserves single, multiple, and nested payload fields.
- **TestFormatError** (2) — Error formatting prefixes every message, including an empty one, with `ERR: `.

#### `tests/test_annotate.py` — `gdoc/annotate.py` (`annotate_markdown`)
Mocking: No boundary is patched; `_make_comment` builds Drive-shaped comments with configurable anchors, resolution state, and replies.
- **TestSingleMatchAnnotation** (3) — A uniquely matched anchor places its open-thread annotation immediately after the anchor's final content line.
- **TestMultipleMatchesAmbiguous** (1) — Repeated anchor text moves the thread to `UNANCHORED` with `anchor ambiguous`.
- **TestZeroMatchesDeleted** (1) — Missing anchor text moves the thread to `UNANCHORED` with `anchor deleted`.
- **TestShortAnchorTooShort** (2) — Anchors shorter than four characters are unanchored as too short; four-character anchors remain eligible for inline placement.
- **TestMultilineAnchor** (2) — Unique multiline anchors annotate after their last line, while repeated multiline anchors are marked ambiguous.
- **TestUnanchoredComment** (2) — Missing or empty `quotedFileContent.value` places a thread in the unanchored section.
- **TestMixedAnchoredAndUnanchored** (1) — Anchored threads remain inline while general comments appear after all document content under `UNANCHORED`.
- **TestEmptyDocumentWithComments** (1) — Comments targeting text in an empty document are retained as unanchored deleted-anchor threads.
- **TestResolvedFilter** (2) — Resolved threads show a `resolved` marker only when `show_resolved=True` and are hidden otherwise.
- **TestLineNumberFormat** (2) — Content lines use right-aligned six-column numbers and tabs; annotation lines use the unnumbered annotation prefix.
- **TestRepliesShown** (3) — Text replies appear with author prefixes for anchored or unanchored threads, while action-only replies remain hidden.
- **TestAnchorTextTruncation** (1) — Displayed anchor labels longer than 40 characters are truncated with an ellipsis.

#### `tests/test_mdparse.py` — `gdoc/mdparse.py` (`parse_markdown`, `to_docs_requests`)
Mocking: No external boundary is patched; tests directly inspect parsed text, style/table metadata, and generated Docs request dictionaries.
- **TestParsePlainText** (4) — plain, multiline, whitespace-only, and empty inputs preserve text and trailing-newline conventions without character styles.
- **TestParseBold** (3) — asterisk and underscore bold syntax is removed from output and produces exact bold ranges in standalone or surrounding text.
- **TestParseItalic** (3) — asterisk and underscore italic syntax is removed from output and produces exact italic ranges in standalone or surrounding text.
- **TestParseBoldItalic** (1) — triple-emphasis syntax produces coincident bold and italic ranges over the marker-free text.
- **TestParseInlineCode** (2) — inline code removes backticks and applies Courier New to the exact code span.
- **TestParseLink** (2) — Markdown links retain visible text, remove destination syntax, and apply the URL to the exact text range.
- **TestParseHeadings** (4) — heading markers map levels one through six to named paragraph styles while preserving inline formatting offsets.
- **TestParseBulletList** (3) — dash and asterisk lists remove markers, emit bullet metadata per item, and retain inline styles.
- **TestParseNumberedList** (1) — numbered-list markers become decimal/alpha/Roman bullet metadata for every item.
- **TestParseMixed** (3) — mixed headings, paragraphs, lists, bold, italic, and code preserve readable text and emit each applicable style.
- **TestParseTable** (8) — valid pipe tables become sized row metadata plus placeholders, track offsets, normalize uneven rows, and coexist with text or other tables.
- **TestToDocsRequests** (10) — request generation inserts text, offsets ranges, emits exact style and bullet fields, handles empties, and orders paragraph before text before bullets.
- **TestParseNormalTextEmission** (6) — every non-heading paragraph, including list items and table placeholders, emits NORMAL_TEXT; headings emit only their heading style.
- **TestToDocsRequestsTabId** (6) — supplied tab IDs propagate to insert, text-style, paragraph-style, and bullet locations; omitted IDs add no `tabId` fields.
- **TestParagraphStyleBeforeTextStyle** (2) — all paragraph-style requests precede character-style requests so named-style application cannot erase bold, italic, or links.
- **TestBackslashEscapes** (11) — escapable punctuation becomes literal without triggering Markdown, real adjacent formatting retains correct ranges, and code spans preserve internal backslashes.
- **TestParseStrikethrough** (2) — strikethrough markers are removed and produce exact style ranges in standalone and surrounding text.
- **TestNestedEmphasis** (5) — nested and abutting bold, italic, strikethrough, and link constructs produce independent, correctly bounded style ranges.
- **TestBlockquote** (2) — blockquotes remove the marker, emit NORMAL_TEXT with indentation, and retain inline formatting.
- **TestHorizontalRule** (4) — valid dash, asterisk, and underscore rules emit a bottom-border paragraph, while emphasized text is not misclassified.
- **TestFencedCode** (4) — fenced blocks remove fences and language labels, preserve lines and indentation, apply code fonts, and suppress inline Markdown parsing.
- **TestNestedLists** (4) — nested list depth becomes leading tabs with correct bullet metadata and character-style offsets.
- **TestNewToDocsRequests** (5) — generated requests include blockquote, rule, and strikethrough fields while ordering and reindexing nested bullets correctly.
- **TestTableTabAdjustment** (4) — parser metadata tracks tabs removed by nested-list bullet conversion, both globally and before each table.

#### `tests/test_mdimport.py` — `gdoc/mdimport.py`
Mocking: No API boundary is patched; tests create temporary local image files and inspect extracted descriptors or stripped Markdown.
- **TestExtractImages** (11) — Extraction replaces local and HTTP images with ordered placeholders, resolves safe paths and MIME types, and rejects traversal, missing, or unsupported files.
- **TestStripImages** (9) — Image stripping removes inline, standalone, remote, and reference-style images, collapses excess blank lines, and preserves other Markdown.

#### `tests/test_frontmatter.py` — `gdoc/frontmatter.py`
Mocking: No boundary is patched; tests directly parse and generate Markdown frontmatter, with one parametrized line-separator case.
- **TestParseFrontmatter** (15) — Parsing recognizes only valid leading key-value blocks, preserves bodies exactly, handles malformed lines and colons, and leaves thematic-break Markdown untouched.
- **TestAddFrontmatter** (6) — Generation serializes metadata and body predictably, round-trips, and flattens every recognized line separator to prevent key injection.
Notes: `test_every_line_separator_flattened` runs against eight separators but counts as one test function.

#### `tests/test_diffrender.py` — `gdoc/diffrender.py`, `gdoc/revdiff.py`
Mocking: No external boundary is patched; `_model` builds revision-diff models and `_paragraphs` generates stable paragraph sequences.
- **TestSelectVisible** (3) — Visibility keeps changed context, all headings, and comment-anchored hunks while allowing unrelated unchanged hunks to collapse.
- **TestSplitComments** (1) — Comments are grouped by hunk in input order, with unanchored threads separated for an appendix.
- **TestRenderTerminal** (6) — Terminal rendering shows word-level changes, optional ANSI styling, collapsed context, revision headers, headings, and preserved list markers.
- **TestRenderHtml** (4) — HTML rendering is self-contained, escapes document content, uses `ins`/`del`, and presents anchored and appendix comment threads with replies and resolution.

#### `tests/test_revdiff.py` — `gdoc/revdiff.py` (revision selectors, hunk construction, comment attachment)
Mocking: No boundary is patched; sparse `REVS`, fixed sentence constants, and `_comment` provide deterministic revision and comment inputs.
- **TestSelectors** (14) — REV selectors resolve sparse IDs, aliases, positional ancestors, and ISO timestamps correctly, with exit code 3 for unavailable or invalid selections.
- **TestRevRange** (4) — `--rev` accepts `A..B` or defaults a single selector to `latest`, while rejecting half-open ranges with exit code 3.
- **TestCleanText** (6) — Export cleanup removes Markdown escaping and blockquote noise, decodes entities, normalizes whitespace, and replaces image references with `⟦diagram⟧`.
- **TestLoadBlocks** (2) — Block loading drops blanks, image definitions, and standalone image data while preserving prose that merely mentions `data:image`.
- **TestBlockClassification** (3) — Markdown headings, bullets, ordered items, and paragraphs receive the correct block type and stripped display text.
- **TestWordDiffCoalescing** (4) — Word diffs coalesce short unchanged islands inside rewrites, preserve meaningful edge matches, and return one equal run for identical text.
- **TestBuildHunks** (11) — Hunk construction preserves visible text and structure changes, records heading/list metadata, and treats export-only escaping or ordered renumbering as equal.
- **TestAttachComments** (10) — Comments prefer changed current-side anchors, retain deleted or unmatched threads appropriately, reject weak false matches, omit action-only replies, and sort chronologically.
Notes: Two selector and classification tests are parametrized; each parametrized function is counted once.

#### `tests/test_util.py` — `gdoc/util.py`
Mocking: Only destructive confirmation patches stdin and `input`; URL, error, typography, and URL-building helpers are exercised directly.
- **TestBuildDocUrl** (3) — Document URLs use the canonical edit path and append `?tab=` only when a tab ID is supplied.
- **TestExtractDocId** (13) — ID extraction accepts Docs, Drive file/folder, query-parameter URLs, fragments, bare IDs, and whitespace while rejecting empty or invalid input.
- **TestErrorClasses** (5) — `GdocError` defaults to exit 1, permits custom codes, and `AuthError` is a `GdocError` fixed at exit 2.
- **TestConfirmDestructive** (4) — Destructive actions require `--force` in non-interactive use, accept explicit `y`, and cancel with exit 3 on refusal.
- **TestFoldTypography** (4) — Typography folding maps smart quotes and en/em dashes to length-preserving ASCII while leaving existing ASCII unchanged.

### MCP server

#### `tests/test_mcp.py` — `gdoc/mcp.py`, `gdoc/cli.py` (`build_parser`, command dispatch)
Mocking: An autouse fixture clears `GDOC_ALLOW_COMMANDS` and `GDOC_ACCOUNT`; tests monkeypatch parser dispatch, account context, services, stdio, and temporary-file handling.
- **Tool surface** (17, module-level) — `build_tools` derives one tool per allowed command from argparse: write commands are dropped in read-only mode, image commands and HTML diff are never exposed, local-path parameters are stripped, choices become enums, required options are marked, and write descriptions flag mutation.
- **Argument mapping** (14, module-level) — tool arguments become a safe argv: options before positionals, dash-prefixed text shielded, unknown or skipped arguments rejected, booleans must be real booleans, inline text goes through a temp file, and `delete-comment` needs a literal `true` force.
- **Call execution** (10, module-level) — each call captures stdout and exit code, pins its account without leaking to the next call or bypassing a default, restores context when a call raises, keeps cached services per account, and never reads the server's stdin.
- **JSON-RPC handling** (14, module-level) — `initialize` echoes a known protocol version, notifications get no response, unknown methods and tools map to the right error codes, the error body is the `ERR:` line not the banner, `diff` exit 1 means differences not failure, and notes travel as a separate content item.
- **stdio serving** (5, module-level) — the serve loop round-trips frames, reports malformed JSON, answers batches with an array, rejects non-object frames, and keeps stray prints off the protocol stream.
Notes: This file has no test classes; the five groups above are by theme, not by class.

### Self-update

#### `tests/test_update.py` — `gdoc/update.py`, `gdoc/cli.py` (`_is_top_level_help_invocation`)
Mocking: Monkeypatches executable paths, environment variables, version lookups, cache location, subprocess execution, and re-exec; fixtures provide an isolated cache and simulated uv install.
- **TestIsUvToolInstall** (4) — uv-tool detection requires the exact adjacent `.local/share/uv/tools` path and rejects ordinary virtualenvs or out-of-order lookalikes.
- **TestAutoUpdateForHelpSkips** (6) — Help auto-update avoids network or installation when disabled, recursive, non-uv, current, offline, or covered by a fresh cache.
- **TestAutoUpdateForHelpUpgrades** (2) — A newer release runs `uv tool install`, re-execs with a recursion guard, reports versions, and warns without re-exec on failure.
- **TestTopLevelHelpDetection** (6) — Only no arguments, `--help`, and `-h` trigger top-level help auto-update; subcommands and `--version` do not.
Notes: The final class protects `gdoc/cli.py` despite living in the update test module.

#### `tests/test_update_version.py` — `gdoc/update.py`
Mocking: Patches installed/latest version lookups, subprocess execution, and cache writes only for `run_update`; comparison helpers are tested directly.
- **TestVersionTuple** (2) — Dotted versions parse into integer tuples, including multi-digit components.
- **TestIsNewer** (4) — Version comparison is numeric, recognizes newer releases, and rejects equal or older versions.
- **TestRunUpdateStaleRemote** (2) — Manual update never downgrades from a stale older remote version and installs when the remote version is newer.

## Fidelity suite (`fidelity-tests/`)

The question this suite answers: can an agent holding only the gdoc CLI carry out a
colleague's plain-language edit request on a messy real document without collateral damage?
Nothing here is mocked. The harness lives in `fidelity-tests/bin/`, the procedure and judging
rules in the repo-local skill `.claude/skills/gdoc-fidelity-test/` (`references/verdict.md`,
`references/diff.md`, `references/capture.md`).

### Fixtures

A fixture is a Google Doc built by hand in the browser from a `prompt.md` that asks for the
mess a real internal doc accumulates (emoji in headings, Word paste with four fonts in one
paragraph, fake headings, manual numbering, a comment spanning a formatting boundary), then
frozen as a named version. Each fixture directory holds:

- `prompt.md` — what the builder was asked to make.
- `built.md` — the as-built record: exact text top to bottom, styles, UTF-16 indices, and the
  trap list the tasks are written against.
- `fixture.md` — doc URL, Drive folder, frozen revision (both the Drive revision number and the
  Docs `revisionId`, since the two APIs disagree), gdoc version at build time.
- `baseline/` — CLI captures of the frozen doc: `structure.json`, `cat.md`, `comments.json`,
  `revisions.json`, plus viewport screenshots at fixed scroll offsets.
- `tasks.md` — the edit requests, five fields each: **Request** (the colleague's wording),
  **Expected** (what the doc must read afterwards, including what must stay intact),
  **Target** (tab, paragraph or cell the edit is confined to), **Allowed** (side effects that
  are not collateral, e.g. the revision list grows), **Preconditions** (what must be present
  on the copy for the run to be valid).
- `runs/<date>-<slug>/` — one directory per run: `before/` and `after/` captures,
  `transcript.md` (the agent's own report), `diff.md` and `diff.json` (structural judge),
  `verdict.md`, `gates.txt`, `copy_id.txt`, `copy_method.txt`.

| Fixture | What it stresses | Tasks |
|---|---|---|
| `kitchen-sink/v01` | a bit of everything: table with chips, footnote, strikethrough run, pending suggestion, open comment | 7 |
| `lists/v01` | three lists that render as one, checklist with ticked items, mixed glyph levels, headings inside a list, a font run and a comment each spanning two items | 12 |
| `tables/v01` | merged header and owner cells, comment inside a merge, suggestion in a cell, dropdown and date chips, nested bullets in cells, borderless layout table | 11 |
| `text/v01` | near-duplicate targets differing only by case, quote style or dash type; NBSP; four fonts in one justified paragraph; sub/superscript, small caps | 11 |
| `collab/v01` | 9 comments (open, resolved, orphaned, threaded) and 12 pending suggestions of every kind | 6 |
| `objects/v01` | images, drawings, equations: prompt written, doc not built | 0 |

### One run

1. `gdt run-start FIXTURE SLUG` copies the fixture into the runs folder, renames it, checks
   the two entry gates (copy matches baseline; task preconditions present) and takes the
   before-capture. Copies whose task needs comments or suggestions are made through the Docs
   UI by a browser agent, because Drive `files.copy` drops both.
2. **Agent track:** a fresh agent is spawned from an empty scratch directory with only the
   request, the copy URL and the account (`bin/task-agent-prompt.md`), told to use only gdoc
   and to decline if it believes the request cannot be done. **Command track:** the runner
   executes the single gdoc command from `repros.md` on a fresh copy, to isolate the CLI from
   the agent's choices.
3. `gdt-transcript` files the agent's report and calls `gdt run-end`, which takes the
   after-capture, checks the revision advanced, and runs `gdt-diff`.
4. Two judges. **Structural:** `gdt-diff` normalises the two `structure.json` dumps, canonicalises
   every style against the doc's named styles, aligns paragraphs with `difflib`, and classifies
   every changed property as `expected`, `allowed` or `unexpected` against the task's Target and
   Allowed fields. **Visual:** a subagent compares before/after screenshots and answers a fixed
   brief. A human judge is recorded when the two disagree.
5. `gdt-verdict` writes `verdict.md`; `gdt-index` regenerates `INDEX.md`; `gdt-review`
   regenerates `REVIEW.md` for manual before/after review in the browser.

Since 2026-09-03 tasks also run as **batches**: all of a fixture's tasks in document order on
one copy, each by a fresh agent, each judged against the state the previous task left. The
runner then makes a **painted review copy** (`gdt-paint`): green background on every expected
change, red on collateral, amber on allowed side effects, a red left border where
paragraph-level style changed, and one numbered comment per task. Those five painted copies
are the fastest way to see the suite's results in the browser; `REVIEW.md` opens with them.

### Verdicts

One outcome per run, decided in this order (`references/verdict.md`):

1. Any gate failed → **INVALID**. The run does not count.
2. Any `unexpected` diff item → **COLLATERAL**, whatever else happened.
3. Expected outcome present, nothing unexpected → **DONE**.
4. Nothing changed and the agent said it could not: the Docs API has no way to express the
   request → **DECLINED-API**; the API can but gdoc cannot → **GAP-CLI**; gdoc can →
   **FAIL-AGENT**.
5. Nothing changed, or the wrong thing did, and the agent claimed success → **FAIL-AGENT**.

Two rates over valid runs, never one pass rate: **completion** = DONE / valid, **safety** =
(valid − COLLATERAL) / valid. Agent and command tracks are scored separately.

### Results as of 2026-09-03

98 judged runs: 94 agent track, 4 command track. Outcomes: DONE 46, COLLATERAL 39, GAP-CLI 7,
DECLINED-API 3, FAIL-AGENT 1, INVALID 2.

| Fixture | Valid runs | Agent completion | Agent safety | Command completion / safety |
|---|---|---|---|---|
| `collab/v01` | 10 | 4/10 | 6/10 | – |
| `kitchen-sink/v01` | 16 | 8/14 | 10/14 | 0/2 / 0/2 |
| `lists/v01` | 26 | 10/24 | 15/24 | 0/2 / 0/2 |
| `tables/v01` | 22 | 18/22 | 20/22 | – |
| `text/v01` | 22 | 6/22 | 6/22 | – |
| **All** | **96** | **46/92** | **57/92** | **0/4 / 0/4** |

What the failures are (`plans/20260902-overnight-report.md`, `repros.md`):

- **`gdoc edit` rewrites the whole paragraph, not the match.** Every COLLATERAL so far is this
  one behaviour: a one-word replace drops bold, italic, strikethrough, highlight, colour, font
  and size on runs outside the match, and drops paragraph-level style too (right alignment, 1.5
  spacing, a 36pt indent, and with `--all` the HEADING_1 named style). Agents that re-read with
  `gdoc structure` could repair bold, italic and links via Markdown; nothing in gdoc restores
  colour, font, size, alignment or spacing, and `gdoc cat` shows none of them, so most agents
  reported success. Overlaps [LucaDeLeo/gdoc#57](https://github.com/LucaDeLeo/gdoc/issues/57).
- **Comment anchors shrink and the structural judge cannot see it.** `gdoc comments --json`
  returns `quotedFileContent` but no `anchor`, so an edit that swallows half an anchor produces
  a clean diff; only the visual judge caught it (two runs recorded COLLATERAL on that basis).
- **Structure the API allows but gdoc cannot express** (GAP-CLI): joining a paragraph to an
  existing list at a chosen nesting level, deleting a table row, editing footnote text, adding
  text as a suggestion.
- **The one honest DECLINED-API:** ticking a checklist item; the Docs API has no checkbox state.

`repros.md` holds ten one-command reproductions of these, meant to be rerun after every CLI
change. `CORRECTIONS.md` logs harness fixes made along the way and two open policy calls
(whether comment `modifiedTime` and pagination hints count as changes).

### Known limits of the harness

- `gdoc cp` drops comments and suggestions, and the Docs-UI copy drops resolved comments, so
  any "reopen a resolved comment" task is currently INVALID by construction.
- Screenshots are viewports at fixed scroll offsets, not pages, and both screenshots and visual
  judging go through subagents to keep the driver's context small.
- Task agents cannot be given a truly empty working directory by the Agent tool; isolation is
  by instruction, and every agent so far has honoured it.
- Agents that decline sometimes leave scratch copies in Drive; gdoc has no trash command, so
  those are renamed `SCRATCH … safe to delete` by hand.
