# diff — relink-rotate-keys

expected 1 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/para[38:Marco to rotate the API keys b].style@"rotate the API keys"`
  - before: `{"textStyle": {"foregroundColor": {"color": {"rgbColor": {"blue": 0.8, "green": 0.33333334, "red": 0.06666667}}}, "link": {"url": "https://example.com/rotate-keys"}, "underline": true}}`
  - after:  `{"textStyle": {"foregroundColor": {"color": {"rgbColor": {"blue": 0.8, "green": 0.33333334, "red": 0.06666667}}}, "link": {"url": "https://example.com/runbooks/rotate-keys"}, "underline": true}}`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -54,3 +54,3 @@
 * Обновить README на русском, спросить Дмитрия  
-* Marco to [rotate the API keys](https://example.com/rotate-keys) before Friday  
+* Marco to [rotate the API keys](https://example.com/runbooks/rotate-keys) before Friday  
 * Contact for infra questions:  
```
