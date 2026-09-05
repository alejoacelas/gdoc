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

The human wanted PR #62 (the Markdown rebuild safeguards) driven to green with every Codex finding fixed and answered on its thread.

- Codex reviews in LucaDeLeo/gdoc run only on an explicit `@codex review` comment. Eight passes produced 14 findings; each was fixed, replied to with the commit, and its thread resolved.
- After five passes each surfaced one more unsupported element kind (table of contents, breaks, page settings, section breaks, smart chips, drawings), the guard was restructured from a denylist to deny-by-default: an explicit allowlist (named-style paragraphs, bullet and numbered lists, and the inline styles `parse_markdown` emits) passes, and any other key blocks under its Docs API field name. One parametrised test feeds every element kind in the schema plus an invented future kind.
- Live checks on throwaway documents showed Drive's Markdown import resets page mode, size, margins, orientation, background and named-style definitions, and rebuilds lists with hyphen bullets and decimal numbering. Because the import forces US Letter even on an untouched A4 document, those became warnings rather than blockers.
- The unchanged-content no-op now records the version read before the export, so a concurrent edit can only surface as a conflict on the next write, never be adopted as an unseen baseline.
- CodeRabbit's OSS plan allows one included review per hour org-wide and reported "Review rate limited" on every push; manual `@coderabbitai review` retries were needed once the window reopened. Its one review found the unattended sync hook still uploading without the guard.
- A ninth Codex pass caught that the export used for the no-op check covers only the first tab, so multi-tab documents never no-op now, and that an explicit right-to-left paragraph direction was allowlisted silently.

Agent session e2391fa3-0243-473f-9ab8-753eb57bce16 · Commits 5f0731d, 1ceb87b, 23322de, 5c9291b, e20ebce, c9d9c30, 0ee6b7b, 829dc8a, 7dd134b, cea0fcd
