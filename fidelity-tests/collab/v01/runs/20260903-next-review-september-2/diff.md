# diff — next-review-september

expected 2 · allowed 0 · unexpected 1 (visible 1, invisible 0)

- **expected** `tab[Tab 1]/para[22:Next review: JuneMarch. Owner:].text`
  - before: `"Jun"`
  - after:  `"S"`
- **unexpected** `tab[Tab 1]/para[22:Next review: JuneMarch. Owner:].style@"e"`
  - before: `{"suggestedInsertionIds": ["suggest.fr9lnzlv781n"], "textStyle": {}}`
  - after:  `{"textStyle": {}}`
- **expected** `tab[Tab 1]/para[22:Next review: JuneMarch. Owner:].text`
  - before: `""`
  - after:  `"ptember"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -38,2 +38,2 @@
 We also need to decide whether the scheme should stay ***simple to administer*** or track receipts per category.  
-Next review: JuneMarch. Owner: People Ops. Send questions to the \#people-ops channel.
+Next review: SeptemberMarch. Owner: People Ops. Send questions to the \#people-ops channel.
```
