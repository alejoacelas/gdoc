# diff — acme-cost-49000

expected 2 · allowed 1 · unexpected 0 (visible 0, invisible 0)

- **allowed** (invisible) `tab[Tab 1]/table[0]/cell[1,1]/para[0:48,500⏎].paragraphStyle.avoidWidowAndOrphan`
  - before: `false`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/table[0]/cell[1,1]/para[0:48,500⏎].text`
  - before: `"8"`
  - after:  `"9"`
- **expected** `tab[Tab 1]/table[0]/cell[1,1]/para[0:48,500⏎].text`
  - before: `"5"`
  - after:  `"0"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -13,3 +13,3 @@
 | :---- | :---- | :---- | :---- |
-| Acme Cloud ☁️ | **48,500** | Sign MSA (Priya) | Aprobado ✅ |
+| Acme Cloud ☁️ | **49,000** | Sign MSA (Priya) | Aprobado ✅ |
 | Datawise Ltd | 12,95012,750  | Renew NDA (Tomás) | Pendiente: *pending legal review* |
```
