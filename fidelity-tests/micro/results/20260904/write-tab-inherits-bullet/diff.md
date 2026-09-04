# diff — write-tab-inherits-bullet

expected 6 · allowed 3 · unexpected 9 (visible 7, invisible 2)

- **expected** `tab[Tab 1]/para[new@2:First paragraph.⏎].text`
  - before: `"∅"`
  - after:  `"First paragraph.⏎"`
- **expected** `tab[Tab 1]/para[new@2:First paragraph.⏎].bullet`
  - before: `"∅"`
  - after:  `{"listId": "kix.f7spk2j6yvr6", "textStyle": {}}`
- **expected** `tab[Tab 1]/para[new@2:First paragraph.⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "indentFirstLine": {"magnitude": 18, "unit": "PT"}, "indentStart": {"magnitude": 36, "unit": "PT"}}`
- **unexpected** `tab[Tab 1]/para[new@3:⏎].text`
  - before: `"∅"`
  - after:  `"⏎"`
- **allowed** `tab[Tab 1]/para[new@3:⏎].bullet`
  - before: `"∅"`
  - after:  `{"listId": "kix.f7spk2j6yvr6", "textStyle": {}}`
- **unexpected** `tab[Tab 1]/para[new@3:⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "indentFirstLine": {"magnitude": 18, "unit": "PT"}, "indentStart": {"magnitude": 36, "unit": "PT"}}`
- **expected** `tab[Tab 1]/para[new@4:Second paragraph.⏎].text`
  - before: `"∅"`
  - after:  `"Second paragraph.⏎"`
- **expected** `tab[Tab 1]/para[new@4:Second paragraph.⏎].bullet`
  - before: `"∅"`
  - after:  `{"listId": "kix.f7spk2j6yvr6", "textStyle": {}}`
- **expected** `tab[Tab 1]/para[new@4:Second paragraph.⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "indentFirstLine": {"magnitude": 18, "unit": "PT"}, "indentStart": {"magnitude": 36, "unit": "PT"}}`
- **unexpected** `tab[Tab 1]/para[new@5:⏎].text`
  - before: `"∅"`
  - after:  `"⏎"`
- **allowed** `tab[Tab 1]/para[new@5:⏎].bullet`
  - before: `"∅"`
  - after:  `{"listId": "kix.f7spk2j6yvr6", "textStyle": {}}`
- **unexpected** `tab[Tab 1]/para[new@5:⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "indentFirstLine": {"magnitude": 18, "unit": "PT"}, "indentStart": {"magnitude": 36, "unit": "PT"}}`
- **unexpected** `tab[Tab 1]/para[del@0:Intro paragraph.⏎].text`
  - before: `"Intro paragraph.⏎"`
  - after:  `"∅"`
- **unexpected** `tab[Tab 1]/para[del@1:first item⏎].text`
  - before: `"first item⏎"`
  - after:  `"∅"`
- **allowed** `tab[Tab 1]/para[del@1:first item⏎].bullet`
  - before: `{"listId": "kix.f7spk2j6yvr6", "textStyle": {}}`
  - after:  `"∅"`
- **unexpected** (invisible) `tab[Tab 1]/para[2:last item⏎].paragraphStyle.headingId`
  - before: `"∅"`
  - after:  `"h.b73pzqb10t0q"`
- **unexpected** (invisible) `tab[Tab 1]/para[2:last item⏎].paragraphStyle.namedStyleType`
  - before: `"NORMAL_TEXT"`
  - after:  `"HEADING_1"`
- **unexpected** `tab[Tab 1]/para[2:last item⏎].text`
  - before: `"last item"`
  - after:  `"New title"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -1,5 +1,7 @@
-Intro paragraph.
+* # New title
 
-* first item  
-* last item  
+*   
+* First paragraph.  
+*   
+* Second paragraph.  
 * 
```
