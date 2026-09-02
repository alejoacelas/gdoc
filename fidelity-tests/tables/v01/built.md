# gdt-tables-v01 — as built

- Built 2026-09-02 by hand in the Docs UI (Chrome, work account).
- Doc: https://docs.google.com/document/d/1qkVHvm__en97IXhioB83XK4lBKV6bvq67Aq6PcWbSYM/edit
- One document tab (`Tab 1`). Two accidental tabs were created and deleted during the build (see detours); none remain.
- Named version: `frozen` (File > Version history > Name current version). No edits after naming.
- State at freeze: mode = Editing; 1 open comment; 1 pending suggestion; 2 pages.

Legend: `[H1]/[H2]/[H3]` headings, `[N]` Normal text, `[● ]` bullet level 0, `[  ○ ]` bullet level 1,
`[L 1.]` numbered list item, `[☐]/[☑]` checklist, `⇥` tab character, `␣` trailing space, `⏎` soft line
break (shift+Return), `[chip: …]` smart chip, `**bold**`, `*italic*`. Table cells are `(row,col)` from 0.

## Exact text, top to bottom

```
[H1] Q3 ops review: vendors, hires, budget 📊
[N]  Total committed vendor spend this quarter is 48,500 GBP across three suppliers; two contracts are still pending legal review and one figure below is n/a until Northwind sends the revised quote. Numbers were pasted from the finance sheet on 28 Aug – treat them as provisional.
[N]  Vendor comparison                              <- fake heading: Normal text, bold, 14pt
[H2] Vendor comparison
[N]  Costs are per quarter, ex VAT. Status column is bilingual because the Madrid team fills it in.
[N]  (empty paragraph — the table was inserted from it)

TABLE A — vendor data table, 4 cols x 6 rows, header row pinned, row 0 bold
+---------------------------+--------------------------+----------------------------+----------------------------+
| (0,0) Vendor              | (0,1) Cost (GBP) & owner   [merged across (0,1)+(0,2)]  | (0,3) Estado · ステータス   |
+---------------------------+--------------------------+----------------------------+----------------------------+
| (1,0) Acme Cloud ☁️       | (1,1) **48,500**         | (1,2) [L 1.] Sign MSA      | (1,3) Aprobado ✅          |
|                           |                          |       (Priya)              |                            |
+---------------------------+--------------------------+----------------------------+----------------------------+
| (2,0) Datawise Ltd        | (2,1) 12,750␣            | (2,2) [L 2.] Renew NDA     | (2,3) Pendiente: *pending  |
|                           |  {SUGGESTION: replace    |       (Tomás)              |       legal review*        |
|                           |   "12,750" -> "12,950"}  |  (same list as (1,2))      |                            |
+---------------------------+--------------------------+----------------------------+----------------------------+
| (3,0) Northwind           | (3,1) n/a                | (3,2) Owner TBD — shared   | (3,3) Revisión legal       |
+---------------------------+--------------------------+   between Ops and Finance  +----------------------------+
| (4,0) Contoso Ltd         | (4,1) =SUM(B2:B4)        |   until the Contoso        | (4,3) Отклонено ❌         |
|                           |                          |   decision lands           |                            |
|                           |                          |  [merged (3,2)+(4,2)]      |                            |
|                           |                          |  {COMMENT anchored on      |                            |
|                           |                          |   "shared between Ops and  |                            |
|                           |                          |    Finance"}               |                            |
+---------------------------+--------------------------+----------------------------+----------------------------+
| (5,0) (empty)             | (5,1) (empty, bold ON)   | (5,2) (empty)              | (5,3) (empty)              |
+---------------------------+--------------------------+----------------------------+----------------------------+

[N]  Datawise is the only vendor with a signed order form; the =SUM(B2:B4) in the Contoso row is a leftover from the spreadsheet paste and was never a live formula here.
[N]  (empty paragraph — the callout was inserted from it)

TABLE B — callout, 1 col x 1 row, cell background light yellow 3 (#fff2cc), border 1pt black
+------------------------------------------------------------------------------------------------------------+
| (0,0) ⚠️ Heads-up: every Contoso number in this doc is **pending legal review** until Sarah signs off.⏎     |
|       Do not forward outside Ops; ask in #vendor-ops instead. Cap for the quarter stays at 48,500.          |
+------------------------------------------------------------------------------------------------------------+

[H2] Hiring pipeline 🧑‍💼                            <- TABLE C follows immediately, no paragraph between

TABLE C — hiring pipeline, 4 cols x 5 rows, row 0 bold, NOT pinned; row 1 on page 1, rows 2–4 on page 2
+---------------------------+--------------------------+----------------------------+----------------------------+
| (0,0) Role                | (0,1) Stage / Этап       | (0,2) Next steps           | (0,3) Owner & links        |
+---------------------------+--------------------------+----------------------------+----------------------------+
| (1,0) Senior data         | (1,1) [chip: dropdown    | (1,2) [● ] Schedule panel  | (1,3) Priya. JD on Notion  |
|       engineer            |  "Project status" preset,|       [  ○ ] Book room 4B  |  ("JD on Notion" is a link)|
|                           |  value "In progress"]    |       [  ○ ] Send take-home|                            |
+---------------------------+--------------------------+----------------------------+----------------------------+
| (2,0) Ops coordinator     | (2,1) Offer out ⏳       | (2,2) [☐] References       | (2,3) Tomás; start [chip:  |
|       (Madrid)            |                          |       [☑] Right-to-work    |  date 2 Sept 2026] (tbc)   |
|                           |                          |       (checked = struck)   |                            |
+---------------------------+--------------------------+----------------------------+----------------------------+
| (3,0) Recruiter           | (3,1) Sourcing           | (3,2) Paused until Q4, see | (3,3) [H3] Budget hold     |
|       (contract)          |                          |       budget  (3 fonts)    |                            |
+---------------------------+--------------------------+----------------------------+----------------------------+
| (4,0) Head of People      | (4,1) (empty, bold ON)   | (4,2) owner⇥stage⇥ETA      | (4,3) TBC after the Q3     |
|                           |                          |                            |       board                |
+---------------------------+--------------------------+----------------------------+----------------------------+

[N]  Sign-off block below is kept as a table so the names line up; borders were switched off on purpose.
[N]  (empty paragraph — the layout table was inserted from it)

TABLE D — layout table, 2 cols x 2 rows, table border 0pt (invisible)
+----------------------------------------------------+----------------------------------------------------+
| (0,0) Prepared by                                  | (0,1) Alejandro Acelas (Ops)                       |
+----------------------------------------------------+----------------------------------------------------+
| (1,0) Reviewed by                                  | (1,1) Sarah K. (Legal), not yet                    |
+----------------------------------------------------+----------------------------------------------------+

[N]  (empty trailing paragraph)
```

## Formatting map

Body text default: Arial 11, Normal text.

Headings and body
- `Q3 ops review: vendors, hires, budget 📊` — Heading 1.
- `Vendor comparison` (first) — Normal text, **bold**, 14pt (fake heading), directly above the real one.
- `Vendor comparison` (second) — Heading 2.
- `Hiring pipeline 🧑‍💼` — Heading 2; Table C is the very next structural element (no paragraph between).
- Intro paragraph: `48,500` plain; `pending legal review` plain; `n/a` plain; `–` is an en dash (autocorrected from `--`).

Table A (vendor comparison)
- Pinned header row: row 0 (right-click > Pin header row).
- Row 0 bold (all three cells).
- Merged: (0,1)+(0,2) horizontally, text `Cost (GBP) & owner`; (3,2)+(4,2) vertically, text `Owner TBD — shared between Ops and Finance until the Contoso decision lands` (em dash typed as `—`).
- (1,1) `48,500` bold.
- (2,1) `12,750␣` — trailing space typed after the digits. Pending suggestion replaces `12,750` with `12,950` (the trailing space was not in the selection).
- (1,2) and (2,2): one numbered list spanning two cells — `1. Sign MSA (Priya)` in (1,2), `2. Renew NDA (Tomás)` in (2,2), joined via right-click > "Continue previous numbering".
- (2,3): `Pendiente: ` plain + `pending legal review` *italic*.
- (5,*): empty row; (5,1) has bold toggled on with no text.
- Column headers contain `·` (U+00B7) and Japanese `ステータス`; cells contain `☁️ ✅ ❌`, Spanish accents (`Tomás`, `Revisión`), Cyrillic (`Отклонено`).
- Comment (open, not resolved) anchored on `shared between Ops and Finance` inside merged cell (3,2). Comment text: `Who actually owns this line? Finance says it is Ops, Ops says it went back to Finance in July.`

Table B (callout)
- 1x1, cell background light yellow 3 (#fff2cc), table border 1pt black (default).
- `pending legal review` **bold**; the rest plain. One soft line break `⏎` after `signs off.`; `48,500` plain.

Table C (hiring pipeline)
- Row 0 bold. Not pinned. Header (0,1) contains Cyrillic `Этап`.
- (1,1): dropdown chip, preset "Project status" (options Not started / Blocked / In progress / Completed), set to `In progress`. Cell has no other text.
- (1,2): bullet list, `Schedule panel` at level 0, `Book room 4B` and `Send take-home` at level 1 (hollow circle bullets).
- (1,3): `Priya. ` plain + `JD on Notion` hyperlink to `https://www.notion.so/ops/jd-senior-data-engineer`.
- (2,1): `Offer out ⏳`.
- (2,2): checklist; `References` unchecked, `Right-to-work` checked (Docs renders it struck through and grey).
- (2,3): `Tomás; start ` + date chip `2 Sept 2026` (inserted via `@today`) + ` (tbc)`.
- (3,2): three runs — `Paused` Courier New 9pt; ` until Q4, ` Arial 11pt; `see budget` Georgia 14pt.
- (3,3): `Budget hold` in Heading 3 style (inside the cell).
- (4,1): empty, bold toggled on.
- (4,2): `owner` `⇥` `stage` `⇥` `ETA` — two real tab characters in one paragraph.
- The table straddles the page break: row 1 ends page 1, rows 2–4 start page 2.

Table D (sign-off)
- 2x2, table border width 0pt (Table options > Colour > Table border > 0 pt). No other formatting.

Suggestion (pending, not accepted): in Table A (2,1), delete `12,750` insert `12,950`; author Alejandro Acelas, 22:49.
Comment (open): see Table A above; author Alejandro Acelas, 22:48.

## Autocorrections observed

- `--` typed in the intro became an en dash `–` (`28 Aug – treat them`).
- `1. ` typed at the start of cell (1,2) auto-converted into a numbered list (intended; used for the cross-cell list).
- Auto-capitalisation fired on a lowercase `x` typed at the start of a scratch body paragraph (`x` -> `X`; scratch was deleted). It did not fire on `n/a` at the start of cell (3,1) — `n/a` is stored lowercase.
- `@today` opened the smart-chip menu; Return inserted a date chip rendered `2 Sept 2026`.
- The dropdown chip inserted with default `Not started`; changed by hand to `In progress`.
- No curly-quote or list autocorrect elsewhere (no straight quotes or `- ` / `* ` prefixes were typed).

## Tried and could not do / detours

- **Tab inside a list-item cell indents the list instead of moving to the next cell.** The first fill of Table A typed everything after `1. Sign MSA (Priya)` into cell (1,2) as indented paragraphs. Selected from `Aprobado` to the end of the cell, deleted, and refilled the remaining cells by clicking into each one (bottom rows first so row-height changes did not shift targets).
- **Insert > "Tab" (Shift+F11) creates a document tab, not a tab character.** Two document tabs (`Tab 2` with `stage`, `Tab 3` with `ETA⇥TBC after the Q3 board`) were created by accident and deleted via the tab's ⋮ menu > Delete. The doc has one tab again.
- **No direct way to type a tab character inside a table cell** (Tab navigates cells; Tab at the start of an empty body paragraph indents it). Workaround: typed `x⇥y` in a body paragraph, selected just the `⇥`, copied it, pasted it twice into (4,2), then deleted the scratch text. A stray second paragraph containing only a tab ended up in (4,2) and was removed before freezing; the `A` of `ETA` was lost in that clean-up and retyped.
- Menu search (`alt+/` then "Table properties") did not visibly do anything; used Format > Table > **Table options** (the sidebar has replaced "Table properties"; the row/column/cell/colour controls live there).
- The floating "Refine" popover that appears under a selection intercepted a click, so `Paused` briefly got 14pt (reset to 9pt). Font changes were done via the toolbar font dropdown's Recent list.
- Drag-selecting a table row and pressing cmd+b did nothing; click in first cell + shift-click in last cell + cmd+b worked.
- The comment's "Comment" button moved as the box grew; first click missed, second posted it.
- The tall row 1 of Table C pushed rows 2–4 onto page 2; left as is (realistic).
- Bold-14pt fake heading: applied via the font-size box; a size dropdown stayed open and had to be dismissed with Escape.

## TRAP LIST

1. **`48,500` x3** — intro prose (plain), Table A (1,1) (**bold**), callout Table B second line (plain, after `stays at `). A replace-all `48,500` -> new figure hits all three; a per-run replacement in (1,1) is likely to drop bold or leave the trailing `\n` bold. Markdown round-trip loses which one was bold.
2. **`12,750␣` + pending suggestion** — Table A (2,1). Stored text is `12,750` + space, with a suggested deletion of `12,750` and suggested insertion `12,950`. Find `12,750` matches the doomed text; find `12,950` matches only suggested text. A naive edit either bakes the suggestion in, rejects it silently, or strips the trailing space. Export with suggestions "accepted" vs "as is" gives different cell values.
3. **`n/a` in a numeric column** — Table A (3,1), and also in the intro prose (`is n/a until Northwind`). Replace-all for the cell hits the prose too; converters that type the column as numbers coerce or drop it.
4. **`=SUM(B2:B4)` x2** — Table A (4,1) and the prose paragraph after the table. Sheets/CSV round-trips may evaluate it or prefix a quote; replace-all hits both.
5. **`pending legal review` x3 with three formats** — intro (plain), Table A (2,3) (*italic*, preceded by `Pendiente: `), callout (**bold**). Replace-all merges runs; italic/bold get lost or bleed into neighbouring text.
6. **Horizontal merge in the header** — Table A row 0 has 3 cells (`Vendor`, `Cost (GBP) & owner` colspan 2, `Estado · ステータス`) while rows 1–5 have 4. Index-based column access shifts the status header into column 2; markdown has no colspan, so exports either duplicate the header or leave an empty header column.
7. **Vertical merge with a comment inside** — Table A (3,2)+(4,2) rowspan 2, text `Owner TBD — shared between Ops and Finance until the Contoso decision lands`; row 4 has only 3 cells. Comment anchored on `shared between Ops and Finance`. Rewriting the cell text drops the anchor (comment becomes orphaned); row 4 indexing puts `Отклонено ❌` in column 2.
8. **Numbered list spanning two cells** — `1. Sign MSA (Priya)` in (1,2) and `2. Renew NDA (Tomás)` in (2,2) share one list id. Markdown re-import renders `1.` twice or restarts; replacing `Sign MSA` must keep the paragraph's bullet.
9. **Two-level bullets inside a cell** — Table C (1,2): `Schedule panel` / `Book room 4B` / `Send take-home` at levels 0/1/1. Markdown tables cannot hold lists; round-trip flattens to one line or `<br>`-joins and loses nesting.
10. **Chips mid-text** — Table C (1,1) dropdown `In progress` (a dropdown chip alone in a cell), (2,3) `Tomás; start ` + date chip `2 Sept 2026` + ` (tbc)`, (1,3) `JD on Notion` link. Text export renders chip text or nothing; find `2 Sept 2026` may not match the API body; an edit to `(tbc)` that rewrites the paragraph destroys the chip.
11. **Three fonts in one cell** — Table C (3,2): `Paused` Courier New 9 + ` until Q4, ` Arial 11 + `see budget` Georgia 14. Replacing `Paused until Q4` spans two runs; a single-style replacement inherits the first run's Courier New 9.
12. **Tabs inside a cell** — Table C (4,2) `owner⇥stage⇥ETA`. Markdown/CSV export splits on tabs or collapses them to spaces; `find "owner stage"` with a space fails.
13. **Empty bold cells and an empty row** — Table A row 5 (all empty, (5,1) bold), Table C (4,1) bold-empty. Exporters drop the empty row; API shows the bold only on the `\n` run. Round-trip silently removes row 5 and changes row indices.
14. **Fake heading above the real one** — `Vendor comparison` as bold 14pt Normal text immediately above `## Vendor comparison`. "Insert after heading Vendor comparison" or a TOC picks the wrong one; markdown round-trip either promotes the fake to `##` (duplicate headings) or demotes the real one.
15. **H3 inside a cell** — Table C (3,3) `Budget hold` (Heading 3). It appears in the outline; markdown tables cannot hold headings, so round-trip demotes it to plain text.
16. **Invisible layout table** — Table D, border 0pt. Any markdown export prints a visible 2x2 table; a tool "removing empty tables" or "finding the last table" may target it instead of Table C.
17. **Callout background + soft break** — Table B: #fff2cc background, `⏎` after `signs off.`. Markdown drops the background; the soft break becomes a paragraph break or a space, changing paragraph count in the cell.
18. **Table immediately after a heading** — `## Hiring pipeline 🧑‍💼` is followed by Table C with no paragraph. "Insert a paragraph after the heading" via index lands inside (0,0) `Role` or before the heading; the heading also carries a ZWJ-sequence emoji (`🧑‍💼`, 3 code points / 5 UTF-16 units) that shifts index math.
