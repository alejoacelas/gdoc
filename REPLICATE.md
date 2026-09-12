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
