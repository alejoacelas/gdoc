# diff — data-engineer-owner-handover

expected 1 · allowed 1 · unexpected 0 (visible 0, invisible 0)

- **allowed** (invisible) `tab[Tab 1]/table[2]/cell[1,3]/para[0:Priya. JD on Notion⏎].paragraphStyle.avoidWidowAndOrphan`
  - before: `false`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/table[2]/cell[1,3]/para[0:Priya. JD on Notion⏎].text`
  - before: `"Priya"`
  - after:  `"Tomás"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -29,3 +29,3 @@
 | :---- | :---- | :---- | :---- |
-| Senior data engineer | In progress | Schedule panel Book room 4B Send take-home | Priya. [JD on Notion](https://www.notion.so/ops/jd-senior-data-engineer) |
+| Senior data engineer | In progress | Schedule panel Book room 4B Send take-home | Tomás. [JD on Notion](https://www.notion.so/ops/jd-senior-data-engineer) |
 | Ops coordinator (Madrid) | Offer out ⏳ | References Right-to-work | Tomás; start 2 Sept 2026 |
```
