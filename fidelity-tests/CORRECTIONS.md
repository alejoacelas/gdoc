# Pipeline corrections log

Things found while running the first vertical slice (2026-09-02) that were fixed on the
spot so the pipeline could run, plus what still needs a decision. Review and delete
entries once you agree; disagreements go back into the skill.

## Fixed

- **`gdoc cp` drops comments and suggestions.** Drive `files.copy` has no option for
  them. Run copies for tasks whose preconditions need either must be made with the Docs
  UI (File > Make a copy, tick "Copy comments and suggestions", untick "Share it with the
  same people"), then moved into `runs/` with `gdoc mv`. First run recorded as INVALID
  because of this; skill updated to say which copy method to use.
- **Screenshots are viewports, not pages.** The browser tool captures the viewport
  (~1440×780 at 100% zoom), so "one PNG per page" was never achievable. Captures are
  now `view-NN.jpg` at fixed `scrollTop` offsets (0, 650, 1300 …) on
  `.kix-appview-editor`, set via JavaScript so before and after line up exactly.
  `shot.json` records the step. Files are JPEG because that is what the tool saves.
- **`--quiet` is not accepted by `gdoc ls`, `gdoc mkdir`, `gdoc mv`** (fine on cat,
  comments, revisions, cp, structure). `gdt doctor` and `gdt capture` adjusted.
- **The fixture was already frozen** (version named `frozen` by the builder session).
  `fixture.md` now carries both the Drive revision number (44) and the Docs
  `revisionId`, since the two APIs disagree about what a revision is.
- **The builder left no `built.md`.** Reconstructed one from the structure dump and a
  browser read; it says so at the top.

- **Task agents could read the fixture notes.** The first task agent ran with the repo
  as its working directory and cited `built.md` in its report. Task agents must be
  spawned with an empty working directory (or told the repo is off limits); the skill's
  Running section now says so. This run's verdict stands because the agent found the
  target by reading the doc, but treat its CONCERNS section as contaminated.
- **`gdt-diff` compared runs by index**, so a paragraph edit that merged runs showed up
  as fifteen "expected" items and hid the two real style losses. It now aligns
  paragraphs by ordinal and characters by `difflib`, and reports a style change on
  unchanged text as its own item, always unexpected. The run's diff went from 15/0 to
  1 expected / 2 unexpected.
- **`gdt-index` now also lists every run** with a link to its copy, so the `gdt INDEX`
  doc is clickable per run.

## Needs a decision

- **Comment `modifiedTime` differs between baseline and a fresh copy** even before any
  edit, so `gdt-diff` reports one "unexpected" item when comparing a copy to the
  fixture baseline. Runs compare before/after of the same copy so this does not affect
  verdicts, but the policy in `references/diff.md` should say whether comment
  `modifiedTime` is dropped globally.
- **Where the `gdt INDEX` Google Doc lives** and whether it should be a pushed copy of
  `INDEX.md` (`gdoc push`) or hand-maintained.

## Fixed (overnight run, 2026-09-02)

- **`gdt-diff` aligned paragraphs by ordinal**, so one inserted or deleted paragraph
  made every later paragraph look changed. It now aligns each container's paragraph
  sequence with `difflib` (most-similar pairing inside replace blocks), reports inserted
  and deleted paragraphs as `para[new@N:…]` / `para[del@N:…]` items carrying their
  bullet and paragraphStyle, and compares paragraphStyle/bullet only on aligned pairs.
  Synthetic check: inserting one list item into the kitchen-sink baseline yields three
  items, all on the new paragraph. The existing run still reads 1 expected / 2 unexpected.
- **`gdt-diff` honoured only the first `paragraph beginning` locator.** Target now
  accepts any number of locators, plus `new paragraph \`X\``, `heading \`X\``,
  `footnote`, `header`, `footer`, several `cells [r,c]` per table. "renumber" in
  Allowed also covers `/lists` leaves.
- **Explicit-default styles produced 33 false "unexpected" items.** After `gdoc edit` on a
  one-paragraph table cell, Docs dropped the paragraph's explicit `alignment: START`,
  zero-width borders and similar values that equal the named style; rendering is identical.
  `gdt-diff` now canonicalises every paragraphStyle, textStyle and bullet textStyle against
  the document's `namedStyles` before diffing (an explicit value equal to the inherited one is
  treated as absent). One genuine change survives in that run: `avoidWidowAndOrphan`
  false → inherited true. **Needs a decision:** pagination hints (`avoidWidowAndOrphan`,
  `keepLinesTogether`, `keepWithNext`) are classified `allowed` and invisible by default;
  say in `references/diff.md` whether that stands.
- **Target with a trailing full stop matched nothing** (`table 1, cell [1,2] (row "…").`),
  so the budget run's one real change was classified unexpected. Regex rewritten.
- **Paragraph-level items inside the Target** (`.bullet.*`, `.paragraphStyle.*`) are now
  `expected` only when the task's Expected or Allowed text mentions that kind of change
  (bullet, list, indent, heading, style, alignment, renumber, checkbox or the property
  name); otherwise `unexpected`. A text edit should not silently excuse a list change.
- **A run where the agent made no edit** failed `after_revision_later`. `gdt run-end` now
  reports `n/a (no edit made; structure identical)` in that case; the outcome is decided by
  the refusal rules, not INVALID.
- **`bin/gdt-verdict`** added: fills the verdict front matter from the run directory
  (copy id, revisions, gates, structural summary) so only outcome, judges and prose are
  typed by hand. It refuses to write a non-INVALID verdict without `after/shot.json`.
- **Task agents cannot be given an empty working directory** by the Agent tool: a `cd`
  outside the project is reset by the harness. Isolation is by instruction (cd into an empty
  scratch dir, read nothing outside it, report `pwd`); every agent tonight reported the
  empty dir and none cited fixture files.
- **Screenshots go through a subagent.** Each `computer screenshot` puts the image in the
  driver's context; 15 views per batch is unsustainable. A "shooter" agent takes the views
  and runs `gdt-shot`, returning paths only. Same for the visual judge, which reads the
  JPEGs itself and returns verbatim answers.
- **A style change the request asks for was always "unexpected".** Retargeting a link or
  removing a highlight changes a run's textStyle on unchanged text, which the diff treated as
  collateral by definition. Now, inside the Target, a style item is `expected` when every
  differing style key is named in the **Request or Allowed** text (link/url, highlight/
  background, colour, bold, italic, font, size …). Matching against Expected was tried first
  and rejected: Expected usually says what must stay intact, which turned the first run's
  strikethrough loss into an expected item. Regression: kitchen-sink next-steps-effort-2 must
  stay 1 expected / 2 unexpected.
- **Task agents that decline may still create Drive files.** Two lists agents made scratch
  copies with `gdoc cp` to try an edit safely, then could not delete them (gdoc has no trash
  command). Both were renamed `… SCRATCH (agent trial, safe to delete)` and moved into the
  runs folder. The task-agent prompt should say whether trial copies are allowed and where.
- **The structural judge is blind to comment anchors.** `gdoc comments --json` returns
  `quotedFileContent` (the text at creation) but no `anchor`, so an anchor that shrinks or
  moves produces no diff item. The visual judge caught two such cases (lists relink-rotate-keys,
  key-rotation-owner-to-priya: the highlight no longer covers `Marco to`). Both are recorded
  COLLATERAL with `human: requested`. Fix options: expose the Drive `anchor` field in `gdoc
  comments --json`, or have `gdt capture` call the Drive API directly for anchors.
- **`gdt-diff` crashed on a dropdown chip.** The Docs API returns a dropdown chip as a
  paragraph element with only `startIndex`/`endIndex` (no type key), which became an empty
  dict after normalisation. It is now a `⟨typelessElement⟩` pseudo-character.
- **Parallel task agents shared one scratch directory** and clobbered each other's
  `structure.json`; one agent noticed and re-verified from a uniquely named dump. Give each
  task agent its own empty directory (`scratchpad/empty/<slug>`).
