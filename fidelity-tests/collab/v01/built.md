# gdt-collab-v01 — as built

- Built: 2026-09-03 (browser, by hand; comment/suggestion timestamps show 00:17–00:27 local)
- Doc: https://docs.google.com/document/d/16-VPn1wWF0ZmyWtlF8JbAq8qxJlfgiT71GNfjPcs00w/edit
- Owner: alejandro.acelas-contractor@80000hours.org (all comments, replies and suggestions are by this account)
- Tabs: one (`Tab 1`)
- Named version: `frozen` (named last; no edits after naming)
- Mode when frozen: Editing
- Docs margin badge at freeze: 19 = 7 open anchored comments + 12 pending suggestions

## Exact text top to bottom

One line per paragraph, prefixed with the paragraph kind. `{+…+}` = pending suggested insertion,
`{-…-}` = pending suggested deletion, `[[…]]#n` = comment anchor n (see table). `{¶-}` marks the
pending suggested deletion of a paragraph break (paragraph merge).

```
TITLE     Home office stipend policy: draft for review
NORMAL    Status: draft v3, owner: People Ops. Comments welcome until Thursday. Please leave feedback in comments rather than editing directly.
H1        Why we are changing the stipend 🏠
NORMAL    The current stipend was set in 2021 and has not moved since. Rent, energy prices {-and equipment costs-} have all risen, and the finance team has asked us to make the scheme easier to audit. This draft tries to do both things at once without adding paperwork for anyone.{¶-}
NORMAL    We want the scheme to be simple to administer. Most of the complaints we heard were not about the amount but about the claim process, which currently involves four forms and a spreadsheet that only Priya can edit.
NORMAL*   [[What changes]]#6                                   (* bold, 14pt, Normal style — fake heading)
H2        Eligibility and amounts
NORMAL    [[Everyone on a permanent contract who works from home at least two days a week is eligible. Contractors are not eligible under this draft, though see the open question below. The annual amount rises from £300 to £450, paid in two instalments, and unspent balance does not roll over.]]#1
NORMAL    Claims go through the expenses portal (see the finance [[handbook]]#2) rather than the old form.
H2        What you can claim{+ (and what you can’t)+}
BULLET    A desk, chair or monitor arm, up to the full annual amount
BULLET    Monitors, keyboards and other peripherals
BULLET    A share of your broadband bill, [[capped at {+£25+}{-£15-} a month]]#3
BULLET    Ergonomic assessments booked through the People Ops calendar
BULLET    {+Noise-cancelling headphones, one pair every three years+}      (whole list item is a suggested insertion)
NORMAL    Items must be for work use. We are not going to police this closely, but if you claim a gaming chair we will ask questions.   ("work use" carries a pending suggested formatting change: bold)
H2        Instalments and timing
TABLE     3x3, no header styling:
  R1      Instalment | Paid | Covers
  R2      First | April payroll | April to September{+ inclusive+}
  R3      Second | [[October payroll]]#4 | October to March
NORMAL    If you join mid-year you get a pro-rated share of the current instalment, [[rounded {+down+}{-up-} to the nearest]]#5 £10. Leavers do not need to {+return+}{-repay-} anything {-already -}claimed. The two-instalment structure is meant to keep the scheme simple to administer for payroll.
H2        Open questions
NORMAL    Should contractors be eligible? Legal thinks it blurs the employment status line; the engineering leads think excluding them is unfair since half the platform team are contractors.{+ People Ops has no strong view either way.+}
NORMAL    We also need to decide whether the scheme should stay simple to [[administer or track]]#8 receipts per category.
NORMAL    Next review: {+June+}{-March-}. Owner: People Ops. Send questions to the #people-ops channel.
```

Notes on the text:
- Paragraph "We want the scheme…" originally read "three forms"; changed to "four forms" in Editing mode
  AFTER comment #7 on "three forms" was resolved.
- Paragraph "We also need to decide…" originally ended " Finance prefers receipts." — that sentence
  (plus its leading space) was deleted in Editing mode after comment #9 was anchored to it, so #9 is orphaned.
- "Thursday" was "Friday": suggested replacement, then ACCEPTED (now plain text).
- "complaints" was suggested → "grumbles", then REJECTED (now plain text, unchanged).

## Comments

| # | Anchored text (at creation) | State | Comment text | Replies |
|---|---|---|---|---|
| 1 | whole paragraph "Everyone on a permanent contract … does not roll over." | open | This paragraph does three jobs (who, how much, when it expires). Split eligibility and amounts into two paragraphs? | — |
| 2 | "handbook" (single word inside the link "finance handbook") | open | This links to the old handbook. The expenses page moved to Notion in June; link should point there. | — |
| 3 | "capped at £15 a month" (inside bullet 3) | open | £15 is below the cheapest fibre plan in most of the UK. Where did this number come from? | (1) Checked three providers: cheapest fibre I can find is about £24 a month. (2) Proposing £25 in a suggestion below. Will loop in finance if nobody objects by Friday. |
| 4 | "October payroll" (table R3C2) | open | Payroll cutoff is the 15th, so anyone who claims after that gets paid in November. Say so here or move the date. | — |
| 5 | "rounded up to the nearest" | open; now overlapped by suggestion "up"→"down" | Rounding up is generous and finance usually rounds the other way. Check before this goes out. | — |
| 6 | "What changes" (bold 14pt fake heading, whole paragraph) | open | This is bold Normal text pretending to be a heading, so it never shows in the outline. Make it a real Heading 2? | — |
| 7 | "three forms" | RESOLVED, then anchored text edited to "four forms" in Editing mode | Is it really three? Priya says the equipment form was retired last year. | — |
| 8 | "administer or track" (starts inside bold-italic run "simple to administer", ends in plain text) | open | Is tracking receipts realistic? One person handles all expenses and she is already behind. | — |
| 9 | "Finance prefers receipts." | ORPHANED (anchored text deleted entirely in Editing mode; card no longer shown in margin) | Do they? Last I heard finance wanted fewer receipts, not more. Who said this? | — |

Open and visible in margin: 1, 2, 3, 4, 5, 6, 8 (7 cards). API `comments.list` should return 9 (7 open-anchored,
1 resolved, 1 open-but-orphaned).

## Suggestions

All made in Suggesting mode by the owner account. Docs card label in the last column.

| # | Kind | Location | Before → after | State | Card label |
|---|---|---|---|---|---|
| S1 | insertion | end of "Should contractors be eligible?…" paragraph | "…are contractors." → "…are contractors. People Ops has no strong view either way." | pending | Add: "People Ops has no strong view either way." |
| S2 | replacement | "Next review: March." paragraph | March → June | pending | Replace: "March" with "June" |
| S3 | replacement (overlaps comment #5) | "rounded up to the nearest £10" | up → down | pending | Replace: "up" with "down" |
| S4 | deletion | "Leavers do not need to repay anything already claimed." | delete "already " | pending | Delete: "already " |
| S5 | replacement (same sentence as S4, two words apart) | same sentence | repay → return | pending | Replace: "repay" with "return" |
| S6 | insertion in table cell | R2C3 "April to September" | → "April to September inclusive" | pending | Add: "inclusive" |
| S7 | formatting | "work use" in "Items must be for work use." | plain → bold | pending | Format: bold, font (Docs lists "font" as well, unprompted) |
| S8 | replacement (overlaps comment #3, inside a list item) | bullet 3 "capped at £15 a month" | £15 → £25 | pending | Add: "£25" (deletion of "£15" shown struck through) |
| S9 | new list item | after bullet 4 (Return at end of "…People Ops calendar") | new bullet "Noise-cancelling headphones, one pair every three years" | pending | Add: "Noise-cancelling headphones, one pair every three years" |
| S10 | deletion of several words | "Rent, energy prices and equipment costs have all risen" | delete "and equipment costs" | pending | Delete: "and equipment costs" |
| S11 | replacement | status line "Comments welcome until Friday." | Friday → Thursday | ACCEPTED (via ✓) | — |
| S12 | replacement | "Most of the complaints we heard" | complaints → grumbles | REJECTED (via ✗) | — |
| S13 | insertion inside a heading | H2 "What you can claim" | → "What you can claim (and what you can’t)" | pending | Add: "(and what you can’t)" |
| S14 | paragraph merge (deleted paragraph break) | between "…paperwork for anyone." and "We want the scheme…" | two Normal paragraphs → one | pending | Delete paragraph |

Pending count: 12 (S1–S10, S13, S14).

## Formatting map (body mess)

- Line 1 is the built-in **Title** style (not a heading level).
- H1 "Why we are changing the stipend 🏠" ends with the U+1F3E0 emoji (typed as text; rendered fine).
- "What changes": **Normal text**, bold, 14pt (set via toolbar +/- from 11) — sits directly above the real H2 "Eligibility and amounts". Comment #6 on it.
- "finance handbook": link to `https://handbook.example.org/finance/expenses`; comment #2 covers only "handbook".
- "simple to administer" appears 3 times with different formatting:
  1. plain — "We want the scheme to be simple to administer." (para under H1)
  2. underline + red text (palette red, #ff0000) — "…keep the scheme simple to administer for payroll." (para under the table)
  3. bold + italic — "…should stay simple to administer or track…" (Open questions). Comment #8 starts inside this run.
- "People Ops" appears 4 times: status line, bullet 4 ("People Ops calendar"), "Owner: People Ops", and inside pending suggested insertion S1.
- One bulleted list (4 real items + 1 suggested item S9). One 3x3 table, default borders, no header row styling.
- Two pages: the page break falls after the table paragraph ("…for payroll."), before H2 "Open questions".

## Autocorrections observed

- Straight apostrophe in `can't` (typed in Suggesting mode into the H2) became a curly `’` (U+2019): the doc has "can’t".
- Nothing else fired: "£" characters, the emoji, "#people-ops", "mid-year", "pro-rated", "two-instalment", "Noise-cancelling" all stayed as typed. No smart-quote pairs (none typed), no dash substitution (none typed), no capitalisation changes.

## Tried and could not do / detours

- First comment: after typing a long comment the "Comment" button moved down as the box grew, so my click missed and the draft stayed open; I posted it with a second click. From then on I submitted with cmd+Return, which works for both comments and replies.
- Second reply on comment #3: typing while the reply box had lost focus went nowhere (nothing entered the doc). Re-clicked the reply field and posted it with the "Reply" button.
- Selecting "simple to administer" for the red underline: a scroll shift made the first double-click land on " administer for"; I undid the one underline (cmd+z) and re-selected. Undo did not touch anything else.
- Word-extension selection (alt+shift+Right) stopped before "£10", so comment #5 anchors "rounded up to the nearest" rather than "…nearest £10".
- The orphaned comment (#9) disappears from the margin entirely as soon as its text is deleted; it is not shown as "orphaned" in the UI. Only the API/"All comments" panel will still list it.
- Docs labelled the bold-only formatting suggestion as "Format: bold, font" — it appears to record a font property change too; did not investigate.
- Did not try: a comment on the emoji itself, a suggestion that crosses a table-cell boundary, or a suggested list-level (indent) change.

## TRAP LIST

1. **"four forms"** (para "We want the scheme…", between "involves " and " and a spreadsheet"). Resolved comment #7 still holds `quotedFileContent` "three forms". An API edit that touches this paragraph (replaceAllText "four"→"three", or rewriting the sentence) will most likely re-orphan or double-orphan the resolved comment; a tool that locates comments by quoted text will not find "three forms" anywhere.
2. **"rounded {+down+}{-up-} to the nearest"** (para under the table). Comment #5 anchor with pending suggestion S3 inside it. Any API text change in this range (e.g. replacing "nearest £10" or inserting after "rounded") is likely to silently accept or discard S3, and the deleteContentRange indices differ depending on suggestionsViewMode — off-by-"up" errors will orphan #5.
3. **"capped at {+£25+}{-£15-} a month"** (bullet 3). Comment #3 has a two-reply thread and overlapping suggestion S8. replaceAllText("£15", …) matches text that is suggested-deleted; a naïve edit either mangles the suggestion or orphans #3 and loses the reply thread's visible anchor.
4. **"administer or track"** (Open questions). Comment #8 starts inside the bold-italic run "simple to administer" and ends in plain text. Reformatting that run (e.g. "make all three 'simple to administer' consistent") via updateTextStyle, or replacing the phrase, splits the anchor across new runs — anchor likely orphaned.
5. **"simple to administer" ×3** (plain / red-underlined / bold-italic). replaceAllText hits all three; the bold-italic one carries comment #8. Also a tool that "normalises formatting" will remove the deliberate red underline on occurrence 2.
6. **"People Ops" ×4, one inside pending insertion S1** ("People Ops has no strong view either way."). replaceAllText("People Ops", "People Operations") reports 4 (or 3) matches depending on view mode and may modify text inside a pending suggestion, partially accepting it.
7. **"What changes"** (bold 14pt Normal, comment #6). "Make this a real Heading 2" via updateParagraphStyle leaves the bold/14pt inline overrides (heading renders bold 14pt, not H2's 16pt regular); deleting and retyping it orphans #6.
8. **Table R2C3 "April to September{+ inclusive+}" / R3C2 "[[October payroll]]#4"**. Any table structure edit (insert row/column, change cell text via deleteContentRange) shifts indices past the pending insertion S6 and risks orphaning #4 or silently accepting S6.
9. **Suggested bullet "Noise-cancelling headphones, one pair every three years"** (S9, last item of the list). "Add a bullet at the end of the list" via API will land before/after a paragraph that exists only as a suggestion; the new bullet may inherit suggestion state, or the tool may count 4 list items vs 5.
10. **Paragraph merge S14** between "…paperwork for anyone." and "We want the scheme…". The paragraph break exists but is suggested-deleted. Inserting at the start of "We want…" or applying a paragraph style to either paragraph may accept the merge or apply the style to both; index math differs by ±1 per view mode.
11. **"finance [[handbook]]#2"** link. Updating the URL over the full link range is fine, but replacing "handbook" (e.g. → "wiki") orphans #2 and the inserted text may not carry the link. The link text is not the URL, so tools matching on URL text will not find it.
12. **Orphaned comment #9 "Finance prefers receipts."** No anchor in the body. comments.list returns it as unresolved; a tool that tries to locate every open comment will fail on this one, and counts will disagree with the UI (7 visible vs 8 unresolved in the API). Also the heading "What you can claim{+ (and what you can’t)+}" (S13): heading text differs between suggestion view modes and contains a curly apostrophe, so searches for "can't" (straight) miss it.
