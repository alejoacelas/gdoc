# diff — drop-old-plan

expected 1 · allowed 0 · unexpected 6 (visible 6, invisible 0)

- **unexpected** `tab[Tab 1]/para[11:The old plan was to ship in Au].style@"T"`
  - before: `{"textStyle": {"bold": true, "strikethrough": true}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[11:The old plan was to ship in Au].text`
  - before: `"he old plan was to ship in August; t"`
  - after:  `""`
- **unexpected** `tab[Tab 1]/para[11:The old plan was to ship in Au].style@"new plan is 14–18 Sept"`
  - before: `{"textStyle": {"backgroundColor": {"color": {"rgbColor": {"green": 1, "red": 1}}}}}`
  - after:  `{"textStyle": {}}`
- **unexpected** `tab[Tab 1]/para[11:The old plan was to ship in Au].style@"internal only"`
  - before: `{"textStyle": {"smallCaps": true}}`
  - after:  `{"textStyle": {}}`
- **unexpected** `tab[Tab 1]/para[11:The old plan was to ship in Au].style@"do not forward"`
  - before: `{"textStyle": {"foregroundColor": {"color": {"rgbColor": {"red": 1}}}}}`
  - after:  `{"textStyle": {}}`
- **unexpected** `tab[Tab 1]/para[11:The old plan was to ship in Au].style@"read this first "`
  - before: `{"textStyle": {"underline": true}}`
  - after:  `{"textStyle": {}}`
- **unexpected** `tab[Tab 1]/para[11:The old plan was to ship in Au].style@"agreed with Legal"`
  - before: `{"textStyle": {"backgroundColor": {"color": {"rgbColor": {"green": 1}}}}}`
  - after:  `{"textStyle": {}}`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -16,3 +16,3 @@
 The formula card still reads H2O and x2, the old deck typed its footnote marker as \[1\] instead of using a real footnote[^1], and the style rule is Northstar 2.1 (non-breaking space) in headlines but Northstar 2.1 (plain space) in body copy.  
-**~~The old plan~~** ~~was to ship in August~~; the new plan is 14–18 Sept.  This draft is internal only — do not forward — and read this first before editing the copy above; the dates are agreed with Legal.  
+The new plan is 14–18 Sept.  This draft is internal only — do not forward — and read this first before editing the copy above; the dates are agreed with Legal.  
 Ship🚀ping starts Monday; the café team in 東京 and the Москва office get the build first, and the Arabic landing page (مرحباً بنورث ستار) ships a week later.  
```
