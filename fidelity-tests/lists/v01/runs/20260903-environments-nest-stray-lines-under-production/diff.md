# diff — environments-nest-stray-lines-under-production

expected 0 · allowed 9 · unexpected 0 (visible 0, invisible 0)

- **allowed** `tab[Tab 1]/lists.kix.73yxf78mr7x1.listProperties.nestingLevels[0].glyphSymbol`
  - before: `"-"`
  - after:  `"●"`
- **allowed** `tab[Tab 1]/lists.kix.73yxf78mr7x1.listProperties.nestingLevels[1].glyphSymbol`
  - before: `"-"`
  - after:  `"○"`
- **allowed** `tab[Tab 1]/lists.kix.73yxf78mr7x1.listProperties.nestingLevels[2].glyphSymbol`
  - before: `"-"`
  - after:  `"■"`
- **allowed** `tab[Tab 1]/lists.kix.73yxf78mr7x1.listProperties.nestingLevels[3].glyphSymbol`
  - before: `"-"`
  - after:  `"●"`
- **allowed** `tab[Tab 1]/lists.kix.73yxf78mr7x1.listProperties.nestingLevels[4].glyphSymbol`
  - before: `"-"`
  - after:  `"○"`
- **allowed** `tab[Tab 1]/lists.kix.73yxf78mr7x1.listProperties.nestingLevels[5].glyphSymbol`
  - before: `"-"`
  - after:  `"■"`
- **allowed** `tab[Tab 1]/lists.kix.73yxf78mr7x1.listProperties.nestingLevels[6].glyphSymbol`
  - before: `"-"`
  - after:  `"●"`
- **allowed** `tab[Tab 1]/lists.kix.73yxf78mr7x1.listProperties.nestingLevels[7].glyphSymbol`
  - before: `"-"`
  - after:  `"○"`
- **allowed** `tab[Tab 1]/lists.kix.73yxf78mr7x1.listProperties.nestingLevels[8].glyphSymbol`
  - before: `"-"`
  - after:  `"■"`

## cat.md

```diff
--- before/cat.md
+++ after/cat.md
@@ -41,3 +41,3 @@
     * Secrets live in Vault under secret/platform/prod, rotate the API keys there  
-- Also a read replica in eu-west3, ask Priya before touching it  
+* Also a read replica in eu-west3, ask Priya before touching it  
 * Staging shares the prod cluster, namespace staging (yes, really)
```
