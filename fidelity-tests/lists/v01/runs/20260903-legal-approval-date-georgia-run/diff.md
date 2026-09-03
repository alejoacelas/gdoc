# diff — legal-approval-date-georgia-run

expected 2 · allowed 0 · unexpected 2 (visible 2, invisible 0)

- **expected** `tab[Tab 1]/para[42:Approved by Legal on 14 Aug, s].text`
  - before: `""`
  - after:  `"2"`
- **unexpected** `tab[Tab 1]/para[42:Approved by Legal on 14 Aug, s].style@"1"`
  - before: `{"textStyle": {"fontSize": {"magnitude": 13, "unit": "PT"}, "weightedFontFamily": {"fontFamily": "Georgia", "weight": 400}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[42:Approved by Legal on 14 Aug, s].text`
  - before: `"4"`
  - after:  `""`
- **unexpected** `tab[Tab 1]/para[42:Approved by Legal on 14 Aug, s].style@" Aug, see the thread⏎"`
  - before: `{"textStyle": {"fontSize": {"magnitude": 13, "unit": "PT"}, "weightedFontFamily": {"fontFamily": "Georgia", "weight": 400}}}`
  - after:  `{"textStyle": {}}`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -59,3 +59,3 @@
 * Kubectl rollout restart deploy/api \-n staging-eu  
-* Approved by Legal on 14 Aug, see the thread  
+* Approved by Legal on 21 Aug, see the thread  
 * Owner:	Marco    
```
