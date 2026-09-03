# diff — northstar-2-2

expected 3 · allowed 0 · unexpected 5 (visible 5, invisible 0)

- **unexpected** `tab[Tab 1]/para[9:Northstar 2.1 is the biggest r].paragraphStyle.alignment`
  - before: `"JUSTIFIED"`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/para[9:Northstar 2.1 is the biggest r].text`
  - before: `"1"`
  - after:  `"2"`
- **unexpected** `tab[Tab 1]/para[9:Northstar 2.1 is the biggest r].style@"release-notes-2.1.md"`
  - before: `{"textStyle": {"fontSize": {"magnitude": 9, "unit": "PT"}, "foregroundColor": {"color": {"rgbColor": {"blue": 0.8, "green": 0.33333334, "red": 0.06666667}}}, "link": {"url": "http://release-notes-2.1.`
  - after:  `{"textStyle": {"foregroundColor": {"color": {"rgbColor": {"blue": 0.8, "green": 0.33333334, "red": 0.06666667}}}, "link": {"url": "http://release-notes-2.1.md"}, "underline": true}}`
- **unexpected** `tab[Tab 1]/para[9:Northstar 2.1 is the biggest r].style@" (more soon...) "`
  - before: `{"textStyle": {"fontSize": {"magnitude": 9, "unit": "PT"}, "weightedFontFamily": {"fontFamily": "Courier New", "weight": 400}}}`
  - after:  `{"textStyle": {}}`
- **unexpected** `tab[Tab 1]/para[9:Northstar 2.1 is the biggest r].style@"as Marta put it in #launch, “we finally "`
  - before: `{"textStyle": {"fontSize": {"magnitude": 13, "unit": "PT"}, "weightedFontFamily": {"fontFamily": "Georgia", "weight": 400}}}`
  - after:  `{"textStyle": {}}`
- **unexpected** `tab[Tab 1]/para[9:Northstar 2.1 is the biggest r].style@"and the landing-page draft says Faster s"`
  - before: `{"textStyle": {"weightedFontFamily": {"fontFamily": "Times New Roman", "weight": 400}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[10:The formula card still reads C].text`
  - before: `"1"`
  - after:  `"2"`
- **expected** `tab[Tab 1]/para[10:The formula card still reads C].text`
  - before: `"1"`
  - after:  `"2"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -14,4 +14,4 @@
 
-Northstar 2.1 is the biggest release since 1.0: [release-notes-2.1.md](http://release-notes-2.1.md) (more soon...) as Marta put it in \#launch, “we finally fixed the sync bug that ate everyone’s Tuesday” and the landing-page draft says Faster sync. Fewer surprises. More soon… (Tomás pasted that last bit from the web page, hence the fonts.)  
-The formula card still reads CO2 and x2, the old deck typed its footnote marker as \[1\] instead of using a real footnote[^1], and the style rule is Northstar 2.1 (non-breaking space) in headlines but Northstar 2.1 (plain space) in body copy.  
+Northstar 2.2 is the biggest release since 1.0: [release-notes-2.1.md](http://release-notes-2.1.md) (more soon...) as Marta put it in \#launch, “we finally fixed the sync bug that ate everyone’s Tuesday” and the landing-page draft says Faster sync. Fewer surprises. More soon… (Tomás pasted that last bit from the web page, hence the fonts.)  
+The formula card still reads CO2 and x2, the old deck typed its footnote marker as \[1\] instead of using a real footnote[^1], and the style rule is Northstar 2.2 (non-breaking space) in headlines but Northstar 2.2 (plain space) in body copy.  
 **~~The old plan~~** ~~was to ship in August~~; the new plan is 14–18 Sept.  This draft is internal only — do not forward — and read this first before editing the copy above; the dates are agreed with Legal.  
```
