# Repros

One gdoc command per entry that reproduces a known failure on a copy of a fixture, without
an agent and without judging. Rerun after every CLI change. Format:

```
## <slug>   (<fixture>, <date>, <outcome>, <issue or "no issue">)
gdoc <command> --account $A <copy of fixture> ...
Expect: <what a fixed CLI does>. Observed: <what happened>.
```

## kitchen-sink-v01-edit-strips-paragraph-styles   (kitchen-sink/v01, 2026-09-02, COLLATERAL, no issue)
gdoc edit --account $A <copy> "Estimated effort: 3 dev-days" "Estimated effort: 4 dev-days"
Expect: only `3` → `4`; strikethrough on `v2 migration script` and highlight on `Estimated effort` untouched.
Observed: both styles removed; paragraph collapsed from 7 runs to 3. Run: kitchen-sink/v01/runs/20260902-next-steps-effort-2.
