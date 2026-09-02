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
