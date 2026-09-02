# Tasks — gdt-kitchen-sink-v01

Five fields each; see the skill's Tasks section. Slugs are the run directory names.

## budget-cloud-credits

- **Request:** In the budget table, the cloud credits line should say $12,900 now, not
  $12,400. Please update it.
- **Expected:** Table cell [1,2] reads `$12,900`. The Finance-note paragraph still reads
  `… 50,400 USD committed / 12,400 spent …` in Courier New 9pt. Nothing else changes.
- **Target:** tab `Tab 1`, table 1, cell [1,2] (row "Cloud credits (AWS -> GCP)").
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** table present with 4 rows; Finance-note paragraph contains
  `12,400` in a Courier New run; date chip present in cell [3,2].

## next-steps-effort

- **Request:** Under Next steps, the estimated effort is now 4 dev-days, not 3. Can you
  change that?
- **Expected:** The Next-steps paragraph reads `Ship the ~~v2 migration script~~ v3
  script by Friday[1]. Estimated effort: 4 dev-days⇥(was 5)` — strikethrough on `v2
  migration script` intact, literal `[1]` intact, tab intact. The Status paragraph
  below it, including its pending suggestion, is unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `Ship the`, the run `: 3 dev-days`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** strikethrough run present in the paragraph; pending suggestion
  present in the following paragraph (`suggestedInsertionIds` in structure); open
  comment on `script v3` present.

## rollout-to-launch-window

- **Request:** In the TL;DR paragraph we now call it the "launch window", not the
  "rollout window". Can you rename it there? Leave the rest of the doc alone.
- **Expected:** The TL;DR paragraph contains `launch window` three times and `rollout
  window` zero times: the first bold, the second italic red inside the curly-quoted Slack
  quote, the third still a link to `https://example.com/rollout-plan` (URL unchanged).
  The word `rollout` in `Who owns the on-call rota during the rollout?` is unchanged.
  Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `We are on track`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** the three `rollout window` runs carry bold / italic+red / link
  respectively (`structure`).

## reply-and-resolve-v3-comment

- **Request:** Someone left a comment asking whether v3 is the final name. Reply to it
  with "Yes, v3 is final — Tomás confirmed on 1 Sept." and mark it resolved.
- **Expected:** The comment anchored on `script v3` has one reply with exactly that text
  and `resolved: true`. Its anchor and quoted text are unchanged. The document body is
  byte-identical (`structure` diff empty; the pending suggestion still pending).
- **Target:** comment (id `AAACGeHZ4dE` in the fixture; a new id in the copy).
- **Allowed:** comment `modifiedTime` changes; revision list grows.
- **Preconditions:** the open comment with `quotedFileContent` `script v3` exists in the
  copy (`gdoc comments --all`); pending suggestion present.

## footnote-v8

- **Request:** The footnote at the bottom still says Finance sheet v7 pulled 28 Aug by
  Tomás. It's v8 now, pulled 2 Sept by Priya. Please fix the footnote.
- **Expected:** The footnote reads `Finance sheet v8, tab “Q3”, pulled 2 Sept by Priya.`
  (curly quotes intact). The Appendix paragraph and its footnote reference are unchanged;
  the `Finance sheet` link in the table and the `Finance sheet` text in the Appendix
  paragraph are unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, footnote `kix.sodj60jamoog`, paragraph beginning
  `Finance sheet v7`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** footnote present with text `Finance sheet v7, tab “Q3”, pulled 28
  Aug by Tomás.`; `Finance sheet` link present in table cell [3,1].

## fix-double-numbering

- **Request:** In Tomás's open-questions list, items 2 and 3 show their number twice
  ("2) 2)", "3) 3)"). Remove the typed duplicates so the list just reads 1) 2) 3).
- **Expected:** The two list items read `do we keep the legacy read replica?   ` (three
  trailing spaces kept) and `¿quién habla con Finance? © 2026`, still bulleted in list
  `kix.5hgdvulx3csg` with glyph `%0)`, still nesting level 0. Item 1 and every other
  list in the document are unchanged (the `1.`–`5.` list, the checklist, the table's
  nested bullets). Nothing else changes.
- **Target:** tab `Tab 1`, paragraph beginning `2) do we keep` and paragraph beginning
  `3) ¿quién habla`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** both paragraphs start with the literal typed `2) ` / `3) ` inside
  real `%0)` list items (`structure`).

## add-open-question

- **Request:** Add one more open question at the end of Tomás's list: "Do we need a
  rollback drill before the 15th?"
- **Expected:** A new fourth item in list `kix.5hgdvulx3csg` (glyph `%0)`, nesting 0)
  directly after `3) ¿quién habla con Finance? © 2026`, reading `Do we need a rollback
  drill before the 15th?` in default text style. The `Budget 💰 / Presupuesto Q3` heading
  and the empty paragraph before the table are unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, new paragraph `Do we need a rollback drill`.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** the `%0)` list has exactly three items; the Budget heading follows it.
