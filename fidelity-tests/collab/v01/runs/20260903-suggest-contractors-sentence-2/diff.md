# diff — suggest-contractors-sentence

expected 1 · allowed 0 · unexpected 2 (visible 2, invisible 0)

- **unexpected** `tab[Tab 1]/para[20:Should contractors be eligible].style@"team are contractors."`
  - before: `{"textStyle": {}}`
  - after:  `{"suggestedInsertionIds": ["suggest.iejv39er8zdg"], "suggestedTextStyleChanges": {"suggest.iejv39er8zdg": {"textStyle": {}, "textStyleSuggestionState": {"backgroundColorSuggested": true, "baselineOffs`
- **unexpected** `tab[Tab 1]/para[20:Should contractors be eligible].style@" "`
  - before: `{"suggestedInsertionIds": ["suggest.iejv39er8zdg"], "textStyle": {}}`
  - after:  `{"suggestedInsertionIds": ["suggest.iejv39er8zdg"], "suggestedTextStyleChanges": {"suggest.iejv39er8zdg": {"textStyle": {}, "textStyleSuggestionState": {"backgroundColorSuggested": true, "baselineOffs`
- **expected** `tab[Tab 1]/para[20:Should contractors be eligible].text`
  - before: `""`
  - after:  `"Legal will confirm by 15 Sept.team are contractors. "`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -36,3 +36,3 @@
 
-Should contractors be eligible? Legal thinks it blurs the employment status line; the engineering leads think excluding them is unfair since half the platform team are contractors. People Ops has no strong view either way.  
+Should contractors be eligible? Legal thinks it blurs the employment status line; the engineering leads think excluding them is unfair since half the platform team are contractors. Legal will confirm by 15 Sept.team are contractors. People Ops has no strong view either way.  
 We also need to decide whether the scheme should stay ***simple to administer*** or track receipts per category.  
```
