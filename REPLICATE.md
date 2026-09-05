# Markdown rebuild safeguards

The human wanted write and push to protect native structures that Markdown cannot represent, warn when rebuilding styles, and skip unchanged whole-document uploads.

- Added failing tests first, then guarded whole-document writes, pushes and tab replacements; `--allow-lossy-rebuild` permits structural loss independently of conflict and tab-collapse overrides.
- Kept headings, lists and style overrides writable with one warning; comment anchors conservatively protect tab replacements because Drive does not reliably identify their tab.
- Verified exact Drive upload parameters and Docs replacement batches, unchanged-content no-ops, refusal without state advancement, and MCP boolean flag mapping. All 1,619 tests, Ruff and the stub check pass.
- Created one synthetic throwaway document with a heading, list, coloured/highlighted text, end-aligned paragraph and footer. Both write scopes exited 3 without mutation requests; raw structure and Drive version stayed identical. Trashed the document afterward.
- Cleared 196 inherited lint findings in a separate mechanical commit to meet the requested repository-wide check. The Drive wrapper's only cleanup is a string-literal line wrap; importer and parser behavior remain unchanged.
- Committed locally without pushing or creating a pull request.

Agent session 01a070b6-1977-7d60-81c1-44b9a866dac2 · Commits ee5995f, b8110d6, 49813ed
