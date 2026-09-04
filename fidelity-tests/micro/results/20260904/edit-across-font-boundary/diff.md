# diff — edit-across-font-boundary

expected 1 · allowed 0 · unexpected 1 (visible 1, invisible 0)

- **unexpected** `tab[Tab 1]/para[0:Kubectl rollout restart deploy].style@"Kubectl rollout restart deploy/api"`
  - before: `{"textStyle": {"fontSize": {"magnitude": 10, "unit": "PT"}, "weightedFontFamily": {"fontFamily": "Courier New", "weight": 400}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[0:Kubectl rollout restart deploy].text`
  - before: `""`
  - after:  `"-eu"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -1,2 +1,2 @@
-Kubectl rollout restart deploy/api \-n staging  
+Kubectl rollout restart deploy/api \-n staging-eu  
 Deploy to staging  
```
