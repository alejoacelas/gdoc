# diff — budget-cloud-credits

expected 1 · allowed 1 · unexpected 0 (visible 0, invisible 0)

- **allowed** (invisible) `tab[Tab 1]/table[0]/cell[1,2]/para[0:$12,400⏎].paragraphStyle.avoidWidowAndOrphan`
  - before: `false`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/table[0]/cell[1,2]/para[0:$12,400⏎].text`
  - before: `"4"`
  - after:  `"9"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -32,3 +32,3 @@
 | :---- | :---- | :---- |
-| Cloud credits (AWS \-\> GCP) | Tomás | $12,400 |
+| Cloud credits (AWS \-\> GCP) | Tomás | $12,900 |
 | Contractors | Ana (data) Backfill 🔁 QA / Качество | $38,000 (est.) |
```
