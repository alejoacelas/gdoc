# diff — merged-owner-cell-interim

expected 1 · allowed 1 · unexpected 0 (visible 0, invisible 0)

- **allowed** (invisible) `tab[Tab 1]/table[0]/cell[3,2]/para[0:Owner TBD — shared between Ops].paragraphStyle.avoidWidowAndOrphan`
  - before: `false`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/table[0]/cell[3,2]/para[0:Owner TBD — shared between Ops].text`
  - before: `" TBD"`
  - after:  `": Ops (interim)"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -15,3 +15,3 @@
 | Datawise Ltd | 12,95012,750  | Renew NDA (Tomás) | Aprobado ✅ |
-| Northwind | 9,800 | Owner TBD — shared between Ops and Finance until the Contoso decision lands | Revisión legal |
+| Northwind | 9,800 | Owner: Ops (interim) — shared between Ops and Finance until the Contoso decision lands | Revisión legal |
 | Contoso Ltd | \=SUM(B2:B4) |  | Aprobado ✅ |
```
