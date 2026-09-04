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

## lists-v01-edit-across-font-boundary-flattens-run   (lists/v01, 2026-09-02, COLLATERAL, no issue)
gdoc edit --account $A <copy> "deploy/api -n staging" "deploy/api -n staging-eu"
Expect: `Kubectl rollout restart deploy/api` keeps Courier New 10pt; only ` -n staging` → ` -n staging-eu`.
Observed: "OK replaced 1 occurrence"; the whole item became one default-style run (Courier New and 10pt gone).
Same shape: gdoc edit <copy> "Approved by Legal on 14 Aug" "Approved by Legal on 21 Aug" drops Georgia 13pt from
`14 Aug, see the thread` although the match ends before the Georgia run starts.
Runs: lists/v01/runs/20260902-kubectl-namespace, lists/v01/runs/20260902-legal-approval-date-georgia-run.

## lists-v01-markdown-bullet-ignores-nesting   (lists/v01, 2026-09-02, GAP-CLI, no issue)
gdoc edit --account $A <copy> --old-file old.txt --new-file new.txt    # new.txt = "  * Also a read replica…\n  * Staging shares…"
Expect: a way to put a paragraph into an existing list at a chosen nesting level (Docs API: createParagraphBullets
over a range that includes the neighbouring item, then indentStart/indentFirstLine for the level).
Observed (on the agent's scratch copy): the markdown bullet joins the nearest list at the level implied by the
paragraph's existing indent (108pt → level 2), leading spaces are ignored, and a multi-level markdown block
flattens to level 0 with literal tab characters left in the text. `gdoc edit` on the `-⇥Staging…` line alone made a
new list (● at 36pt) instead of joining `kix.73yxf78mr7x1`.
Runs: lists/v01/runs/20260902-staging-line-to-bullet, lists/v01/runs/20260902-environments-nest-stray-lines-under-production.

## text-v01-edit-resets-paragraph-style   (text/v01, 2026-09-02, COLLATERAL, no issue)
gdoc edit --account $A <copy> "Marta, 2 Sept 2026" "Marta, 3 Sept 2026"
Expect: the right-aligned signature keeps `alignment: END`.
Observed: paragraph alignment dropped to default (left). Same shape: `gdoc edit "O and x" " and x"` in the
1.5-spacing paragraph drops `lineSpacing: 150`; `gdoc edit --all "  " " "` drops the 36pt indent on the
`Open question` paragraph. Paragraph-level style is lost along with run styles.
Runs: text/v01/runs/20260902-signature-date, 20260902-co2-formula, 20260903-tidy-double-spaces.

## text-v01-edit-all-demotes-heading   (text/v01, 2026-09-02, COLLATERAL, no issue)
gdoc edit --account $A --all --case-sensitive <copy> "launch window" "release window"
Expect: five replacements keeping HEADING_1 on the title, bold, italic, and the link on `launch window FAQ`.
Observed: the H1 became NORMAL_TEXT, bold/italic gone, the link shrank to ` FAQ`, and bold on `checklist`
(same paragraph, outside the match) gone. Re-promoting with `# …` gives the heading a new `headingId`, so
any link to the old heading breaks. Run: text/v01/runs/20260902-launch-to-release-window.

## text-v01-edit-drops-font-size   (text/v01, 2026-09-02, COLLATERAL, no issue)
gdoc edit --account $A --case-sensitive <copy> "Key dates" "Key dates and labels"
Expect: the bold 14pt Normal paragraph keeps bold and 14pt.
Observed: both dropped; `**…**` markdown restores bold only — gdoc has no way to set a font size.
Run: text/v01/runs/20260902-rename-key-dates-fake-heading.

## collab-v01-link-retarget-orphans-comment   (collab/v01, 2026-09-03, COLLATERAL, no issue)
gdoc edit --account $A <copy> "finance handbook" "[finance handbook](https://www.notion.so/people-ops/expenses)"
Expect: only `link.url` changes; the comment anchored on `handbook` stays anchored.
Observed: url changed, text and styling identical, but the comment lost its anchor (card gone from the
margin; `gdoc comments` still lists it as open with the old quotedFileContent). Same mechanism as
lists relink-rotate-keys (anchor shrank). Run: collab/v01/runs/20260903-handbook-link-notion.

## gdoc-insert-start-demotes-first-heading   (harness, 2026-09-03, COLLATERAL, no issue)
gdoc insert --account $A --tab "Tab 1" --position start <copy> header.md
Expect: the markdown is inserted before the existing content; the document's first paragraph keeps HEADING_1.
Observed: the original first paragraph (`🚀 Q3 platform migration …`) becomes NORMAL_TEXT. Found while
building the review-copy header; the painter now inserts through the Docs API instead.

## write-v01-write-tab-inherits-terminal-bullet   (write/v01, 2026-09-04, COLLATERAL, https://github.com/LucaDeLeo/gdoc/issues/59)
gdoc write --account $A --tab Repro <copy> fidelity-tests/write/v01/rewrite.md
Expect: H1, plain paragraph, two list items, plain paragraph; only the two items carry a bullet.
Observed: all nine paragraphs (heading, blank separators, prose) become items of the list that owned the
tab's terminal empty paragraph, 36pt indent; `gdoc cat` prints `* # Rewritten heading`. Precondition: the
tab's terminal paragraph carries a bullet (`write/v01/build.sh` adds it with createParagraphBullets; the
Docs UI leaves one whenever a list is the last thing typed). gdoc-written lists never bullet the terminal
paragraph, so a tab seeded only by gdoc does not reproduce. Cause: `_tab_body_range` keeps the final
newline, its paragraph survives the delete with the bullet, and the inserted text merges into it.
Run: write/v01/runs/20260904-rewrite-tab-after-ui-bullet. Unit test: tests/test_write_tab_terminal_bullet.py.
