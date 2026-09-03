# diff — datawise-status-approved

expected 3 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/table[0]/cell[2,3]/para[new@0:Aprobado ✅⏎].text`
  - before: `"∅"`
  - after:  `"Aprobado ✅⏎"`
- **expected** `tab[Tab 1]/table[0]/cell[2,3]/para[new@0:Aprobado ✅⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "lineSpacing": 100}`
- **expected** `tab[Tab 1]/table[0]/cell[2,3]/para[del@0:Pendiente: pending legal revie].text`
  - before: `"Pendiente: pending legal review⏎"`
  - after:  `"∅"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -14,3 +14,3 @@
 | Acme Cloud ☁️ | **49,000** | Sign MSA (Priya) | Aprobado ✅ |
-| Datawise Ltd | 12,95012,750  | Renew NDA (Tomás) | Pendiente: *pending legal review* |
+| Datawise Ltd | 12,95012,750  | Renew NDA (Tomás) | Aprobado ✅ |
 | Northwind | 9,800 | Owner TBD — shared between Ops and Finance until the Contoso decision lands | Revisión legal |
```
