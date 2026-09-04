# diff — legal-approval-date-georgia-run

expected 1 · allowed 0 · unexpected 1 (visible 1, invisible 0)

- **expected** `tab[Tab 1]/para[40:Approved by Legal on 14 Aug, s].text`
  - before: `"14"`
  - after:  `"21"`
- **unexpected** `tab[Tab 1]/para[40:Approved by Legal on 14 Aug, s].style@" Aug, see the thread⏎"`
  - before: `{"textStyle": {"fontSize": {"magnitude": 13, "unit": "PT"}, "weightedFontFamily": {"fontFamily": "Georgia", "weight": 400}}}`
  - after:  `{"textStyle": {}}`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -57,3 +57,3 @@
 * Kubectl rollout restart deploy/api \-n staging  
-* Approved by Legal on 14 Aug, see the thread  
+* Approved by Legal on 21 Aug, see the thread  
 * Owner:	Marco    
```
