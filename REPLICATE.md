# Inline edit formatting

The user wanted inline edits to preserve paragraph and homogeneous direct text styles while retaining intentional whole-paragraph Markdown formatting.

- Added failing exact-request tests before implementation, then passed paragraph/run context from the CLI to the replacement planner; partial list and heading markers now remain literal prose.
- Restored differing direct style fields only over the inserted span, using field-mask resets for absent overrides; covered paragraph starts, UTF-16 ranges, table cells, tabs, conflict warnings, and mixed inline/block matches with `--all`.
- All 1,578 unit tests and the no-stubs gate pass. Full Ruff remains blocked by 196 pre-existing violations, confirmed against the unchanged baseline; this change adds none.
- On one throwaway document, two synthetic edits preserved alignment, link, highlight, list state, and all raw style overrides. Literal JSON equality failed because Google split one run into two with identical styles; coalescing only that split confirmed the two text replacements were the only content changes. The document was trashed.
- Kept mixed-style length-changing edits outside the supported guarantees and left pushing and pull-request creation to the next agent.

Agent session 01a070b6-0c34-7120-8625-a269a21ebf37 · Commits 2cb2ace, 9615182, 8109039

# Inline edit review rounds

The user wanted PR #60 babysat to green with every CodeRabbit and Codex finding settled.

- CodeRabbit's one finding (a shared mock body hid root-body forwarding in the `--tab` route test) was fixed with distinct bodies and confirmed by a mutation check.
- Codex, which on this repo runs only when summoned with `@codex review`, found fence edge cases one regex at a time across seven passes (backtick fences, tilde fences, closers on their own line, unclosed fences). Replaced the accumulated regexes with one CommonMark rule: on a partial-paragraph replacement a backtick string of length N opens a code span that only an equal-length string closes, unmatched strings are literal, and block syntax is literal. Stated in the `edit` epilog and the PR description; covered by a 22-case parametrised test.
- Codex also caught that inserted text does not reliably inherit a neighbour's link and that setting a link resets colour and underline. The baseline restore now reapplies the link with the target's colour and underline, and again after any Markdown link in the replacement.
- Roadblocks: CodeRabbit's one-review-per-hour cap left every commit after the first unreviewed by it, and 68e5b74 shipped with a red test because a pipe to `tail` masked pytest's exit code; fixed in the next commit.

Agent session 8967abb9-167c-43a8-87b8-47b16b1e636d · Commits 26f61a8, ac3546f, 77d3d40, 7f2d6bf, 50fa87f, bdced47, f8b6c88, 68e5b74, 49e1d55

# Preserve native paragraph boundaries

The user wanted PR #60 rebuilt so wording edits preserve paragraph structure and heading deletion never changes a neighbor.

- Split multiline edit and suggest matches into text-only ranges, retaining each native paragraph mark, named style, list ID and nesting; explicit heading/list/quote Markdown changes only its own complete paragraph. Ambiguous paragraph-count changes fail before writing; whole-cell replacement explicitly clears old list state.
- Unified positional, stdin and file input handling: exactly one trailing newline is ignored. Start/end insertion creates its own paragraph before styling, and zero-width paragraph-style requests are skipped.
- Removed speculative post-edit cleanup and its neighbor-promotion/final-newline deletion. Empty replacements retain native marks; the explicit cleanup helper refuses the final mark and image paragraphs.
- Fixed raw code-span closer detection and converted the table-restriction test to pytest-mock. Confirmed the existing tab-route test already uses distinct root and selected-tab bodies.
- Added 57 synthetic offline cases: transport variants, mixed headings/title/subtitle/nested lists, partial multiline context, multiple matches, cell list removal, insertion boundaries, final/nonfinal heading deletion beside normal/list/table/image neighbors, code closers, and suggested multiline edits. All 1,664 tests pass; Ruff has the same 196 baseline findings, with none on added or changed lines.
- Kept the inherited run-style policy unchanged. Export grammar, full-document reconstruction, native target validation, and staged-write concurrency remain outside this PR; no live API replay, push, or PR edits were performed.

Agent session 01a09704-0c2d-79c0-ac5b-677663a7b39c · Commits 3307511, bc5dec3

# Close paragraph replacement review gaps

The user wanted PR #60's adversarial findings and seven harness replays resolved, with offline regressions and a committed, unpushed branch.

- Matched terminal newlines now consume the corresponding replacement terminator; one- and multi-paragraph inputs use the same count check. Fenced replacement content is parsed once for edit and suggest, preserving literal asterisks and links; incompatible rendered paragraph counts fail before service access. Thematic breaks style the retained native mark without inserting another paragraph.
- Empty body replacements remove complete paragraphs, borrowing the preceding newline for a final paragraph and coalescing adjacent deletion ranges. A segment's only paragraph retains its mandatory newline; removal after a table refuses before writing rather than deleting table structure.
- Plain whole-cell wording preserves paragraph properties and list membership, including when collapsing multiple paragraphs. Explicit structural Markdown can still restyle. Insertion resets list indents only when the insertion boundary inherits a bullet.
- Saved replay snapshots showed no neighbor deletion in either heading rename, no shortening of the trailing heading during append, and no new TITLE/SUBTITLE heading IDs. Added guards for those preserved behaviors alongside the confirmed failures; no live write was needed to establish what the saved requests did.
- All 1,724 tests pass (60 more than the starting branch); Ruff has exactly the same 196 diagnostics as origin/main, with zero additions. No push or PR mutation; live verification of the new request plans remains with the coordinator.

Agent session 01a09713-3fb2-72c2-bef4-658137d2e74f · Commits 1596dcd

# Restore whole-cell list removal

The user wanted PR #60's documented plain-prose list-removal route restored, four cell replacement shapes tested, and the second live replay's alleged regressions investigated without pushing.

- Whole-cell plain prose replacing list items now clears bullets and applies NORMAL_TEXT with list-indent resets only to the replacement paragraphs. Empty replacement leaves one NORMAL_TEXT paragraph, including from a non-list heading; explicit Markdown lists still create membership. Nonempty prose in non-list cells and ordinary text-targeted edits keep the preservation policy.
- Added a 16-case request matrix through the real argument parser and `cmd_edit`, covering one/two native paragraphs, prose/empty/list/multiline replacements, bullets/non-list headings, UTF-16 ranges, and tab targeting. Updated obsolete list-preservation expectations and added a nonfinal-heading deletion guard with an inline image later in the body.
- Replay `20260912T193354-7cc207ac02`: the saved request deletes exactly [65,82), the heading plus its LF. After removing that paragraph and ignoring index fields, the remaining body equals the saved after body; the footnotes, inline-object map and sibling tab also remain equal. The image moves from content[7] at [145,147) to content[6] at [128,130); the remote paragraph moves from content[8] to content[7]. No image becomes text and no unrelated paragraph merges.
- Replay `20260912T193230-87278f56aa`: the saved pre-fix batch contains only deletion [27,54) and insertion of Confirmed. Both original list items' paragraphStyle and bullet dictionaries equal the resulting paragraph's dictionaries, including alignment, lineSpacing and avoidWidowAndOrphan; other cells and the outside paragraph remain equal after index normalization. This is whole-cell syntax (one replacement positional), so the new intentional list-to-prose rule applies; there is no old-text search argument in this command.
- Replays `20260912T193329-a481b99e9e` and `20260912T193433-e96b549a92`: both saved requests delete [41,57) and insert the 14-character Final findings without an LF. Both snapshots retain exactly three paragraphs; the introduction is identical, the heading keeps its style and ID, and the final paragraph keeps its text and style while shifting from [58,100) to [56,98). There is no added element or empty paragraph outside the target; array-position/absolute-index comparisons do not establish collateral changes.
- Full `uv run pytest -q`: 1,739 passed; no-stubs gate passed. Ruff reports the same 196 diagnostics as origin/main, with zero added diagnostics when compared by file, code and message. Snapshot comparisons and new planner tests ran offline; no live API write, push or PR mutation was performed.

Agent session 01a0971e-0d33-74c3-9708-fdcfb35bb4b7 · Commits be56630

# Rebuild replacement scope across tabs and segments

The user wanted PR #61 rebuilt on PR #60 so replacements find every intended tab and segment, preserve their coordinates, and fail during planning before sending a write.

- Worktree: `/Users/alejo/best/tools/active/gdoc/pr61-segment-redo`; branch: `alejoacelas/fix-segment-replacements`; base: `88165fcaa982853c2caacf2363cce0b12cee69bd`. Replayed the useful old #61 commits (`6776467`, `5e2827a`, `cbcd4e5`, `dd083e2`, `f60e735`), resolving conflicts against #60's paragraph planner. Omitted the old broad lint cleanup and superseded verification metadata.
- Unscoped text replacement searches every tab, including child tabs. Multiple matches require `--all` or a narrower `--tab`; a unique match in a later tab succeeds without `--all`. Explicit `--tab` restricts the search. `edit --all` reports matched counts by tab ID in terse, plain and JSON output; command help states the rule. Whole-cell targeting retains its existing scope.
- Tab and segment IDs now accompany matching, paragraph/style lookup, overlap checks, context keys, deletion unions, shift calculations and every applicable batch request. Body, header, footer and footnote offsets remain independent, even when tabs reuse segment IDs. Non-body structural Markdown is rejected before mutation. The supplied #60 base already replaced the old `_replacement_text_style` collector with `_inline_baseline`, which uses `.get("startIndex", 0)`; this change routes the correct segment content into that existing safe collector without changing style policy.
- Added 18 synthetic offline regressions in `tests/test_replacement_scope.py`: three output modes prove six replacements across two nested tabs and four container types with correct per-container direct styles; edit/suggest ambiguity cases prove no write; explicit-tab cases and unique-later-tab cases prove scope; a SUGGEST batch proves zero-index header/footer/footnote coordinates on deletes, inserts and text styles; two missing-container and two late-request-builder failures prove planning finishes before mutation; a later-tab pending suggestion blocks the entire batch; empty replacement keeps six independent deletion ranges; two help checks prove the documented scope rule. Retained and adapted 45 segment regressions from old #61.
- Full `uv run --offline pytest -q`: **1,802 passed** (63 more than the 1,739-test base). The focused inherited suite passed 283 tests before the new matrix. `bash scripts/check-no-stubs.sh` and `git diff --check` pass. Ruff has exactly the same **196** diagnostics as `origin/main`, with zero additions or removals when compared by relative file, rule, message and offending source line. Dependency synchronization used `uv sync --offline --extra dev`.
- Initial inherited tests still mocked the former body-only read and had to be updated to mock the all-tab read; old cleanup assertions were replaced with assertions that #60's removed cleanup remains unused. No campaign files, main checkout, comment anchoring, tab-title ambiguity rules, style inheritance policy, or broad lint cleanup were changed. Staged table-write concurrency and live API verification remain outside this PR; no push or PR creation was performed. The coordinator owns final review, rebase and publication.

Agent session 01a09723-74a3-7451-a0c5-49d86b0e2d14 · Commits 8384c09, 3640b4e, 9fc51e7, d694bc7, 085f11c, cef3806, 40f279e

# Close segment deletion and ambiguity review findings

The user wanted both PR #61 P2 findings fixed, the header suggestion request checked, and the branch committed without pushing.

- Normalize omitted paragraph start indices to zero in the existing deletion helper. Header, footer and footnote first-paragraph removal now includes the paragraph mark; last-paragraph removal borrows the preceding mark and preserves the segment-final newline.
- Cross-tab edit/suggest ambiguity errors name every matching tab by title and ID. Same-tab ambiguity recommends `--all` or more specific text, without implying `--tab` can resolve it. Both paths still fail before writing.
- Added 12 fixed-coordinate deletion cases covering three segment types, explicit/omitted zero indices and first/last paragraphs, plus two same-tab ambiguity cases; extended both cross-tab ambiguity tests. Before the fix, seven assertions failed on the reported defects; afterward the focused suite passed 32 tests and full `uv run pytest -q` passed 1,816 tests. The no-stubs and diff checks pass; Ruff matches origin/main's 196 diagnostics exactly, with zero additions or removals by file, rule, message and source line.
- Saved replay `20260912T195004-00768dcae2` confirms one successful SUGGEST batch with the source revision guard, header/tab identity, deletion [8,14), and insertion of UPDATED at 8. Accepted/rejected previews have the intended text and all three views preserve the body. UPDATED is bold in the inline suggestion view but plain in the accepted preview; G08 style handling remains with #63 and was not changed.
- No live writes or push; the coordinator owns live acceptance and publication.

Agent session 01a0972d-e63f-7db3-81be-e10b7e0508cd · Commits cc6952c
