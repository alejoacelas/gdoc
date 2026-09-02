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
