# diff — rename-key-dates-fake-heading

expected 1 · allowed 0 · unexpected 2 (visible 2, invisible 0)

- **unexpected** `tab[Tab 1]/para[4:Key dates⏎].style@"Key dates"`
  - before: `{"textStyle": {"bold": true, "fontSize": {"magnitude": 14, "unit": "PT"}}}`
  - after:  `{"textStyle": {"bold": true}}`
- **expected** `tab[Tab 1]/para[4:Key dates⏎].text`
  - before: `""`
  - after:  `" and labels"`
- **unexpected** `tab[Tab 1]/para[4:Key dates⏎].style@"⏎"`
  - before: `{"textStyle": {"bold": true, "fontSize": {"magnitude": 14, "unit": "PT"}}}`
  - after:  `{"textStyle": {"bold": true}}`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -7,3 +7,3 @@
 
-**Key dates**  
+**Key dates and labels**  
 The **launch window** opens 14–18 Sept 2026, not 14-18 Sept as the v2 draft said and not 14—18 Sept as the CMS rendered it.  Legal signed off on Tuesday; Marta wants the “beta” label gone and the "beta"  badge hidden in the same release.  
```
