# diff — handbook-link-notion

expected 1 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/para[8:Claims go through the expenses].style@"finance handbook"`
  - before: `{"textStyle": {"foregroundColor": {"color": {"rgbColor": {"blue": 0.8, "green": 0.33333334, "red": 0.06666667}}}, "link": {"url": "https://handbook.example.org/finance/expenses"}, "underline": true}}`
  - after:  `{"textStyle": {"foregroundColor": {"color": {"rgbColor": {"blue": 0.8, "green": 0.33333334, "red": 0.06666667}}}, "link": {"url": "https://www.notion.so/people-ops/expenses"}, "underline": true}}`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -13,3 +13,3 @@
 Everyone on a permanent contract who works from home at least two days a week is eligible. Contractors are not eligible under this draft, though see the open question below. The annual amount rises from £300 to £450, paid in two instalments, and unspent balance does not roll over.  
-Claims go through the expenses portal (see the [finance handbook](https://handbook.example.org/finance/expenses)) rather than the old form.
+Claims go through the expenses portal (see the [finance handbook](https://www.notion.so/people-ops/expenses)) rather than the old form.
 
```
