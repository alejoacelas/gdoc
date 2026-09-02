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

## kitchen-sink-v01-edit-all-strips-run-styles   (kitchen-sink/v01, 2026-09-02, COLLATERAL, no issue)
gdoc edit --account $A --all --case-sensitive <copy> "rollout window" "launch window"
Expect: three replacements, each keeping the style of the run it sits in (bold / italic+red / link).
Observed: "OK replaced 3 occurrences"; bold, italic, red and the link all stripped. Repairing with
markdown replacements (`**…**`, `*…*`, `[…](url)`) restores bold/italic/link but not the red colour,
and each markdown-bearing edit resets the paragraph to only what the replacement specifies.
Run: kitchen-sink/v01/runs/20260902-rollout-to-launch-window.

## kitchen-sink-v01-edit-cannot-reach-footnote   (kitchen-sink/v01, 2026-09-02, GAP-CLI, no issue)
gdoc edit --account $A --case-sensitive <copy> "pulled 28 Aug by Tomás" "pulled 2 Sept by Priya"
Expect: one replacement inside footnote kix.sodj60jamoog (the Docs API addresses footnote text via
segmentId in deleteContentRange/insertText).
Observed: exit 3 "no match found" although `gdoc cat` prints the footnote; same with --normalize.
Run: kitchen-sink/v01/runs/20260902-footnote-v8.
