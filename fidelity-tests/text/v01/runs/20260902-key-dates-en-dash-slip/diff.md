# diff — key-dates-en-dash-slip

expected 1 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/para[5:The launch window opens 14–18 ].text`
  - before: `"4–18"`
  - after:  `"5–19"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -8,3 +8,3 @@
 **Key dates**  
-The **launch window** opens 14–18 Sept 2026, not 14-18 Sept as the v2 draft said and not 14—18 Sept as the CMS rendered it.  Legal signed off on Tuesday; Marta wants the “beta” label gone and the "beta"  badge hidden in the same release.  
+The **launch window** opens 15–19 Sept 2026, not 14-18 Sept as the v2 draft said and not 14—18 Sept as the CMS rendered it.  Legal signed off on Tuesday; Marta wants the “beta” label gone and the "beta"  badge hidden in the same release.  
 Ana’s note: the *launch window* is not the same thing as the Launch Window banner in the app; the banner string lives in the [release **checklist**](https://example.com/northstar/checklist) and is owned by design.  See also the [launch window FAQ](https://example.com/northstar/faq) before replying to customers.  
```
