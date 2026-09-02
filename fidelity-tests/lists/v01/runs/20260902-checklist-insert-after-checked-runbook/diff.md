# diff — checklist-insert-after-checked-runbook

expected 3 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/para[new@18:Get added to the on-call rota ].text`
  - before: `"∅"`
  - after:  `"Get added to the on-call rota (ask Marco)⏎"`
- **expected** `tab[Tab 1]/para[new@18:Get added to the on-call rota ].bullet`
  - before: `"∅"`
  - after:  `{"listId": "kix.i11mp0ghmsa2", "textStyle": {}}`
- **expected** `tab[Tab 1]/para[new@18:Get added to the on-call rota ].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "indentFirstLine": {"magnitude": 18, "unit": "PT"}, "indentStart": {"magnitude": 36, "unit": "PT"}}`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -27,2 +27,3 @@
 - [x] ~~Read the runbook 📘 (the one in Notion, not the wiki)~~  
+- [ ] Get added to the on-call rota (ask Marco)  
 - [ ] Pair with your buddy for a week  
```
