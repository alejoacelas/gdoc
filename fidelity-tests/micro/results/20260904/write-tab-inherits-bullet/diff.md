# diff — write-tab-inherits-bullet

expected 4 · allowed 4 · unexpected 13 (visible 11, invisible 2)

- **expected** `tab[Tab 1]/para[new@2:First paragraph.⏎].text`
  - before: `"∅"`
  - after:  `"First paragraph.⏎"`
- **expected** `tab[Tab 1]/para[new@2:First paragraph.⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT"}`
- **unexpected** `tab[Tab 1]/para[new@3:⏎].text`
  - before: `"∅"`
  - after:  `"⏎"`
- **unexpected** `tab[Tab 1]/para[new@3:⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT"}`
- **expected** `tab[Tab 1]/para[new@4:Second paragraph.⏎].text`
  - before: `"∅"`
  - after:  `"Second paragraph.⏎"`
- **expected** `tab[Tab 1]/para[new@4:Second paragraph.⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT"}`
- **unexpected** `tab[Tab 1]/para[new@5:⏎].text`
  - before: `"∅"`
  - after:  `"⏎"`
- **unexpected** `tab[Tab 1]/para[new@5:⏎].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT"}`
- **unexpected** `tab[Tab 1]/para[del@0:Intro paragraph.⏎].text`
  - before: `"Intro paragraph.⏎"`
  - after:  `"∅"`
- **unexpected** `tab[Tab 1]/para[del@1:first item⏎].text`
  - before: `"first item⏎"`
  - after:  `"∅"`
- **allowed** `tab[Tab 1]/para[del@1:first item⏎].bullet`
  - before: `{"listId": "kix.uvuot02si0t9", "textStyle": {}}`
  - after:  `"∅"`
- **unexpected** (invisible) `tab[Tab 1]/para[2:last item⏎].paragraphStyle.headingId`
  - before: `"∅"`
  - after:  `"h.4m8i4h2qn6ga"`
- **unexpected** `tab[Tab 1]/para[2:last item⏎].paragraphStyle.indentFirstLine.magnitude`
  - before: `18`
  - after:  `"∅"`
- **unexpected** `tab[Tab 1]/para[2:last item⏎].paragraphStyle.indentFirstLine.unit`
  - before: `"PT"`
  - after:  `"∅"`
- **unexpected** `tab[Tab 1]/para[2:last item⏎].paragraphStyle.indentStart.magnitude`
  - before: `36`
  - after:  `"∅"`
- **unexpected** `tab[Tab 1]/para[2:last item⏎].paragraphStyle.indentStart.unit`
  - before: `"PT"`
  - after:  `"∅"`
- **unexpected** (invisible) `tab[Tab 1]/para[2:last item⏎].paragraphStyle.namedStyleType`
  - before: `"NORMAL_TEXT"`
  - after:  `"HEADING_1"`
- **allowed** `tab[Tab 1]/para[2:last item⏎].bullet`
  - before: `"∅"`
  - after:  `null`
- **allowed** (invisible) `tab[Tab 1]/para[2:last item⏎].bullet.listId`
  - before: `"kix.uvuot02si0t9"`
  - after:  `"∅"`
- **allowed** `tab[Tab 1]/para[2:last item⏎].bullet.textStyle`
  - before: `{}`
  - after:  `"∅"`
- **unexpected** `tab[Tab 1]/para[2:last item⏎].text`
  - before: `"last item"`
  - after:  `"New title"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -1,5 +1,5 @@
-Intro paragraph.
+# New title
 
-* first item  
-* last item
+First paragraph.
 
+Second paragraph.  
```
