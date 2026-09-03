# diff — smoke-test-apple-pay

expected 1 · allowed 0 · unexpected 0 (visible 0, invisible 0)

- **expected** `tab[Tab 1]/para[8:Smoke test the payment flow (c].text`
  - before: `""`
  - after:  `" + Apple Pay"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -13,3 +13,3 @@
 4. Deploy to staging	(infra, not us)  
-5. Smoke test the payment flow (card \+ SEPA)  
+5. Smoke test the payment flow (card \+ SEPA \+ Apple Pay)  
 6. Ship to 5% of users  
```
