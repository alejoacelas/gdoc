# Markdown rebuild safeguards

The human wanted write and push to protect native structures that Markdown cannot represent, warn when rebuilding styles, and skip unchanged whole-document uploads.

- Added failing tests first, then guarded whole-document writes, pushes and tab replacements; `--allow-lossy-rebuild` permits structural loss independently of conflict and tab-collapse overrides.
- Kept headings, lists and style overrides writable with one warning; comment anchors conservatively protect tab replacements because Drive does not reliably identify their tab.
- Verified exact Drive upload parameters and Docs replacement batches, unchanged-content no-ops, refusal without state advancement, and MCP boolean flag mapping. All 1,619 tests, Ruff and the stub check pass.
- Created one synthetic throwaway document with a heading, list, coloured/highlighted text, end-aligned paragraph and footer. Both write scopes exited 3 without mutation requests; raw structure and Drive version stayed identical. Trashed the document afterward.
- Cleared 196 inherited lint findings in a separate mechanical commit to meet the requested repository-wide check. The Drive wrapper's only cleanup is a string-literal line wrap; importer and parser behavior remain unchanged.
- Committed locally without pushing or creating a pull request.

Agent session 01a070b6-1977-7d60-81c1-44b9a866dac2 · Commits ee5995f, b8110d6, 49813ed

# Babysitting PR #62 through Codex review

The human wanted PR #62 (the Markdown rebuild safeguards) driven to green with every Codex finding fixed and answered on its thread, and the guard restructured so review could converge.

- Codex reviews in LucaDeLeo/gdoc run only on an explicit `@codex review` comment and must be re-summoned after every push. Thirty-three passes produced 49 findings; each was fixed or rebutted on its thread with the commit, and the thread resolved.
- After five passes each surfaced one more unsupported element kind, the guard was restructured from a denylist to deny-by-default: an explicit allowlist (normal-text and heading paragraphs, bullet and numbered lists, and the inline styles `parse_markdown` emits) passes, and any other key blocks under its Docs API field name. One parametrised test feeds every element kind in the schema plus an invented future kind.
- Style-only losses warn instead of blocking. The comparisons use the exact output of each rebuild path, captured live from throwaway documents: the import's named styles, page setup, section style and list glyphs (hyphen bullets, decimal numbering, Arial 11pt markers, 18/36pt indents per level), and the Docs UI presets for tab replacements.
- Tab replacements are verified by an actual round trip: the whole tab is exported the way `write --tab` would and parsed back, and any paragraph whose text, named style, bullet or positional inline styles differ blocks. That check found and fixed exporter gaps (unescaped `)` in URLs, no code spans, emphasis dropped on links) and closed literal-Markdown reinterpretation.
- The unchanged-content no-op records the version read before the export and never applies to multi-tab documents, whose export covers only the first tab.
- CodeRabbit's OSS plan allows one included review per hour org-wide and reported "Review rate limited" after most pushes; it approved the PR mid-session, found the unattended sync hook still uploading without the guard, and raised one design question (comment anchors under `--allow-lossy-rebuild`) that was answered as intentional.
- Two slips during the loop are recorded on the PR: one reply named a commit that did not yet contain the fix (corrected in the next reply) and one push briefly carried a failing test (fixed in the following commit). Both came from chaining GitHub posts after an edit or test step without gating on its exit status.

Agent session e2391fa3-0243-473f-9ab8-753eb57bce16 · Commits 5f0731d, 1ceb87b, 23322de, 5c9291b, e20ebce, c9d9c30, 0ee6b7b, 829dc8a, 7dd134b, cea0fcd, 77202a1, 3b3eb31, 77055ec, 7f13f90, 08cf57c, 2f9b5ba, 4167fa2, a662ea7, 41fa5d6, febb24f, 8b10a71, 952912e, 7864cfd, 29acc48, 155bc93, f7a8549, e156bd7, c85cbbb, 4bc571d, a43683c, d191cfc, 27f18f1, a8b326f, 7877ebe, 969a5fb, d3fc281, fc0f6a4
