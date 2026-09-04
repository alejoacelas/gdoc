# diff — co2-formula

expected 1 · allowed 0 · unexpected 1 (visible 1, invisible 0)

- **unexpected** `tab[Tab 1]/para[10:The formula card still reads H].paragraphStyle.lineSpacing`
  - before: `150`
  - after:  `"∅"`
- **expected** `tab[Tab 1]/para[10:The formula card still reads H].text`
  - before: `"H2O"`
  - after:  `"CO2"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -15,3 +15,3 @@
 Northstar 2.1 is the biggest release since 1.0: [release-notes-2.1.md](http://release-notes-2.1.md) (more soon...) as Marta put it in \#launch, “we finally fixed the sync bug that ate everyone’s Tuesday” and the landing-page draft says Faster sync. Fewer surprises. More soon… (Tomás pasted that last bit from the web page, hence the fonts.)  
-The formula card still reads H2O and x2, the old deck typed its footnote marker as \[1\] instead of using a real footnote[^1], and the style rule is Northstar 2.1 (non-breaking space) in headlines but Northstar 2.1 (plain space) in body copy.  
+The formula card still reads CO2 and x2, the old deck typed its footnote marker as \[1\] instead of using a real footnote[^1], and the style rule is Northstar 2.1 (non-breaking space) in headlines but Northstar 2.1 (plain space) in body copy.  
 **~~The old plan~~** ~~was to ship in August~~; the new plan is 14–18 Sept.  This draft is internal only — do not forward — and read this first before editing the copy above; the dates are agreed with Legal.  
```
