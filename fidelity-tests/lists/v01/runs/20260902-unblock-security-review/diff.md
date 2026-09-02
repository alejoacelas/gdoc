# diff — unblock-security-review

expected 15 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].bullet.textStyle`
  - before: `"∅"`
  - after:  `{}`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].bullet.textStyle.backgroundColor.color.rgbColor.green`
  - before: `1`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].bullet.textStyle.backgroundColor.color.rgbColor.red`
  - before: `1`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].text`
  - before: `"BL"`
  - after:  `"D"`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].style@"O"`
  - before: `{"textStyle": {"backgroundColor": {"color": {"rgbColor": {"green": 1, "red": 1}}}, "foregroundColor": {"color": {"rgbColor": {"red": 1}}}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].text`
  - before: `"CK"`
  - after:  `"N"`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].style@"E"`
  - before: `{"textStyle": {"backgroundColor": {"color": {"rgbColor": {"green": 1, "red": 1}}}, "foregroundColor": {"color": {"rgbColor": {"red": 1}}}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].text`
  - before: `"D"`
  - after:  `""`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].style@":"`
  - before: `{"textStyle": {"backgroundColor": {"color": {"rgbColor": {"green": 1, "red": 1}}}, "foregroundColor": {"color": {"rgbColor": {"red": 1}}}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].text`
  - before: `" waiting on the"`
  - after:  `""`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].style@" security review "`
  - before: `{"textStyle": {"backgroundColor": {"color": {"rgbColor": {"green": 1, "red": 1}}}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].text`
  - before: `""`
  - after:  `"signed off "`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].style@"(Sam, "`
  - before: `{"textStyle": {"backgroundColor": {"color": {"rgbColor": {"green": 1, "red": 1}}}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].text`
  - before: `"again"`
  - after:  `"2 Sep"`
- **expected** `tab[Tab 1]/para[42:BLOCKED: waiting on the securi].style@")⏎"`
  - before: `{"textStyle": {"backgroundColor": {"color": {"rgbColor": {"green": 1, "red": 1}}}}}`
  - after:  `{"textStyle": {}}`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -59,3 +59,3 @@
 * Owner:	Marco    
-* BLOCKED: waiting on the security review (Sam, again)  
+* DONE: security review signed off (Sam, 2 Sep)  
 * 
```
