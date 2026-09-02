# diff — tidy-double-spaces

expected 6 · allowed 0 · unexpected 17 (visible 17, invisible 0)

- **expected** `tab[Tab 1]/para[1:Owner:⇥Marta Kowalczyk⇥Status:].text`
  - before: `"  "`
  - after:  `""`
- **unexpected** `tab[Tab 1]/para[5:The launch window opens 14–18 ].style@"launch window"`
  - before: `{"textStyle": {"bold": true}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[5:The launch window opens 14–18 ].text`
  - before: `" "`
  - after:  `""`
- **expected** `tab[Tab 1]/para[5:The launch window opens 14–18 ].text`
  - before: `" "`
  - after:  `""`
- **unexpected** `tab[Tab 1]/para[6:Ana’s note: the launch window ].style@"launch window"`
  - before: `{"textStyle": {"italic": true}}`
  - after:  `{"textStyle": {}}`
- **unexpected** `tab[Tab 1]/para[6:Ana’s note: the launch window ].style@"checklist"`
  - before: `{"textStyle": {"bold": true, "foregroundColor": {"color": {"rgbColor": {"blue": 0.8, "green": 0.33333334, "red": 0.06666667}}}, "link": {"url": "https://example.com/northstar/checklist"}, "underline":`
  - after:  `{"textStyle": {"foregroundColor": {"color": {"rgbColor": {"blue": 0.8, "green": 0.33333334, "red": 0.06666667}}}, "link": {"url": "https://example.com/northstar/checklist"}, "underline": true}}`
- **expected** `tab[Tab 1]/para[6:Ana’s note: the launch window ].text`
  - before: `" "`
  - after:  `""`
- **unexpected** `tab[Tab 1]/para[11:The old plan was to ship in Au].style@"The old plan"`
  - before: `{"textStyle": {"bold": true, "strikethrough": true}}`
  - after:  `{"textStyle": {}}`
- **unexpected** `tab[Tab 1]/para[11:The old plan was to ship in Au].style@" was to ship in August"`
  - before: `{"textStyle": {"strikethrough": true}}`
  - after:  `{"textStyle": {}}`
- **unexpected** `tab[Tab 1]/para[11:The old plan was to ship in Au].style@"new plan is 14–18 Sept"`
  - before: `{"textStyle": {"backgroundColor": {"color": {"rgbColor": {"green": 1, "red": 1}}}}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[11:The old plan was to ship in Au].text`
  - before: `" "`
  - after:  `""`
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
- **unexpected** `tab[Tab 1]/para[21:Open question for Tomás: do we].paragraphStyle.indentFirstLine.magnitude`
  - before: `36`
  - after:  `"∅"`
- **unexpected** `tab[Tab 1]/para[21:Open question for Tomás: do we].paragraphStyle.indentFirstLine.unit`
  - before: `"PT"`
  - after:  `"∅"`
- **unexpected** `tab[Tab 1]/para[21:Open question for Tomás: do we].paragraphStyle.indentStart.magnitude`
  - before: `36`
  - after:  `"∅"`
- **unexpected** `tab[Tab 1]/para[21:Open question for Tomás: do we].paragraphStyle.indentStart.unit`
  - before: `"PT"`
  - after:  `"∅"`
- **unexpected** `tab[Tab 1]/para[21:Open question for Tomás: do we].style@"Open question"`
  - before: `{"textStyle": {"bold": true}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[21:Open question for Tomás: do we].text`
  - before: `" "`
  - after:  `""`
- **unexpected** `tab[Tab 1]/para[21:Open question for Tomás: do we].style@"maybe"`
  - before: `{"suggestedInsertionIds": ["suggest.p6habqssdsab"], "suggestedTextStyleChanges": {"suggest.p6habqssdsab": {"textStyle": {"bold": true, "italic": true}, "textStyleSuggestionState": {"backgroundColorSug`
  - after:  `{"suggestedInsertionIds": ["suggest.p6habqssdsab"], "suggestedTextStyleChanges": {"suggest.p6habqssdsab": {"textStyle": {}, "textStyleSuggestionState": {"backgroundColorSuggested": true, "baselineOffs`
- **unexpected** `tab[Tab 1]/para[21:Open question for Tomás: do we].style@"yes"`
  - before: `{"suggestedDeletionIds": ["suggest.p6habqssdsab"], "suggestedTextStyleChanges": {"suggest.p6habqssdsab": {"textStyle": {"bold": true, "italic": true}, "textStyleSuggestionState": {"backgroundColorSugg`
  - after:  `{"suggestedDeletionIds": ["suggest.p6habqssdsab"], "suggestedTextStyleChanges": {"suggest.p6habqssdsab": {"textStyle": {}, "textStyleSuggestionState": {"backgroundColorSuggested": true, "baselineOffse`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -2,3 +2,3 @@
 
-Owner:	Marta Kowalczyk	Status:	DRAFT    
+Owner:	Marta Kowalczyk	Status:	DRAFT  
 **Summary**
@@ -8,4 +8,4 @@
 **Key dates**  
-The **launch window** opens 14–18 Sept 2026, not 14-18 Sept as the v2 draft said and not 14—18 Sept as the CMS rendered it.  Legal signed off on Tuesday; Marta wants the “beta” label gone and the "beta"  badge hidden in the same release.  
-Ana’s note: the *launch window* is not the same thing as the Launch Window banner in the app; the banner string lives in the [release **checklist**](https://example.com/northstar/checklist) and is owned by design.  See also the [launch window FAQ](https://example.com/northstar/faq) before replying to customers.  
+The launch window opens 14–18 Sept 2026, not 14-18 Sept as the v2 draft said and not 14—18 Sept as the CMS rendered it. Legal signed off on Tuesday; Marta wants the “beta” label gone and the "beta" badge hidden in the same release.  
+Ana’s note: the launch window is not the same thing as the Launch Window banner in the app; the banner string lives in the [release checklist](https://example.com/northstar/checklist) and is owned by design. See also the [launch window FAQ](https://example.com/northstar/faq) before replying to customers.  
 If anything slips, the launch window moves as a whole; we do not ship half the features. Live status: [https://status.example.com/northstar](https://status.example.com/northstar) (updated hourly).
@@ -16,3 +16,3 @@
 The formula card still reads H2O and x2, the old deck typed its footnote marker as \[1\] instead of using a real footnote[^1], and the style rule is Northstar 2.1 (non-breaking space) in headlines but Northstar 2.1 (plain space) in body copy.  
-**~~The old plan~~** ~~was to ship in August~~; the new plan is 14–18 Sept.  This draft is internal only — do not forward — and read this first before editing the copy above; the dates are agreed with Legal.  
+The old plan was to ship in August; the new plan is 14–18 Sept. This draft is internal only — do not forward — and read this first before editing the copy above; the dates are agreed with Legal.  
 Ship🚀ping starts Monday; the café team in 東京 and the Москва office get the build first, and the Arabic landing page (مرحباً بنورث ستار) ships a week later.  
@@ -28,3 +28,3 @@
 	Beta badge	Ana	TBD   
-**Open question** for Tomás: do we keep the beta badge for existing users?  Ana says ***maybeyes***, Marta says no.
+Open question for Tomás: do we keep the beta badge for existing users? Ana says maybeyes, Marta says no.
 
```
