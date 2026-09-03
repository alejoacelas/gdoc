# diff — paused-until-q1

expected 1 · allowed 1 · unexpected 2 (visible 2, invisible 0)

- **allowed** (invisible) `tab[Tab 1]/table[2]/cell[3,2]/para[0:Paused until Q4, see budget⏎].paragraphStyle.avoidWidowAndOrphan`
  - before: `false`
  - after:  `"∅"`
- **unexpected** `tab[Tab 1]/table[2]/cell[3,2]/para[0:Paused until Q4, see budget⏎].style@"Paused"`
  - before: `{"textStyle": {"fontSize": {"magnitude": 9, "unit": "PT"}, "weightedFontFamily": {"fontFamily": "Courier New", "weight": 400}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/table[2]/cell[3,2]/para[0:Paused until Q4, see budget⏎].text`
  - before: `"4"`
  - after:  `"1"`
- **unexpected** `tab[Tab 1]/table[2]/cell[3,2]/para[0:Paused until Q4, see budget⏎].style@"see budget⏎"`
  - before: `{"textStyle": {"fontSize": {"magnitude": 14, "unit": "PT"}, "weightedFontFamily": {"fontFamily": "Georgia", "weight": 400}}}`
  - after:  `{"textStyle": {}}`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -31,3 +31,3 @@
 | Ops coordinator (Madrid) | Offer out ⏳ | References Right-to-work | Tomás; start 2 Sept 2026 |
-| Recruiter (contract) | Sourcing | Paused until Q4, see budget | Budget hold |
+| Recruiter (contract) | Sourcing | Paused until Q1, see budget | Budget hold |
 | Head of People |  | owner	stage	ETA | TBC after the Q3 board |
```
