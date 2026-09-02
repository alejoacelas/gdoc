# diff — ops-coordinator-start-date

expected 1 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/table[2]/cell[2,3]/para[0:Tomás; start ⟨dateElement⟩ (tb].text`
  - before: `" (tbc)"`
  - after:  `""`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -30,3 +30,3 @@
 | Senior data engineer | In progress | Schedule panel Book room 4B Send take-home | Priya. [JD on Notion](https://www.notion.so/ops/jd-senior-data-engineer) |
-| Ops coordinator (Madrid) | Offer out ⏳ | References Right-to-work | Tomás; start 2 Sept 2026 (tbc) |
+| Ops coordinator (Madrid) | Offer out ⏳ | References Right-to-work | Tomás; start 2 Sept 2026 |
 | Recruiter (contract) | Sourcing | Paused until Q4, see budget | Budget hold |
```
