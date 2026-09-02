# gdt-text-v01 — as built

Built by hand in the browser on 2026-09-02, work account
(alejandro.acelas-contractor@80000hours.org), single tab ("Tab 1"). Named version
**`frozen`** (see "Frozen revision" below). Two pages: page 1 ends after the two empty
formatted paragraphs, page 2 holds only the "Open items" section. One open comment, one
pending suggestion (two suggestion records), one footnote. Editing mode was restored before
freezing.

Doc: https://docs.google.com/document/d/1zU7pmkVdMCQEfJYSZ5-fTvoXUMWGtTuAcFyXNRqFZfU/edit

Indices below are UTF-16 offsets from `gdoc structure --suggestions-view-mode
suggestions_inline` taken just before naming the version. Named styles are the Docs
defaults (Arial; Normal 11pt, H1 20pt, H2 16pt, H3 14pt). Nothing was pasted — every
"pasted" run was typed and then given its font/size by hand.

## Exact text, top to bottom

`⇥` = a real tab character. `␣` = a trailing space. `⍽` = U+00A0 no-break space. Double
spaces inside a line are shown as two real spaces and listed under "Spacing" below.
Paragraph kinds: `[H1]`/`[H2]`/`[H3]` named heading styles; `[N]` Normal text; suffixes
give paragraph-level formatting.

```
[H1]            Northstar 2.1 launch window — announcement draft (v3)
[N]             Owner:⇥Marta Kowalczyk⇥Status:⇥DRAFT␣␣
[N bold 14pt]   Summary                                       ← fake heading, directly above real H2
[H2]            What we are shipping                          ← real H2, text also bold+underline (direct)
[N bold 14pt]   Key dates                                     ← fake heading, directly below real H2
[N]             The launch window opens 14–18 Sept 2026, not 14-18 Sept as the v2 draft said and not 14—18 Sept as the CMS rendered it.  Legal signed off on Tuesday; Marta wants the “beta” label gone and the "beta"  badge hidden in the same release.
[N]             Ana’s note: the launch window is not the same thing as the Launch Window banner in the app; the banner string lives in the release checklist and is owned by design.  See also the launch window FAQ before replying to customers.
[N]             If anything slips, the launch window moves as a whole; we do not ship half the features. Live status: https://status.example.com/northstar (updated hourly).
[H2]            Copy for the announcement
[N justified]   Northstar 2.1 is the biggest release since 1.0: release-notes-2.1.md (more soon...) as Marta put it in #launch, “we finally fixed the sync bug that ate everyone’s Tuesday” and the landing-page draft says Faster sync. Fewer surprises. More soon… (Tomás pasted that last bit from the web page, hence the fonts.)
[N 1.5 spacing] The formula card still reads H₂O and x², the old deck typed its footnote marker as [1] instead of using a real footnote¹, and the style rule is Northstar⍽2.1 (non-breaking space) in headlines but Northstar 2.1 (plain space) in body copy.
[N 1.15 expl.]  The old plan was to ship in August; the new plan is 14–18 Sept.  This draft is internal only — do not forward — and read this first before editing the copy above; the dates are agreed with Legal.
[N 1.15 expl.]  Ship🚀ping starts Monday; the café team in 東京 and the Москва office get the build first, and the Arabic landing page (مرحباً بنورث ستار) ships a week later.
[N right]       — Marta, 2 Sept 2026
[N]             ⇥                                             ← paragraph that is only a tab
[H3]                                                          ← empty Heading 3
[N bold 14pt]                                                 ← empty paragraph, newline carries bold + 14pt
[H2]            Open items                                    ← first paragraph on page 2
[N]             Feature⇥Owner⇥ETA
[N]             ⇥Sync v2⇥Tomás⇥14 Sept
[N]             ⇥Beta badge⇥Ana⇥TBD␣
[N indent 36pt] Open question for Tomás: do we keep the beta badge for existing users?  Ana says yes, Marta says no.     ← comment on "question for Tomás"; pending suggestion yes→maybe
[FOOTNOTE 1]    Deck v7, slide 12, exported 28 Aug by Ana.   ← footnote body starts with a leading space
```

### Twin pairs — exact characters

| Twin | Side A | Side B (and C) |
|---|---|---|
| Quotes around `beta` (para "The launch window opens…", idx 133–367) | `“beta”` = U+201C … U+201D (1st, autocorrected) | `"beta"` = U+0022 … U+0022 (2nd, kept straight via undo-the-autocorrect) |
| Date range dash (same para) | `14–18 Sept 2026` = U+2013 EN DASH | `14-18 Sept` = U+002D HYPHEN-MINUS; `14—18 Sept` = U+2014 EM DASH |
| Second en dash | `new plan is 14–18 Sept` (idx 1365–1387, yellow highlight) = U+2013 | — |
| Ellipsis (justified para, idx 777–1087) | `More soon…` = U+2026 (Times New Roman run) | `(more soon...)` = three U+002E (Courier New 9pt run) |
| No-break space (1.5-spacing para) | `Northstar⍽2.1 (non-breaking space)` = U+00A0 | `Northstar 2.1 (plain space)` = U+0020; the H1 and the justified para also use U+0020 |
| Case twin | `launch window` ×5 (lower case) | `Launch Window` ×1 (idx ~426–439, plain text, "the Launch Window banner") |
| Apostrophes | `Ana’s`, `everyone’s` = U+2019 (autocorrected / typed) | none straight |
| Em dashes typed as such | H1 `—`; `internal only — do not forward — and`; signature `— Marta` = U+2014 | |
| Accent | `café` = `e` + U+0301 COMBINING ACUTE (decomposed) | `Tomás` ×3 = precomposed U+00E1 |

### Spacing details

- Two spaces after a full stop: `rendered it.  Legal` (idx 133–367); `by design.  See also` (367–594);
  `14–18 Sept.  This draft` (1325–1521); `existing users?  Ana says` (1777–1883).
- Accidental double space mid-sentence: `"beta"  badge` (two U+0020 after the straight closing quote).
- Trailing spaces: `DRAFT␣␣` (two, idx 92–94); `TBD␣` (one, idx 1775–1776).
- Tabs: `Owner:⇥…⇥Status:⇥` (three tabs); tab-only paragraph idx 1700–1702; `Feature⇥Owner⇥ETA`;
  two lines that *start* with a tab (`⇥Sync v2…`, `⇥Beta badge…`).

## Formatting map

Run-level (UTF-16 indices from `structure`):

| Where | Text | Formatting |
|---|---|---|
| 1–55 | H1 text | HEADING_1, no direct style; contains "launch window" (placement 4: **heading**) |
| 94–102 | `Summary` | NORMAL_TEXT + direct **bold, 14pt** — directly above the real H2 |
| 102–123 | `What we are shipping` | HEADING_2 + direct **bold + underline** on the whole text |
| 123–133 | `Key dates` | NORMAL_TEXT + direct **bold, 14pt** — directly below the real H2 |
| 137–150 | `launch window` | **bold** (placement 1) |
| 383–396 | `launch window` | *italic* (placement 2) |
| 490–507 | `release checklist` | link → `https://example.com/northstar/checklist`, default link colour #1155cc + underline; split into two runs: `release ` (490–498, link only) and `checklist` (498–507, link + **bold**) — bold applied after linking |
| 546–563 | `launch window FAQ` | link → `https://example.com/northstar/faq` (placement 3: **inside a link**; visible text ≠ URL) |
| 616–629 | `launch window` | plain (placement 5: **plain text**) |
| 696–732 | `https://status.example.com/northstar` | bare URL auto-linked by Docs on the following space |
| 777–1087 | whole paragraph | alignment JUSTIFIED. Four fonts, three sizes: 777–825 Arial 11 (default); 825–845 `release-notes-2.1.md` Courier New 9 **and auto-linked to `http://release-notes-2.1.md`** (Docs treated `.md` as a TLD); 845–861 ` (more soon...) ` Courier New 9; 861–949 Slack quote Georgia 13; 949–1022 web copy Times New Roman 11; 1022–1087 Arial 11 |
| 1087–1325 | whole paragraph | lineSpacing 150 (1.5). 1117–1118 `2` SUBSCRIPT (H₂O); 1125–1126 `2` SUPERSCRIPT (x²); 1201–1204 typed `[1]` plain; **footnote reference at 1206–1207** (`kix.dy0afxbtah37`, number 1), i.e. `real footnote¹,`; NBSP at 1240 inside `Northstar⍽2.1` |
| 1325–1337 | `The old plan` | **bold + strikethrough** |
| 1337–1359 | ` was to ship in August` | strikethrough only → strikethrough spans the bold/plain boundary at 1337 |
| 1365–1387 | `new plan is 14–18 Sept` | highlight (background) yellow rgb(1,1,0) |
| 1404–1417 | `internal only` | **small caps** (renders INTERNAL ONLY; stored lower case) |
| 1420–1434 | `do not forward` | text colour red rgb(1,0,0) |
| 1441–1457 | `read this first ` | underline **including the trailing space** |
| 1502–1519 | `agreed with Legal` | highlight (background) green rgb(0,1,0) |
| 1325–1702 | four paragraphs | explicit lineSpacing 115 (the default made explicit, from resetting after the 1.5 paragraph) |
| 1521–1679 | international para | `Ship🚀ping` (emoji U+1F680 mid-word = 2 code units); `café` with U+0301; `東京`; `Москва`; Arabic `مرحباً بنورث ستار` (includes U+064B fathatan) in a paragraph whose base direction stays LTR |
| 1679–1700 | `— Marta, 2 Sept 2026` | alignment END (right-aligned via Format > Align) |
| 1700–1702 | `⇥` | paragraph containing only a tab |
| 1702–1703 | (empty) | HEADING_3 with no text |
| 1703–1704 | (empty) | NORMAL_TEXT whose newline carries **bold + 14pt** |
| 1777–1790 | `Open question` | **bold**; paragraph indentStart 36pt + indentFirstLine 36pt (one Increase indent) |
| 1785–1803 | `question for Tomás` | **comment anchor** — starts inside the bold run (`question`) and ends in plain text (` for Tomás`) |
| 1858–1866 | `maybe` / `yes` | **pending suggestion**: `maybe` (1858–1863) suggested insertion, `yes` (1863–1866) suggested deletion, both `suggest.p6habqssdsab`; plus a text-style suggestion `suggest.u3q9mxhek3a0` (bold + italic + font) on the same span. Accepted result: `Ana says ***maybe***, Marta says no.` |

Comment (Drive comments API id `AAACGebRK78`, open, author Alejandro Acelas, 23:34):
"Anchor deliberately spans the bold/plain boundary. Still unresolved as of 2 Sept - Tomás
to decide by Friday." (the ` - ` in the comment is a plain hyphen; the comment box did not
autocorrect it).

Footnote 1 body (footnote `kix.dy0afxbtah37`): ` Deck v7, slide 12, exported 28 Aug by Ana.`
— Docs inserts a leading space before footnote text.

## Autocorrections observed

- Straight `"beta"` typed normally → `“beta”` (U+201C/U+201D). Straight quotes were kept
  on the second twin by typing `"` and pressing cmd+z immediately: the undo reverts only the
  smart-quote substitution and leaves U+0022. Same trick recovered `...`.
- `Ana's` → `Ana’s` (U+2019).
- `...` → `…` (U+2026) **even inside a Courier New run** — code font does not suppress it.
  Reverted with cmd+z; the three dots survived.
- `14-18` between digits stayed a hyphen. Typed `–`, `—`, `“ ”`, `’`, `…`, U+00A0 and
  U+0301 all landed as the literal characters (no normalisation; NBSP did not need the
  Special characters dialog; `e`+U+0301 was not composed to `é`).
- `https://status.example.com/northstar` auto-linked on the trailing space.
- `release-notes-2.1.md` auto-linked to `http://release-notes-2.1.md` on the trailing
  space — an accidental trap worth keeping.
- No unwanted capitalisation or list conversion occurred (no line started with `1. ` or `-`).
- Not Docs but the exporter: `gdoc cat` writes `\#launch` and `\[1\]`.

## Tried and could not do / detours

- Enter in the link dialog did not apply the link (dialog stayed open; stray keys landed in
  the URL field harmlessly). Clicking **Apply** works.
- Style leakage: after selecting text and toggling bold (or strikethrough) and then pressing
  ArrowRight, subsequent typing inherited that style. Fixed by re-selecting 56 chars (bold)
  and 45 chars (strikethrough) and toggling off. Side effect kept as mess: the double space
  in `"beta"  badge`.
- First suggestion attempt selected `es,` (off by one). Rejected both of my own suggestion
  cards with their X buttons and redid it; rejected suggestions leave no trace in the API.
- Applying bold+italic to the selection in Suggesting mode before typing produced two
  records (a replace and a separate "Format: bold, font, italic") rather than one — Docs
  shows them as two cards.
- Resetting the paragraph after the 1.5 one via the line-spacing menu wrote explicit
  `lineSpacing: 115` on the next four paragraphs.
- Small caps exists in this Docs build (menu search "Small caps", Option+Shift+K) — no
  detour needed. Superscript/subscript via cmd+. / cmd+, (the tool rejects `cmd+period`).
- `gdoc` default account had no access; `--account alejandro.acelas-contractor@80000hours.org`
  needed. `gdoc cat --comments` lists the comment as `[UNANCHORED] … [anchor deleted]`
  even though the anchor is intact in the UI — a CLI finding, not a doc defect.
- The tool's `type` action inserts Unicode directly, so Insert > Special characters was
  never used.

## TRAP LIST

1. **`launch window` ×5 + `Launch Window`.** Placements: H1 (1–55), bold (137–150), italic
   (383–396), inside link text `launch window FAQ` (546–563), plain (616–629); case variant
   `Launch Window` in "the Launch Window banner" (367–594). A case-insensitive replace-all
   changes the banner name and the heading; a per-run replace loses the bold/italic; a
   markdown round trip must keep `[launch window FAQ](…)` intact.
2. **`“beta”` vs `"beta"`** (U+201C/U+201D vs U+0022, same paragraph, 133–367). Replacing
   `"beta"` typed with straight quotes should match only the second; a smart-quote
   normaliser on export/import silently merges them. The straight one is followed by two
   spaces (`"beta"  badge`).
3. **`14–18` / `14-18` / `14—18` Sept** (U+2013 / U+002D / U+2014) in one paragraph, plus a
   second `14–18 Sept` at 1365–1387 that is yellow-highlighted. Replacing "14-18" must hit
   exactly one; editing the highlighted one must keep the background colour.
4. **`(more soon...)` vs `More soon…`** (three U+002E in Courier New 9 vs U+2026 in Times New
   Roman) inside the justified four-font paragraph (777–1087). The three-dot run sits right
   after `release-notes-2.1.md`, which Docs auto-linked to `http://release-notes-2.1.md`; a
   markdown round trip may convert `...` to `…`, drop the bogus link, or collapse fonts.
5. **`Northstar⍽2.1` vs `Northstar 2.1`** (U+00A0 vs U+0020; 1 NBSP occurrence at ~1240 vs 3
   plain: H1, 777–825, 1207–1325). Replace "Northstar 2.1" → "Northstar 2.2" should miss the
   NBSP one; markdown export may normalise NBSP to a space and then "fix" it.
6. **Split link `release checklist`** (490–507): `release ` plain link + `checklist` bold link,
   same URL. Editing "checklist" or re-bolding may produce two link runs, drop the bold, or
   drop the link on one half; markdown form is `[release **checklist**](url)`.
7. **Strikethrough across a bold boundary**: `~~**The old plan** was to ship in August~~`
   (1325–1359). Markdown round trip reorders nesting (`**~~…~~** ~~…~~`) and can move the
   space in/out of the struck run; a replace of "old plan" should keep both strike and bold.
8. **Underline with trailing space** `read this first ` (1441–1457) and small caps
   `internal only` (1404–1417). Markdown has no syntax for either: export lowercases the
   small caps and drops the underline, so round-tripping the paragraph loses both and the
   trailing-space boundary. Searching for "INTERNAL ONLY" finds nothing.
9. **`H₂O`, `x²`, typed `[1]` next to a real footnote¹** (1087–1325). The `2`s are separate
   one-char runs with baselineOffset; plain-text search for "H2O" matches across the run
   boundary and a naive replace flattens the subscript. `[1]` (typed, 1201–1204) sits two
   words before the footnote reference at 1206–1207; markdown shows `\[1\]` and `[^1]`.
10. **`Ship🚀ping` and `café` (e + U+0301)** (1521–1679). The emoji is two UTF-16 code units
    (index arithmetic off by one for everything after it); `café` with a precomposed é will
    not match the decomposed one, while `Tomás` elsewhere is precomposed. RTL Arabic in the
    same paragraph: any insertion after `(` risks landing on the wrong visual side.
11. **Fake vs real headings and empty formatted paragraphs.** `Summary`/`Key dates` are bold
    14pt Normal text hugging the real H2 `What we are shipping`, whose text is also
    bold+underlined by direct formatting. Between the signature and `Open items` sit a
    tab-only paragraph, an empty H3 and an empty paragraph whose newline is bold+14pt. A
    markdown round trip turns `Summary` into a heading or the H2 into `## **…**`, and
    collapses the three empty/tab paragraphs into blank lines.
12. **Comment anchor across bold→plain and pending suggestion in the same paragraph**
    (1777–1883, indented 36pt). Comment `AAACGebRK78` anchors `question for Tomás`; the
    suggestion replaces `yes` (1863–1866, suggested deletion) with bold+italic `maybe`
    (1858–1863, suggested insertion). A text replace of "yes" or "Ana says" either edits a
    suggested-deletion run, accepts the suggestion implicitly, or shifts the comment anchor;
    `gdoc cat` already shows the merged `***maybeyes***`.

## Frozen revision

Named version **`frozen`** = Drive revision **66** (2026-09-02 23:36 local, 22:36:01Z),
Docs `revisionId`
`ANLCKQm8oF40UqP4tfn0oYLXW5ND-rhL464DYdekaJCqHeBMChO8zeckTEOL2FJpmwTDd2zsUYuYoxWtzptDN9fqvzYGIcpXdsF4VxM6--g`
(identical before and after naming — naming a version creates no new revision). Drive's
`revisions.list` does not expose the Docs version name; `keepForever` stays false. Retained
revisions at freeze time: 1 and 3 (21:38, blank doc) and 66 (this build). Comments API id
`AAACGebRK78`; suggestion ids `suggest.p6habqssdsab` (replace) and `suggest.u3q9mxhek3a0`
(style). Browser tab left open on the doc.
