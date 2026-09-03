# diff — key-rotation-owner-to-priya

expected 2 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/para[38:Marco to rotate the API keys b].text`
  - before: `"M"`
  - after:  `"Priy"`
- **expected** `tab[Tab 1]/para[38:Marco to rotate the API keys b].text`
  - before: `"rco"`
  - after:  `""`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -53,3 +53,3 @@
 * Обновить README на русском, спросить Дмитрия  
-* Marco to [rotate the API keys](https://example.com/runbooks/rotate-keys) before Friday  
+* Priya to [rotate the API keys](https://example.com/runbooks/rotate-keys) before Friday  
 * Contact for infra questions:  
```
