# diff — kubectl-namespace

expected 1 · allowed 0 · unexpected 1 (visible 1, invisible 0)

- **unexpected** `tab[Tab 1]/para[39:Kubectl rollout restart deploy].style@"Kubectl rollout restart deploy/api"`
  - before: `{"textStyle": {"fontSize": {"magnitude": 10, "unit": "PT"}, "weightedFontFamily": {"fontFamily": "Courier New", "weight": 400}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[39:Kubectl rollout restart deploy].text`
  - before: `""`
  - after:  `"-eu"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -56,3 +56,3 @@
   Actually the retro room is booked till 3pm on the 12th, use Zoom instead and skip the next two items if you are not on infra.  
-* Kubectl rollout restart deploy/api \-n staging  
+* Kubectl rollout restart deploy/api \-n staging-eu  
 * Approved by Legal on 14 Aug, see the thread  
```
