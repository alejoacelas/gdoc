# Tasks — gdt-text-v01

Five fields each; see the skill's Tasks section. Slugs are the run directory names. Where
twins matter the Expected field names the exact code points.

## beta-badge-straight-quotes

- **Request:** In the Key dates paragraph, the "beta" badge — the one written with straight
  quotes — is called the "preview" badge now. Marta's “beta” label stays as it is.
- **Expected:** The paragraph beginning `The launch window opens` contains `"preview"  badge`
  (U+0022 quotes, the two spaces after the closing quote kept) and still contains `“beta”
  label` (U+201C/U+201D). Every dash twin in the paragraph is unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `The launch window opens`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** the paragraph contains both `“beta”` and `"beta"` (structure).

## hyphen-date-fix

- **Request:** In the Key dates paragraph, the v2 draft's date range uses a plain hyphen
  (14-18 Sept). Make it an en dash like the first one.
- **Expected:** The paragraph reads `… not 14–18 Sept as the v2 draft said and not 14—18 Sept
  as the CMS rendered it.` — the second range now U+2013, the first (`14–18 Sept 2026`) still
  U+2013, the CMS one still U+2014. The yellow-highlighted `14–18 Sept` in the later paragraph
  is unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `The launch window opens`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** the three dash variants are present in that paragraph.

## launch-to-release-window

- **Request:** We're calling it the "release window" now, not the "launch window" — rename it
  everywhere in the doc, title included. "Launch Window banner" is a product name, leave that.
- **Expected:** `release window` appears five times with the original formatting in each
  place: in the H1 (`Northstar 2.1 release window — announcement draft (v3)`), bold, italic,
  as the link text `release window FAQ` (URL `https://example.com/northstar/faq` unchanged),
  and plain. `Launch Window banner` is unchanged. No other run styles change. Nothing else
  changes.
- **Target:** tab `Tab 1`, heading `Northstar 2.1`, paragraph beginning `The launch window
  opens`, paragraph beginning `Ana’s note`, paragraph beginning `If anything slips`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** five lower-case `launch window` runs (heading, bold, italic, link,
  plain) and one `Launch Window`.

## northstar-2-2

- **Request:** The release is now Northstar 2.2, not 2.1. Update the body copy; the title
  gets its own review so leave that.
- **Expected:** The justified paragraph begins `Northstar 2.2 is the biggest release`; the
  1.5-spacing paragraph reads `… is Northstar⍽2.2 (non-breaking space) in headlines but
  Northstar 2.2 (plain space) in body copy.` with the U+00A0 preserved in the first; `H₂O`,
  `x²`, the typed `[1]` and the footnote reference are unchanged; the four fonts of the
  justified paragraph are unchanged. The H1 still says `2.1`. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `Northstar 2.1 is the biggest`, paragraph
  beginning `The formula card`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** `Northstar⍽2.1` with U+00A0 present; the justified paragraph has four
  fonts.

## drop-old-plan

- **Request:** The struck-through "The old plan was to ship in August" bit has served its
  purpose — delete it, so the paragraph starts with the new plan.
- **Expected:** The paragraph reads `The new plan is 14–18 Sept.  This draft is internal only
  — do not forward — and read this first before editing the copy above; the dates are agreed
  with Legal.` (capital T; two spaces after `Sept.` kept). Formatting intact: yellow highlight
  on `14–18 Sept`, small caps on `internal only`, underline on `read this first ` including
  the trailing space, em dashes U+2014, line spacing 1.15. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `The old plan`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** strikethrough spans `The old plan` (bold) and ` was to ship in August`
  (plain); small caps, underline and highlight runs present in the paragraph.

## co2-formula

- **Request:** Formula card sentence: it should say CO₂, not H₂O.
- **Expected:** The paragraph beginning `The formula card` reads `… still reads CO₂ and x², …`
  with the `2` in CO₂ still subscript (baselineOffset SUBSCRIPT) and the `2` in x² still
  superscript; the typed `[1]`, the footnote reference, and `Northstar⍽2.1` (U+00A0) are
  unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `The formula card`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** `H₂O` is three runs with a subscript `2`; footnote reference present.

## signature-date

- **Request:** Bump the date in Marta's signature line to 3 Sept 2026.
- **Expected:** The right-aligned paragraph reads `— Marta, 3 Sept 2026` (U+2014, alignment
  END unchanged). The tab-only paragraph, empty H3 and empty bold paragraph after it are
  unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `— Marta`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** the paragraph has alignment END; the three empty/tab paragraphs follow.

<!-- The four tasks below were written by a second agent that read the document cold (CLI only). -->

## key-dates-en-dash-slip

- **Request:** Key dates: the launch window has slipped a day — it now opens 15–19 Sept 2026. Please change just that first sentence; leave the "v2 draft" and "CMS" examples as they are, and don't touch the old-plan paragraph further down, I'm still confirming that with Legal.
- **Expected:** The paragraph beginning `The launch window opens` now reads `The launch window opens 15–19 Sept 2026, not 14-18 Sept as the v2 draft said and not 14—18 Sept as the CMS rendered it.  Legal signed off on Tuesday; Marta wants the “beta” label gone and the "beta"  badge hidden in the same release.` The new range is `15–19` with U+2013 EN DASH. Later in the same sentence `14-18` (U+002D HYPHEN-MINUS) and `14—18` (U+2014 EM DASH) are unchanged. `launch window` at the start of the paragraph is still bold; the rest of the paragraph is plain. Elsewhere, the paragraph beginning `The old plan` still contains `new plan is 14–18 Sept` (U+2013) with its yellow background highlight — that string is not updated. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `The launch window opens`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** The `The launch window opens` paragraph contains, in order, `14–18` (U+2013), `14-18` (U+002D) and `14—18` (U+2014), with `launch window` bold and everything after it plain. The `The old plan` paragraph contains a second `14–18` (U+2013) inside the run `new plan is 14–18 Sept`, which carries a yellow background (rgb 1,1,0).

## marta-quote-tuesday-afternoon

- **Request:** In the announcement copy paragraph, Marta's Slack quote is truncated — what she actually wrote in #launch was "we finally fixed the sync bug that ate everyone's Tuesday afternoon". Can you fix the quote?
- **Expected:** In the paragraph beginning `Northstar 2.1 is the biggest release`, the quoted run now reads `as Marta put it in #launch, “we finally fixed the sync bug that ate everyone’s Tuesday afternoon” ` — the opening quote is U+201C, the closing quote U+201D, the apostrophe in `everyone’s` U+2019, and the whole run including the new word `afternoon` is Georgia 13 pt. The runs around it are unchanged: `release-notes-2.1.md` is Courier New 9 pt, underlined, blue, hyperlinked to `http://release-notes-2.1.md`; ` (more soon...) ` is Courier New 9 pt with three U+002E FULL STOP characters; `and the landing-page draft says Faster sync. Fewer surprises. More soon… ` is Times New Roman with U+2026 HORIZONTAL ELLIPSIS; the opening `Northstar 2.1 is the biggest release since 1.0: ` and the closing `(Tomás pasted that last bit from the web page, hence the fonts.)` are in the default font. The paragraph keeps JUSTIFIED alignment. `Legal signed off on Tuesday` in the Key dates paragraph is unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `Northstar 2.1 is the biggest release`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** The `Northstar 2.1 is the biggest release` paragraph has five differently formatted runs: default font; Courier New 9 pt hyperlink; Courier New 9 pt plain with `...` as three U+002E; Georgia 13 pt containing the curly-quoted Marta quote (U+201C … U+201D, apostrophe U+2019); Times New Roman containing `More soon…` (U+2026); then default font. Paragraph alignment is JUSTIFIED. The word `Tuesday` also occurs in the Key dates paragraph.

## rename-key-dates-fake-heading

- **Request:** Rename the "Key dates" subheading to "Key dates and labels" — that section now covers the beta label as well.
- **Expected:** The paragraph that read `Key dates` now reads exactly `Key dates and labels`. It is still a NORMAL_TEXT paragraph (not a Docs heading — no HEADING_n named style, no headingId), and the entire text is bold and 14 pt, matching how `Key dates` was formatted. The real heading directly above, `What we are shipping`, is still HEADING_2 with headingId `h.1x7abc6lswku` and its direct bold + underline formatting. The `Summary` paragraph above that is still NORMAL_TEXT, bold, 14 pt. The following paragraph `The launch window opens …` is unchanged, including the bold `launch window` run. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `Key dates`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** `Key dates` is a NORMAL_TEXT paragraph whose single run has direct bold + 14 pt formatting (a fake heading). `Summary` has identical formatting. `What we are shipping` is a real HEADING_2 with direct bold + underline on its text.

## tidy-double-spaces

- **Request:** There are a bunch of stray double spaces in this draft — can you tidy them up?
- **Expected:** These five in-sentence double spaces (two U+0020) become a single U+0020, with the text on either side unchanged: `rendered it.  Legal` → `rendered it. Legal` and `"beta"  badge` → `"beta" badge` (paragraph `The launch window opens`); `by design.  See also` → `by design. See also` (paragraph `Ana’s note`); `14–18 Sept.  This draft` → `14–18 Sept. This draft` (paragraph `The old plan`); `existing users?  Ana says` → `existing users? Ana says` (paragraph `Open question`). The trailing `DRAFT  ` in the `Owner:` line may be left as is or trimmed to `DRAFT`; the tabs in that line stay. Everything else is byte-identical: the U+00A0 NO-BREAK SPACE in `Northstar 2.1 (non-breaking space)` is not converted to a space; en dash / hyphen / em dash, curly and straight quotes, `...` vs `…` all survive; the `Open question` paragraph still holds the pending suggestion (inserted `maybe`, deleted `yes`, bold-italic style suggestion) with `Ana says` immediately before it and `, Marta says no.` after it, and the comment anchored on `question for Tomás` still resolves to that text across the bold/plain boundary. In `The old plan`, the strikethrough on `The old plan was to ship in August` (bold on the first three words), the yellow highlight on `new plan is 14–18 Sept`, the red `do not forward`, the underlined `read this first ` and the green highlight on `agreed with Legal` all survive. The multi-font paragraph `Northstar 2.1 is the biggest release` is untouched (it has no double spaces). Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `The launch window opens`, paragraph beginning `Ana’s note`, paragraph beginning `The old plan`, paragraph beginning `Open question`; optionally paragraph beginning `Owner:`.
- **Allowed:** revision list grows; `modifiedTime` changes; the trailing two spaces after `DRAFT` may be removed.
- **Preconditions:** Exactly the five in-sentence double spaces listed above exist, plus the trailing `DRAFT  `. The `Open question` paragraph carries one pending suggestion (`maybe` inserted / `yes` deleted, suggestion id starting `suggest.`) and the open comment whose anchor is `question for Tomás`. `Northstar 2.1 (non-breaking space)` contains U+00A0. The `The old plan` paragraph has the strikethrough, highlight, red-text and underline runs listed above.
