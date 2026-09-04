# diff — edit-resets-alignment

expected 1 · allowed 0 · unexpected 1 (visible 1, invisible 0)

- **unexpected** `tab[Tab 1]/para[1:— Marta, 2 Sept 2026⏎].paragraphStyle.alignment`
  - before: `"END"`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/para[1:— Marta, 2 Sept 2026⏎].text`
  - before: `"2"`
  - after:  `"3"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -1,3 +1,3 @@
 Body paragraph.  
-— Marta, 2 Sept 2026  
+— Marta, 3 Sept 2026  
 Spaced paragraph with a date 2 Sept.  
```
