# diff — fix-double-numbering

expected 2 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/para[16:2) do we keep the legacy read ].text`
  - before: `"2) "`
  - after:  `""`
- **expected** `tab[Tab 1]/para[17:3) ¿quién habla con Finance? ©].text`
  - before: `"3) "`
  - after:  `""`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -25,4 +25,4 @@
 1) Who owns the on-call rota during the rollout?  
-2) 2\) do we keep the legacy read replica?     
-3) 3\) ¿quién habla con Finance? © 2026
+2) do we keep the legacy read replica?     
+3) ¿quién habla con Finance? © 2026
 
```
