# diff — add-open-question

expected 3 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/para[new@18:Do we need a rollback drill be].text`
  - before: `"∅"`
  - after:  `"Do we need a rollback drill before the 15th?⏎"`
- **expected** `tab[Tab 1]/para[new@18:Do we need a rollback drill be].bullet`
  - before: `"∅"`
  - after:  `{"listId": "kix.5hgdvulx3csg", "textStyle": {}}`
- **expected** `tab[Tab 1]/para[new@18:Do we need a rollback drill be].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "indentFirstLine": {"magnitude": 18, "unit": "PT"}, "indentStart": {"magnitude": 36, "unit": "PT"}}`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -26,3 +26,4 @@
 2) 2\) do we keep the legacy read replica?     
-3) 3\) ¿quién habla con Finance? © 2026
+3) 3\) ¿quién habla con Finance? © 2026  
+4) Do we need a rollback drill before the 15th?
 
```
