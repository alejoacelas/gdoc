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
