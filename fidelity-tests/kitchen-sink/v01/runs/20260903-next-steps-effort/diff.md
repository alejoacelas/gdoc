# diff — next-steps-effort

expected 1 · allowed 0 · unexpected 1 (visible 1, invisible 0)

- **unexpected** `tab[Tab 1]/para[24:Ship the v2 migration script v].style@"Estimated effort"`
  - before: `{"textStyle": {"backgroundColor": {"color": {"rgbColor": {"green": 1, "red": 1}}}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[24:Ship the v2 migration script v].text`
  - before: `"3"`
  - after:  `"4"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -41,3 +41,3 @@
 
-Ship the ~~v2 migration script~~ v3 script by Friday\[1\]. Estimated effort: 3 dev-days	(was 5\)  
+Ship the ~~v2 migration script~~ v3 script by Friday\[1\]. Estimated effort: 4 dev-days	(was 5\)  
 Status:	🟢 green	(as of 09-02)  Ana says amber 🟠, not green  
```
