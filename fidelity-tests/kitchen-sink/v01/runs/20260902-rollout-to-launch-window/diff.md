# diff — rollout-to-launch-window

expected 9 · allowed 0 · unexpected 3 (visible 3, invisible 0)

- **expected** `tab[Tab 1]/para[4:We are on track for the rollou].text`
  - before: `"ro"`
  - after:  `""`
- **expected** `tab[Tab 1]/para[4:We are on track for the rollou].text`
  - before: `"lo"`
  - after:  `"a"`
- **expected** `tab[Tab 1]/para[4:We are on track for the rollou].text`
  - before: `"t"`
  - after:  `"nch"`
- **expected** `tab[Tab 1]/para[4:We are on track for the rollou].text`
  - before: `"ro"`
  - after:  `""`
- **unexpected** `tab[Tab 1]/para[4:We are on track for the rollou].style@"l"`
  - before: `{"textStyle": {"foregroundColor": {"color": {"rgbColor": {"red": 1}}}, "italic": true}}`
  - after:  `{"textStyle": {"italic": true}}`
- **expected** `tab[Tab 1]/para[4:We are on track for the rollou].text`
  - before: `"lo"`
  - after:  `"a"`
- **unexpected** `tab[Tab 1]/para[4:We are on track for the rollou].style@"u"`
  - before: `{"textStyle": {"foregroundColor": {"color": {"rgbColor": {"red": 1}}}, "italic": true}}`
  - after:  `{"textStyle": {"italic": true}}`
- **expected** `tab[Tab 1]/para[4:We are on track for the rollou].text`
  - before: `"t"`
  - after:  `"nch"`
- **unexpected** `tab[Tab 1]/para[4:We are on track for the rollou].style@" window"`
  - before: `{"textStyle": {"foregroundColor": {"color": {"rgbColor": {"red": 1}}}, "italic": true}}`
  - after:  `{"textStyle": {"italic": true}}`
- **expected** `tab[Tab 1]/para[4:We are on track for the rollou].text`
  - before: `"ro"`
  - after:  `""`
- **expected** `tab[Tab 1]/para[4:We are on track for the rollou].text`
  - before: `"lo"`
  - after:  `"a"`
- **expected** `tab[Tab 1]/para[4:We are on track for the rollou].text`
  - before: `"t"`
  - after:  `"nch"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -7,3 +7,3 @@
 
-We are on track for the **rollout window** of 15-19 Sept. infra sign-off is done; the data team still owes us the backfill numbers – see the budget table below. Priya wrote in Slack “don’t touch the *rollout window* without asking me first”, so the [rollout window](https://example.com/rollout-plan) is frozen until the Monday sync.
+We are on track for the **launch window** of 15-19 Sept. infra sign-off is done; the data team still owes us the backfill numbers – see the budget table below. Priya wrote in Slack “don’t touch the *launch window* without asking me first”, so the [launch window](https://example.com/rollout-plan) is frozen until the Monday sync.
 
```
