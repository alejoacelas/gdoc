# diff — contoso-status-approved

expected 3 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/table[0]/cell[4,3]/para[new@0:Aprobado ✅⏎].text`
  - before: `"∅"`
  - after:  `"Aprobado ✅⏎"`
- **expected** `tab[Tab 1]/table[0]/cell[4,3]/para[new@0:Aprobado ✅⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "lineSpacing": 100}`
- **expected** `tab[Tab 1]/table[0]/cell[4,3]/para[del@0:Отклонено ❌⏎].text`
  - before: `"Отклонено ❌⏎"`
  - after:  `"∅"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -16,3 +16,3 @@
 | Northwind | n/a | Owner TBD — shared between Ops and Finance until the Contoso decision lands | Revisión legal |
-| Contoso Ltd | \=SUM(B2:B4) |  | Отклонено ❌ |
+| Contoso Ltd | \=SUM(B2:B4) |  | Aprobado ✅ |
 |  |  |  |  |
```
