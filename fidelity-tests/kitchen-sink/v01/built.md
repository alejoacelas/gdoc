# gdt-kitchen-sink-v01 — as built

Built by hand in the browser on 2026-09-02, work account, single tab ("Tab 1").
Named version **"frozen"** = revision 44 (21:14), Docs `revisionId`
`ANLCKQm_ccZ7BeHd5JVvuMWEjSFC1IHLVmeoClWphpb5xdEIOzee9kLHN47r2hYgvl7ax7t40fiKW-QYCGBfjQpRfNrwDgF1T1ulySb1NAM`.
Two pages; the table ends page 1, "Finance note…" opens page 2. One open comment, one
pending suggestion, one footnote. Editing mode was restored before freezing.

Indices below are UTF-16 offsets from `gdoc structure` at the frozen revision. Named
styles are the Docs defaults (Arial; Normal 11pt, H1 20pt, H2 16pt, H3 14pt bold-ish grey).

## Exact text, top to bottom

`⇥` = a real tab character. `␣` marks trailing spaces. Blank lines that carry formatting
are called out.

```
[H1]   🚀 Q3 platform migration — status & notes (更新 v3)
[N]    Owner:⇥Priya N.⇥last edit: 2 Sep 2026␣␣␣
[N]    Summary                                   ← bold 14pt Normal text, fake heading
[H2]   TL;DR ✅
[N]    We are on track for the rollout window of 15-19 Sept. infra sign-off is done; the data team still owes us the backfill numbers – see the budget table below. Priya wrote in Slack “don’t touch the rollout window without asking me first”, so the rollout window is frozen until the Monday sync.
[H2]   Meeting notes — 28 Aug 🗓️ (Zoom)
[L1 1.] Confirm DNS cutover owner (Tomás)
[L1 2.] Freeze schema changes after 12 Sept 🧊
[L1 3.] Draft partner comms -> Español y 日本語 versions
[CK ☐]   Book the war room for 15 Sept (Ana)            ← checklist, indented 72pt
[CK ☐]   ✅ rotate the API keys before cutover           ← checklist, indented 72pt
[N]    (Ana, later: the numbering above got mangled when Tomás pasted from Notion, don’t bother fixing it.)
[L1 4.] Retro on 22 Sept, bring 🍰                       ← same list as items 1–3 (continued)
[L1 5.] Decommission old cluster (wait 30 days)
[N]    Open questions (Tomás’s list, pasted from email):
[L2 1)] Who owns the on-call rota during the rollout?
[L2 2)] 2) do we keep the legacy read replica?␣␣␣        ← literal "2) " typed inside a real "2)" item
[L2 3)] 3) ¿quién habla con Finance? © 2026              ← literal "3) " typed inside a real "3)" item
[H2]   Budget 💰 / Presupuesto Q3
[N]    (empty paragraph, index 994–995, no formatting)
[TABLE 4x3]
  | Line item 📦          | Owner / 責任者                          | Q3 spend (USD)      |   ← all three bold
  | Cloud credits (AWS -> GCP) | Tomás                              | $12,400             |
  | Contractors           | • Ana (data)                            | $38,000 (est.)      |
  |                       |     ○ Backfill 🔁                       |                     |
  |                       |     ○ QA / Качество                     |                     |
  | Vendor licences       | See Finance sheet (ask Priya)           | TBD ⚠️ [2 Sept 2026]|   ← link; date chip
[N]    Finance note (pasted from Slack by Priya): Q3 actuals: 50,400 USD committed / 12,400 spent as of 08-28 – pls confirm the contractor number before we send it to the board 🙏 (Alejo: i think the 38k is inflated, see comment.)
[N]    (empty paragraph, index 1437–1438, carries bold + 14pt)
[H3]   次のステップ 🔜 Next steps
[N]    Ship the v2 migration script v3 script by Friday[1]. Estimated effort: 3 dev-days⇥(was 5)
[N]    Status:⇥🟢 green⇥(as of 09-02)␣␣Ana says amber 🟠, not green     ← "Ana says…green" is a pending suggestion
[N, centered] – end of notes –
[N]    (empty paragraph, index 1627–1628)
[N]    ―――― horizontal rule ――――
[N]    Appendix: numbers come from the Finance sheet¹
[FOOTNOTE 1] Finance sheet v7, tab “Q3”, pulled 28 Aug by Tomás.
```

Characters to be careful with: the H1/H2 dashes are em dashes (U+2014, typed as such);
the dashes in the TL;DR paragraph, the Finance note and "– end of notes –" are en dashes
(U+2013, produced by autocorrect from `--`). All quotes are curly. `->` stayed literal
both times. `©` came from typing `(c)`.

## Formatting map

Run-level (indices are UTF-16, from `structure`):

| Where | Text | Formatting |
|---|---|---|
| 92–100 | `Summary` | Normal text, **bold, 14pt** — sits directly above real H2 `TL;DR ✅` |
| 132–146 | `rollout window` (1st) | bold |
| 303–317 | `rollout window` (2nd, inside the curly-quoted Slack quote) | italic, red `#ff0000` |
| 351–365 | `rollout window` (3rd) | link → `https://example.com/rollout-plan` (default blue underline) |
| 998–1040 | table header row | bold, all three cells |
| 1176–1189 | `Finance sheet` (table cell r4c2) | link → `https://docs.google.com/spreadsheets/d/1FAKEfinanceSheet000/edit` (stayed a plain link, did not become a chip — the sheet does not exist) |
| 1210–1211 | table cell r4c3, after `TBD ⚠️ ` | **date smart chip** `dateElement`, displayText `2 Sept 2026`, locale en-GB, one code unit |
| 1256–1315 | `Q3 actuals: … as of 08-28` | **Courier New 9pt** |
| 1315–1386 | ` – pls confirm … board 🙏 ` | **Georgia 13pt** |
| 1386–1437 | `(Alejo: i think … see comment.)` | Arial 11 (default) — three fonts/sizes in one paragraph |
| 1437–1438 | empty paragraph | bold + 14pt on the newline only |
| 1468–1487 | `v2 migration script` | strikethrough |
| 1507–1510 | `[1]` | superscript (typed text, not a footnote) |
| 1512–1528 | `Estimated effort` | yellow highlight `#ffff00` |
| 1549–1581 | `Status:⇥🟢 green⇥(as of 09-02)␣␣` | two tab chars, two trailing spaces before the suggestion |
| 1581–1609 | `Ana says amber 🟠, not green` | **pending suggested insertion** (two runs, split at the emoji), by Alejandro Acelas |
| 1610–1627 | `– end of notes –` | paragraph alignment CENTER |
| 1628–1629 | — | horizontal rule element |
| 1675–1676 | after `Finance sheet` | footnoteReference → footnote `kix.sodj60jamoog` |

Paragraph/structure level:

- Headings: H1 (1), H2 (3: TL;DR, Meeting notes, Budget), H3 (1, Japanese + emoji). The
  outline in the left panel shows all five plus nothing for "Summary".
- Lists (four list objects):
  - `kix.lmi7a3gh5v4z` DECIMAL `%0.` — items 1–3 **and** 4–5. Same listId; the plain
    paragraph "(Ana, later: …)" and two checklist items sit between them. Produced with
    right-click → "Continue previous numbering".
  - `kix.bqp2axw8ev2s` checklist (GLYPH_TYPE_UNSPECIFIED, checkbox glyphs) — the two
    "Book the war room" / "✅ rotate" items. `indentStart` 72pt (one level deeper than the
    numbered items at 36pt) but `nestingLevel` 0. Both unchecked.
  - `kix.5hgdvulx3csg` DECIMAL `%0)` — the "Open questions" list, created by Docs
    autoformat when I typed `1) `. Items 2 and 3 contain a second literal `2) ` / `3) `.
  - `kix.hjn7uzy4hlb1` bullets `●/○` — inside table cell r3c2, levels 0 and 1.
- Table: 4 rows × 3 columns, default borders, no header-row flag, indices 995–1213.
  Nested list in r3c2, link in r4c2, date chip in r4c3. The paragraph before the table
  (994–995) is empty.
- Tabs used for alignment in two paragraphs (`Owner:⇥Priya N.⇥…` and
  `Status:⇥🟢 green⇥…`) plus one mid-paragraph tab before `(was 5)`.
- Trailing spaces: 3 after `2 Sep 2026`, 3 after `read replica?`, 2 after `(as of 09-02)`
  (immediately before the suggestion), 1 after `board 🙏` inside the Georgia run.
- Comment (open, id `AAACGeHZ4dE`): "Is v3 actually the final name? Tomás called it v2.1
  in the standup." Anchored on **`script v3`** (1481–1490) — `script` is the tail of the
  strikethrough run, ` v3` is plain text, so the anchor straddles a formatting boundary.
- Suggestion (pending): insertion of `Ana says amber 🟠, not green` at 1581. Mode was
  switched back to Editing afterwards. `gdoc cat` renders the suggestion inline as if
  accepted; `structure` without `--suggestions-view-mode` may hide or show it.
- Footnote: one, `kix.sodj60jamoog`, text `Finance sheet v7, tab “Q3”, pulled 28 Aug by Tomás.`
- Page break is natural (no explicit break); it falls after the table.

## Autocorrections observed

- `--` → `–` (en dash) three times: TL;DR paragraph, Finance note, `-- end of notes --`.
  Note it is an en dash, not an em dash; the heading em dashes were typed directly.
- Straight `"…"` → curly `“…”` (TL;DR quote, footnote `“Q3”`); `'` in `don't`, `Tomás's`
  → `’`.
- `(c)` → `©` in `¿quién habla con Finance? (c) 2026`.
- First letter capitalised at paragraph/list-item start: `confirm` → `Confirm`,
  `book the war room` → `Book…`, `who owns` → `Who owns`, `see Finance sheet` → `See…`,
  `backfill 🔁` → `Backfill 🔁` (inside a nested bullet in a table cell).
- **Not** capitalised: `infra sign-off` after `Sept. ` (mid-paragraph, after an
  abbreviation), `last edit:` after a tab, `i think` (lone `i` left lowercase),
  `rotate` after the leading `✅ ` in a checklist item.
- `1) ` at line start → converted to a real `%0)` numbered list. Subsequent `2) ` / `3) `
  typed inside the auto-created items were left as literal text, so the doc shows
  `2) 2) do we…` and `3) 3) ¿quién…`.
- `->` was **not** converted to an arrow (both occurrences literal).
- `@today` opened the smart-chip picker; picking "Today's date" produced a date chip.
- `"2) "` inside an existing list item did not restart or renumber anything.
- Spelling underline appeared under `do we` (blue squiggle in the UI only; not in the API).

## Tried and could not do / detours

- **Checklist halfway through a list**: `cmd+shift+9` (and `cmd+shift+7`) apply to the
  *whole* list, not the selected items — the first attempt turned all five items into
  checkboxes. Workaround: Backspace at the start of items 4–5 to pop them out of the list,
  then apply checklist to those two paragraphs. Side effect: they kept the list indent, so
  the checklist sits at 72pt instead of 36pt. Kept as-is (realistic mess).
- **Link dialog**: pressing Return right after typing the URL sometimes did nothing (the
  suggestions list was still loading); clicking Apply worked. First attempt on the third
  `rollout window` silently failed and had to be redone.
- **Sheets link → chip**: a Sheets URL to a non-existent sheet stays a plain hyperlink; no
  file chip. Did not want to link a real internal sheet.
- **Person chip / @-mention**: skipped — inserting one would email or notify a colleague.
- **Right alignment**: avoided `cmd+shift+r` (Chrome hard-reload risk); used centre
  (`cmd+shift+e`) instead. No right-aligned paragraph in the doc.
- **Font changes** via the toolbar dropdown were awkward; `alt+/` menu search
  ("Courier New", "Georgia", "Arial", "Horizontal line", "Name current version") worked
  reliably and is the method used.
- **Browser session**: mid-task the extension's tab group vanished (Chrome reported no tab
  group); reopened the doc in a fresh tab and continued. No content was lost (autosave).
- Not attempted: images/drawings, headers/footers, page breaks, columns, equations,
  merged table cells, table header-row flag, bookmarks, a second tab (forbidden).

## TRAP LIST — where an API find-and-replace or write is most likely to do collateral damage

Each entry: exact target text, what surrounds it, and what is likely to break.

1. **`rollout window`** (3 occurrences, TL;DR paragraph). Formatted bold / italic-red /
   linked. A replace-all that rewrites the run text will flatten all three to the style of
   the first run it touches, or drop the link on the third. Target for a "rename the
   rollout window to launch window" task.
2. **`Summary`** (bold 14pt Normal, index 92–100) directly above **`TL;DR ✅`** (real H2).
   A tool that treats "bold, larger than body" as a heading, or a markdown round-trip, will
   either promote `Summary` to a heading or demote/duplicate `TL;DR ✅`. Also a trap for
   "insert a paragraph after the first heading".
3. **`script v3`** (comment anchor, 1481–1490, spans strikethrough → plain). Replacing
   `v2 migration script` or `v3 script` shifts or orphans the comment anchor; a write that
   rebuilds the paragraph loses the anchor entirely and the comment becomes unanchored.
4. **`Ana says amber 🟠, not green`** (pending suggestion, 1581–1609). `cat` shows it as
   if accepted. A write from that markdown silently accepts the suggestion; an edit that
   targets `(as of 09-02)` right before it may land inside the suggestion or delete the
   two trailing spaces the suggestion is attached to.
5. **`2 Sept 2026`** (date chip, r4c3, index 1210, one code unit). The visible text does
   not exist as text; a find for `TBD ⚠️ 2 Sept 2026` will not match, and any
   character-offset arithmetic done in Python (emoji `⚠️` is 2 code units + VS16) lands
   one or more code units off. Writes that rebuild the cell drop the chip.
6. **`Finance sheet`** — appears three times: as a link in table cell r4c2
   (1176–1189), as plain text in `Appendix: numbers come from the Finance sheet` (body),
   and inside the footnote (`Finance sheet v7`). A replace-all for `Finance sheet` will
   hit the footnote and the link text; a careless one strips the hyperlink.
7. **`Backfill 🔁` / `QA / Качество`** (nested bullets inside table cell r3c2, list
   `kix.hjn7uzy4hlb1`, levels 0/1). Markdown export flattens them to
   `Ana (data) Backfill 🔁 QA / Качество`; a write-back turns the cell into one run with no
   list. Also the `backfill` lowercase in the TL;DR paragraph (`the backfill numbers`) is a
   false-positive match for a case-insensitive replace.
8. **Items `4. Retro on 22 Sept…` and `5. Decommission…`** share listId
   `kix.lmi7a3gh5v4z` with items 1–3 across an interrupting paragraph and a checklist.
   Deleting or replacing the `(Ana, later: …)` paragraph, or converting the checklist,
   can renumber these to 1–2 or merge the checklist into the numbered list.
9. **`2) do we keep the legacy read replica?   `** and **`3) ¿quién habla con Finance? © 2026`**
   — literal `2) `/`3) ` inside real `%0)` list items. A "fix the double numbering" task
   tempts a replace of `2) ` that also matches the glyph-less start of… nothing (the real
   glyph is not text), but a naive regex `^\d\) ` on exported markdown hits the auto glyph
   line and removes the *real* list. Also three trailing spaces after `replica?`.
10. **`Q3 actuals: 50,400 USD committed / 12,400 spent as of 08-28`** (Courier New 9pt),
    followed by Georgia 13pt then Arial 11pt in the same paragraph. Replacing `12,400`
    (which also appears as `$12,400` in the table, r2c3) hits both; rebuilding the
    paragraph from `cat` output loses all three fonts and sizes.
11. **`Owner:⇥Priya N.⇥last edit: 2 Sep 2026   `** and
    **`Status:⇥🟢 green⇥(as of 09-02)  `** — tab characters and trailing spaces.
    Markdown round-trips normalise tabs to spaces and strip trailing whitespace, so a
    write "changes nothing" yet diffs. `2 Sep 2026` (text) vs `2 Sept 2026` (chip) is a
    near-duplicate trap for a date-update task.
12. **Empty paragraph at 1437–1438 (bold 14pt)** and **empty paragraph before the table
    (994–995)**. Tools that "clean up blank lines" or insert content "before the
    Next steps heading" will land in, or delete, the formatted empty paragraph; text
    inserted there inherits bold 14pt and looks like another fake heading.

Bonus: the heading text `次のステップ 🔜 Next steps` and `Budget 💰 / Presupuesto Q3`
contain emoji whose UTF-16 length (2 code units) breaks offset math for anything inserted
after them; `更新` in the H1 does not (BMP characters), which makes the bug intermittent.
