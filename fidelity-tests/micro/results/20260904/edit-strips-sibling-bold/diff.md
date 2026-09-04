# diff — edit-strips-sibling-bold

expected 1 · allowed 0 · unexpected 2 (visible 2, invisible 0)

- **unexpected** `tab[Tab 1]/para[1:Ship the v2 script by Friday. ].style@"v2 script"`
  - before: `{"textStyle": {"strikethrough": true}}`
  - after:  `{"textStyle": {}}`
- **unexpected** `tab[Tab 1]/para[1:Ship the v2 script by Friday. ].style@"Estimated effort"`
  - before: `{"textStyle": {"backgroundColor": {"color": {"rgbColor": {"green": 1, "red": 1}}}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[1:Ship the v2 script by Friday. ].text`
  - before: `"3"`
  - after:  `"4"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -2,3 +2,3 @@
 
-Ship the ~~v2 script~~ by Friday. Estimated effort: 3 dev-days (was 5\)  
+Ship the v2 script by Friday. Estimated effort: 4 dev-days (was 5\)  
 Status: green  
```
