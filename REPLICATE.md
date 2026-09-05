# Search and replace document segments

The user wanted a local, test-first change that lets `edit` and `suggest` replace
text in the selected tab's body, headers, footers, and footnotes.

- Added failing tests with invented text and exact batch request assertions, then
  retained segment and tab coordinates through search, replacement, and suggestion
  overlap checks. Body-only request shapes remain unchanged.
- Kept each container's indices independent, limited default searches to the first
  tab, and rejected structural Markdown in non-body replacements before mutation.
- Verified 1,608 passing tests, a clean `uv run ruff check gdoc/ tests/`, and a passing
  `bash scripts/check-no-stubs.sh`. Existing lint violations required a separate
  mechanical cleanup commit.
- Created one throwaway two-tab document. One revision-pinned edit batch replaced
  three tokens in the first tab's body, header, and footnote; raw read-back confirmed
  correct segment ranges, unchanged segment text and paragraph styles, and an
  unchanged sibling tab. Trashed the document afterward.
- Kept all commits local for a separate agent to push and open the pull request.

Agent session 01a070b6-0f7c-7880-967e-5cd4a8d0b6b5 · Commits 6776467, 5e2827a,
cbcd4e5, 21c443f, dd083e2, f60e735
