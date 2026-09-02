# Known gdoc behaviours that affect fidelity runs

Each entry links to a repro line or an issue. Delete entries that have neither, and
entries whose issue is closed once a rerun confirms the fix.

| Behaviour | Evidence |
|---|---|
| `gdoc edit` parses the replacement as markdown: a leading `1. ` or `# ` restyles the whole paragraph; `_word_` becomes italic. Use `--old-file/--new-file`. | [LucaDeLeo/gdoc#57](https://github.com/LucaDeLeo/gdoc/issues/57) |
| `gdoc edit` rewrites the whole paragraph's runs, so strikethrough, highlight, bold, italic, colour, font and size elsewhere in the paragraph are lost — even 25 characters outside the match, and across a font boundary. Reproduced on the command track in four fixtures. | `fidelity-tests/repros.md#kitchen-sink-v01-edit-strips-paragraph-styles`, `#kitchen-sink-v01-edit-all-strips-run-styles`, `#lists-v01-edit-across-font-boundary-flattens-run` |
| `gdoc edit` also resets paragraph-level style: alignment, line spacing, indent, and the HEADING named style (`--all` demoted an H1 to Normal text). | `fidelity-tests/repros.md#text-v01-edit-resets-paragraph-style`, `#text-v01-edit-all-demotes-heading` |
| `gdoc edit` cannot find text inside footnotes (`no match found` although `cat` prints it). | `fidelity-tests/repros.md#kitchen-sink-v01-edit-cannot-reach-footnote` |
| Markdown bullets in a replacement join the nearest list at the level implied by the paragraph's indent; leading spaces are ignored and multi-level blocks leave literal tabs. No way to choose a list or nesting level. | `fidelity-tests/repros.md#lists-v01-markdown-bullet-ignores-nesting` |
| No command deletes a table row, sets a font size, highlight or colour, or ticks a checklist item (the last is an API limit). | verdicts: tables remove-empty-vendor-row (GAP-CLI), text rename-key-dates-fake-heading, lists tick-pair-with-buddy (DECLINED-API) |
| `gdoc comments --json` has no `anchor` field, so anchor moves are invisible to tooling. | `fidelity-tests/CORRECTIONS.md` (anchor blindness) |
| `gdoc edit --cell` replaces the whole cell paragraph (del/new pair in the diff); fine for one-line cells. | tables verdicts northwind-quote, datawise-status-approved |
| `gdoc cp` (Drive `files.copy`) drops comments and pending suggestions. | `fidelity-tests/CORRECTIONS.md`; kitchen-sink INVALID run |
| `gdoc write` from markdown misplaces paragraph styles after emoji and other non-BMP characters; looks like Python length versus UTF-16 index arithmetic. | needs repro |
| `gdoc cat` refuses `--tab` with `--comments`; use `gdoc comments --all`. | needs repro |
| Revision export ignores `--tab`. | needs repro |

Operational, not defects:

- The default account may not see the fixtures; always pass `--account` from
  `config.yaml`.
