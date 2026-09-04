# diff — rewrite-tab-after-ui-bullet

expected 0 · allowed 0 · unexpected 22 (visible 21, invisible 1)

- **unexpected** `tab[Repro]/para[new@5:second bullet⏎].text`
  - before: `"∅"`
  - after:  `"second bullet⏎"`
- **unexpected** `tab[Repro]/para[new@5:second bullet⏎].bullet`
  - before: `"∅"`
  - after:  `{"listId": "kix.95e8uvky1zrr", "textStyle": {}}`
- **unexpected** `tab[Repro]/para[new@5:second bullet⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "indentFirstLine": {"magnitude": 18, "unit": "PT"}, "indentStart": {"magnitude": 36, "unit": "PT"}}`
- **unexpected** `tab[Repro]/para[new@7:Closing plain paragraph.⏎].text`
  - before: `"∅"`
  - after:  `"Closing plain paragraph.⏎"`
- **unexpected** `tab[Repro]/para[new@7:Closing plain paragraph.⏎].bullet`
  - before: `"∅"`
  - after:  `{"listId": "kix.95e8uvky1zrr", "textStyle": {}}`
- **unexpected** `tab[Repro]/para[new@7:Closing plain paragraph.⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "indentFirstLine": {"magnitude": 18, "unit": "PT"}, "indentStart": {"magnitude": 36, "unit": "PT"}}`
- **unexpected** `tab[Repro]/para[new@8:⏎].text`
  - before: `"∅"`
  - after:  `"⏎"`
- **unexpected** `tab[Repro]/para[new@8:⏎].bullet`
  - before: `"∅"`
  - after:  `{"listId": "kix.95e8uvky1zrr", "textStyle": {}}`
- **unexpected** `tab[Repro]/para[new@8:⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "indentFirstLine": {"magnitude": 18, "unit": "PT"}, "indentStart": {"magnitude": 36, "unit": "PT"}}`
- **unexpected** `tab[Repro]/para[del@4:alpha item⏎].text`
  - before: `"alpha item⏎"`
  - after:  `"∅"`
- **unexpected** `tab[Repro]/para[del@4:alpha item⏎].bullet`
  - before: `{"listId": "kix.95e8uvky1zrr", "textStyle": {}}`
  - after:  `"∅"`
- **unexpected** (invisible) `tab[Repro]/para[0:Seed⏎].paragraphStyle.headingId`
  - before: `"h.sw3bblfxsa73"`
  - after:  `"h.cr2tlksvi7x"`
- **unexpected** `tab[Repro]/para[0:Seed⏎].text`
  - before: `"S"`
  - after:  `"R"`
- **unexpected** `tab[Repro]/para[0:Seed⏎].text`
  - before: `""`
  - after:  `"writt"`
- **unexpected** `tab[Repro]/para[0:Seed⏎].text`
  - before: `""`
  - after:  `"n hea"`
- **unexpected** `tab[Repro]/para[0:Seed⏎].text`
  - before: `""`
  - after:  `"ing"`
- **unexpected** `tab[Repro]/para[2:Placeholder paragraph one.⏎].text`
  - before: `"ceholder"`
  - after:  `"in"`
- **unexpected** `tab[Repro]/para[2:Placeholder paragraph one.⏎].text`
  - before: `"o"`
  - after:  `"after the headi"`
- **unexpected** `tab[Repro]/para[2:Placeholder paragraph one.⏎].text`
  - before: `"e"`
  - after:  `"g"`
- **unexpected** `tab[Repro]/para[5:beta item⏎].text`
  - before: `""`
  - after:  `"first "`
- **unexpected** `tab[Repro]/para[5:beta item⏎].text`
  - before: `""`
  - after:  `"ull"`
- **unexpected** `tab[Repro]/para[5:beta item⏎].text`
  - before: `"a item"`
  - after:  `""`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -4,9 +4,11 @@
 
-* # Seed
+* # Rewritten heading
 
 *   
-* Placeholder paragraph one.  
+* Plain paragraph after the heading.  
 *   
-* alpha item  
-* beta item  
+* first bullet  
+* second bullet  
+*   
+* Closing plain paragraph.  
 * 
```
