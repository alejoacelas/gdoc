# diff — fill-empty-vendor-row

expected 12 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/table[0]/cell[5,0]/para[new@0:Globex⏎].text`
  - before: `"∅"`
  - after:  `"Globex⏎"`
- **expected** `tab[Tab 1]/table[0]/cell[5,0]/para[new@0:Globex⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "lineSpacing": 100}`
- **expected** `tab[Tab 1]/table[0]/cell[5,0]/para[del@0:⏎].text`
  - before: `"⏎"`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/table[0]/cell[5,1]/para[new@0:3,200⏎].text`
  - before: `"∅"`
  - after:  `"3,200⏎"`
- **expected** `tab[Tab 1]/table[0]/cell[5,1]/para[new@0:3,200⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "lineSpacing": 100}`
- **expected** `tab[Tab 1]/table[0]/cell[5,1]/para[del@0:⏎].text`
  - before: `"⏎"`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/table[0]/cell[5,2]/para[new@0:Sign SOW (Priya)⏎].text`
  - before: `"∅"`
  - after:  `"Sign SOW (Priya)⏎"`
- **expected** `tab[Tab 1]/table[0]/cell[5,2]/para[new@0:Sign SOW (Priya)⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "lineSpacing": 100}`
- **expected** `tab[Tab 1]/table[0]/cell[5,2]/para[del@0:⏎].text`
  - before: `"⏎"`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/table[0]/cell[5,3]/para[new@0:Aprobado ✅⏎].text`
  - before: `"∅"`
  - after:  `"Aprobado ✅⏎"`
- **expected** `tab[Tab 1]/table[0]/cell[5,3]/para[new@0:Aprobado ✅⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "lineSpacing": 100}`
- **expected** `tab[Tab 1]/table[0]/cell[5,3]/para[del@0:⏎].text`
  - before: `"⏎"`
  - after:  `"∅"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -17,3 +17,3 @@
 | Contoso Ltd | \=SUM(B2:B4) |  | Отклонено ❌ |
-|  |  |  |  |
+| Globex | 3,200 | Sign SOW (Priya) | Aprobado ✅ |
 
```
