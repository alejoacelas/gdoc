# diff — launch-to-release-window

expected 15 · allowed 0 · unexpected 1 (visible 0, invisible 1)

- **unexpected** (invisible) `tab[Tab 1]/para[0:Northstar 2.1 launch window — ].paragraphStyle.headingId`
  - before: `"h.fhr9e3eq4raj"`
  - after:  `"h.h8p2iegzr8wc"`
- **expected** `tab[Tab 1]/para[0:Northstar 2.1 launch window — ].text`
  - before: `""`
  - after:  `"re"`
- **expected** `tab[Tab 1]/para[0:Northstar 2.1 launch window — ].text`
  - before: `""`
  - after:  `"e"`
- **expected** `tab[Tab 1]/para[0:Northstar 2.1 launch window — ].text`
  - before: `"unch"`
  - after:  `"se"`
- **expected** `tab[Tab 1]/para[5:The launch window opens 15–19 ].text`
  - before: `""`
  - after:  `"re"`
- **expected** `tab[Tab 1]/para[5:The launch window opens 15–19 ].text`
  - before: `""`
  - after:  `"e"`
- **expected** `tab[Tab 1]/para[5:The launch window opens 15–19 ].text`
  - before: `"unch"`
  - after:  `"se"`
- **expected** `tab[Tab 1]/para[6:Ana’s note: the launch window ].text`
  - before: `""`
  - after:  `"re"`
- **expected** `tab[Tab 1]/para[6:Ana’s note: the launch window ].text`
  - before: `""`
  - after:  `"e"`
- **expected** `tab[Tab 1]/para[6:Ana’s note: the launch window ].text`
  - before: `"unch"`
  - after:  `"se"`
- **expected** `tab[Tab 1]/para[6:Ana’s note: the launch window ].text`
  - before: `""`
  - after:  `"re"`
- **expected** `tab[Tab 1]/para[6:Ana’s note: the launch window ].text`
  - before: `""`
  - after:  `"e"`
- **expected** `tab[Tab 1]/para[6:Ana’s note: the launch window ].text`
  - before: `"unch"`
  - after:  `"se"`
- **expected** `tab[Tab 1]/para[7:If anything slips, the launch ].text`
  - before: `""`
  - after:  `"re"`
- **expected** `tab[Tab 1]/para[7:If anything slips, the launch ].text`
  - before: `""`
  - after:  `"e"`
- **expected** `tab[Tab 1]/para[7:If anything slips, the launch ].text`
  - before: `"unch"`
  - after:  `"se"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -1,2 +1,2 @@
-# Northstar 2.1 launch window — announcement draft (v3)
+# Northstar 2.1 release window — announcement draft (v3)
 
@@ -8,5 +8,5 @@
 **Key dates and labels**  
-The launch window opens 15–19 Sept 2026, not 14–18 Sept as the v2 draft said and not 14—18 Sept as the CMS rendered it. Legal signed off on Tuesday; Marta wants the “beta” label gone and the "preview" badge hidden in the same release.  
-Ana’s note: the launch window is not the same thing as the Launch Window banner in the app; the banner string lives in the [release checklist](https://example.com/northstar/checklist) and is owned by design. See also the [launch window FAQ](https://example.com/northstar/faq) before replying to customers.  
-If anything slips, the launch window moves as a whole; we do not ship half the features. Live status: [https://status.example.com/northstar](https://status.example.com/northstar) (updated hourly).
+The release window opens 15–19 Sept 2026, not 14–18 Sept as the v2 draft said and not 14—18 Sept as the CMS rendered it. Legal signed off on Tuesday; Marta wants the “beta” label gone and the "preview" badge hidden in the same release.  
+Ana’s note: the release window is not the same thing as the Launch Window banner in the app; the banner string lives in the [release checklist](https://example.com/northstar/checklist) and is owned by design. See also the [release window FAQ](https://example.com/northstar/faq) before replying to customers.  
+If anything slips, the release window moves as a whole; we do not ship half the features. Live status: [https://status.example.com/northstar](https://status.example.com/northstar) (updated hourly).
 
```
