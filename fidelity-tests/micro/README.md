# micro — the fast loop

`bin/gdt micro cases/` seeds a minimal Google Doc through the Docs API (about two seconds, no
browser, no copy), runs **one** gdoc command on it, captures before and after, and judges with
the same `gdt-diff` and Target/Allowed rules as the full suite. Six cases run in about ten
seconds in parallel. Use it to reproduce an issue in the smallest document that shows it, to
try a fix, and to sweep variations (fonts, positions, list types) that would take an hour each
in the browser-built fixtures.

What it cannot do: comments and suggestions (the Docs API cannot create them), chips, drawings,
and anything the visual judge is for (a chip's rendering, a suggestion's colour). Those stay in
the browser-built fixtures.

## Case file

`cases/<name>.json`, see the docstring at the top of `bin/gdt-micro` for every seed key:
`text` with `bold/italic/strike/underline/color/highlight/link` ranges, `font`, `style`
(heading), `align`, `spacing`, `indent`, `bullets`/`numbered`, `table`, `footnote`. `command`
is a gdoc command with `{DOC}` and `{A}` placeholders (wrap shell pipelines in `sh -c "…"`);
`target` and `allowed` use the locator language from `references/diff.md`.

## Results

`results/<YYYYMMDD>/<name>/` holds `before/`, `after/`, `command.txt`, `diff.md`, `result.json`.
Outcomes: `DONE` (expected items only), `COLLATERAL` (any unexpected item), `NO-CHANGE (exit n)`
(command made no change; read `command.txt`), `UNJUDGED` (changed but the Target matched
nothing — fix the locator). Seed docs land in the Drive folder `micro` under the suite root
(`micro/folder.txt`) and are cheap to delete in bulk.

## First run (2026-09-04, gdoc 0.21.0)

| case | issue | outcome |
|---|---|---|
| edit-strips-sibling-bold | #57 | COLLATERAL — strikethrough and highlight elsewhere in the paragraph gone |
| edit-across-font-boundary | | COLLATERAL — Courier New 10pt flattened |
| edit-resets-alignment | | COLLATERAL — right alignment lost |
| edit-list-marker-restyles | #57 | COLLATERAL — `1. …` inside the replacement turned the paragraph into a numbered list |
| edit-footnote-text | | NO-CHANGE (exit 3) — `edit` cannot see footnote text |
| write-tab-inherits-bullet | #59 | COLLATERAL — rewritten tab's paragraphs carry the old list's bullet |

Every finding of the two-night browser suite reproduces in a document of two or three
paragraphs.
