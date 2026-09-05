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
