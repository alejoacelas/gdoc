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
| write-tab-inherits-bullet | #59 | COLLATERAL — when the old tab ended in a bulleted paragraph, every rewritten paragraph (title included) carries that bullet; without the terminal bullet the rewrite is clean apart from blank spacer paragraphs |

Every finding of the two-night browser suite reproduces in a document of two or three
paragraphs.

## Preview API for comments and suggestions (tested 2026-09-04)

Direct calls with gdoc's stored credentials and the plain `build("docs", "v1")` client work; the
"preview" is an enrolment flag on the Cloud project, not a different endpoint. The generated
client does not know the new fields, but the server accepts them:

- Pending suggestion: `documents.batchUpdate` with the normal `deleteContentRange` +
  `insertText` requests plus `"writeControl": {"requiredRevisionId": <rev>, "writeMode":
  "SUGGEST"}`. The response returns `createdSuggestionIds`. Read back with
  `suggestionsViewMode=SUGGESTIONS_INLINE`.
- Anchored comment: `documents.batchUpdate` with `{"insertComment": {"content": …, "range":
  {"startIndex", "endIndex"}}}`; the response carries `commentId` (same id Drive returns) and
  `anchorId`; `documents.get` with `commentsViewMode=COMMENTS_VIEW_MODE_INCLUDED` (needs an
  `AuthorizedSession` GET, the generated client rejects the unknown query parameter) returns
  `commentAnchors`. Drive `comments.create` with a hand-built anchor only stores a string; the
  comment is unanchored in the UI.
- No request exists to accept or reject a suggestion or to resolve a comment through the Docs
  API; only the read mode `PREVIEW_SUGGESTIONS_ACCEPTED`.
- Gotcha, and a candidate micro case: `insertComment` ranges are interpreted in the
  SUGGESTIONS_INLINE index space. An anchor computed from a default-view read of a document
  that already holds suggestions lands in the wrong place. Check whether `gdoc comment --quote`
  has this problem.

Consequences for the campaign: seeds can carry anchored comments and pending suggestions, so
the sweep covers "edit next to / under a comment anchor", "edit inside / next to a pending
suggestion", and comment anchors become visible to the structural judge (read the document with
`commentsViewMode` and diff `commentAnchors`), which removes the blind spot the browser suite had.

## Scripted browser captures

Use `bin/gdt-shot-headless` from `fidelity-tests/` to replace the Chrome-extension
shooter. It runs normal Google Chrome off-screen, with Playwright over CDP and a
separate profile at `~/.config/gdt-chrome`. It never shares or edits a document.

Install Google Chrome and `uv`; for PDF comparisons, install Poppler (`brew install
poppler`). The executable installs its pinned Playwright dependency through `uv` on
first use; no Playwright browser download is needed. This launcher targets macOS's
`/Applications/Google Chrome.app`.

```bash
bin/gdt-shot-headless 'DOC_URL' /tmp/my-capture
bin/gdt-shot-headless 'DOC_URL?tab=t.TAB_ID' /tmp/my-tab-capture --views 3
```

On first use, the script opens Chrome and prints a login instruction. Sign in as
`alejandro.acelas-contractor@80000hours.org`, leave Chrome sync off, and leave the
Doc open. The script waits for the human login, then continues. Sessions stay in
that profile; neither credentials nor cookies belong in the repository. Port 9224
must be free or belong to that dedicated Chrome. Close only the dedicated profile
if Chrome reports a profile lock; then rerun the command.

- Captures use a fixed 1440×828 CSS viewport, 100% Docs zoom, print layout, collapsed
  outlines and hidden comment cards/panel. Chrome is asked for a 1440×1200 window;
  macOS may clamp the outer height. Actual geometry is recorded.
- The editor scrolls to 0, 650, 1300, … until its bottom is visible. `--views N`
  requests exactly N views, retaining repeated bottom views when Chrome clamps
  the offset. Use the same count for before/after comparisons.
- `gdt-shot` files `view-01.jpg`, `view-02.jpg`, … and the existing `shot.json`.
  `capture.json` adds actual geometry, requested/actual offsets and timings. An
  existing capture is refused; use a fresh output directory. A failed capture
  never publishes `shot.json`.
- Capture documents sequentially. Keep the dedicated window untouched while it
  runs. Documents open elsewhere may show collaborator cursors in the image.
  Authentication errors, access denial and changed UI selectors fail visibly.
- `--cold-cache` clears only the dedicated browser's HTTP cache before navigation
  for a first-load measurement. Cookies and login remain. The default reuses cache.

The [benchmark and browser/PDF comparison](shots-benchmark.md) includes the five
painted review copies and all six micro cases. Reproduce it from this directory,
using a new output path:

```bash
python3 benchmark-shots.py --out /tmp/gdt-benchmark-new
./compare-shots.py /tmp/gdt-benchmark-new
```

The benchmark only reads the URLs in `../REVIEW.md` and the six dated result files;
PDF exports explicitly select the work account. Local scrolling and filing tests
visit no Google documents:

```bash
uv run --with playwright==1.62.0 --with pytest pytest ../tests/test_shot_headless.py
```
