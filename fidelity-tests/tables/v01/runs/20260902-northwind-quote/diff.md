# diff — northwind-quote

expected 3 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/table[0]/cell[3,1]/para[new@0:9,800⏎].text`
  - before: `"∅"`
  - after:  `"9,800⏎"`
- **expected** `tab[Tab 1]/table[0]/cell[3,1]/para[new@0:9,800⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "lineSpacing": 100}`
- **expected** `tab[Tab 1]/table[0]/cell[3,1]/para[del@0:n/a⏎].text`
  - before: `"n/a⏎"`
  - after:  `"∅"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -15,3 +15,3 @@
 | Datawise Ltd | 12,750  | Renew NDA (Tomás) | Pendiente: *pending legal review* |
-| Northwind | n/a | Owner TBD — shared between Ops and Finance until the Contoso decision lands | Revisión legal |
+| Northwind | 9,800 | Owner TBD — shared between Ops and Finance until the Contoso decision lands | Revisión legal |
 | Contoso Ltd | \=SUM(B2:B4) |  | Отклонено ❌ |
```
