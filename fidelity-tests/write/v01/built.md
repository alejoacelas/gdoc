# gdt-write-v01 — as built

- Built 2026-09-04 by `build.sh` (gdoc 0.21.0, the account in `config.yaml`). Docs UI never opened.
- Two tabs: the default `Tab 1` (empty) and `Repro`, the one under test.
- `Repro` after `gdoc write --tab Repro seed.md`, then `createParagraphBullets` on the final
  empty paragraph (indices 56–57), preset `BULLET_DISC_CIRCLE_SQUARE`:

```
[H1] Seed
[N]
[N]  Placeholder paragraph one.
[N]
[● ] alpha item
[● ] beta item
[● ]            ← the terminal empty paragraph, now a list item (36pt indent, 18pt first line)
```

Before that last request the terminal paragraph was plain, and `gdoc write --tab` on the tab
rendered correctly. The bullet on the terminal paragraph is the whole fixture.
