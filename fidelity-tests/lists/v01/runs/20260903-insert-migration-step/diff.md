# diff — insert-migration-step

expected 3 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/para[new@8:Run the DB migrations on stagi].text`
  - before: `"∅"`
  - after:  `"Run the DB migrations on staging (Priya)⏎"`
- **expected** `tab[Tab 1]/para[new@8:Run the DB migrations on stagi].bullet`
  - before: `"∅"`
  - after:  `{"listId": "kix.ehmbnlna9fov", "textStyle": {}}`
- **expected** `tab[Tab 1]/para[new@8:Run the DB migrations on stagi].paragraphStyle`
  - before: `"∅"`
  - after:  `{"namedStyleType": "NORMAL_TEXT", "indentFirstLine": {"magnitude": 18, "unit": "PT"}, "indentStart": {"magnitude": 36, "unit": "PT"}}`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -13,4 +13,5 @@
 4. Deploy to staging	(infra, not us)  
-5. Smoke test the payment flow (card \+ SEPA \+ Apple Pay)  
-6. Ship to 5% of users  
+5. Run the DB migrations on staging (Priya)  
+6. Smoke test the payment flow (card \+ SEPA \+ Apple Pay)  
+7. Ship to 5% of users  
 
```
