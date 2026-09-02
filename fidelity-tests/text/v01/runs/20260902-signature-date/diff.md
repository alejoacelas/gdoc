# diff — signature-date

expected 1 · allowed 0 · unexpected 1 (visible 1, invisible 0)

- **unexpected** `tab[Tab 1]/para[13:— Marta, 2 Sept 2026⏎].paragraphStyle.alignment`
  - before: `"END"`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/para[13:— Marta, 2 Sept 2026⏎].text`
  - before: `"2"`
  - after:  `"3"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -18,3 +18,3 @@
 Ship🚀ping starts Monday; the café team in 東京 and the Москва office get the build first, and the Arabic landing page (مرحباً بنورث ستار) ships a week later.  
-— Marta, 2 Sept 2026  
+— Marta, 3 Sept 2026  
 	
```
