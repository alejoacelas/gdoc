# REPLICATE

A readable record of what substantial agent sessions accomplished in this repo.

## Test suite report (2026-09-04)

Alejo wanted a report covering every test group in the repo, at class level, with the live fidelity suite included, committed as Markdown.

- Wrote `docs/TESTS.md`: one line per test class (334 classes across 55 pytest files, grouped by layer) stating the behaviour it guarantees, a per-file note on what is mocked, and a section on the fidelity suite (fixtures, the run pipeline, verdict rules, results as of 2026-09-03, harness limits).
- Verified every class name and test count against the source with `ast`, and that the file set matches the `fidelity-tests` branch.
- The working checkout was switched to another branch by a concurrent session mid-task, so the report was written and committed from a separate worktree of `fidelity-tests`.

Agent session a5c5713c-45aa-43b0-87ad-00c0d88aeae7 · Commits f0f3704

## write --tab bullet-inheritance repro (2026-09-04)

Alejo wanted a fidelity test for the failure seen when `gdoc write --tab` rewrote a hand-edited tab and every paragraph came back bulleted, using frozen snapshots, and a skill for submitting such cases.

- Froze the failing and the good tab's `gdoc structure` privately, then reduced the cause to one property: the tab's terminal empty paragraph carried a `bullet` (the Docs UI leaves one when a list is typed last; gdoc never does), which the per-tab write keeps and the inserted text inherits.
- Reproduced it in a scripted, anonymous fixture: `fidelity-tests/write/v01` (`build.sh` = three gdoc commands plus one `createParagraphBullets`), with a command-track run, `gdt-diff` (22 unexpected items), verdict COLLATERAL, and a `repros.md` entry; `gdt validate-fixture` only misses screenshots, recorded in `shot.json`.
- Added `tests/test_write_tab_terminal_bullet.py`: one test that fails until the fix clears the surviving paragraph's bullet, one passing counterpart for plain tabs.
- Added a "Reducing a failure seen in a real document" section to the `gdoc-fidelity-test` skill.

Agent session 7b7d0e6b-823f-4b1b-855e-c973745645cd · Commits 8762094

## Scripted browser captures and PDF comparison (2026-09-05)

Alejo wanted a scripted replacement for the extension-driven Google Docs shooter, timed on existing fidelity documents and compared with PDF exports, without editing or sharing any document.

- Added `gdt-shot-headless`: normal Chrome off-screen through Playwright/CDP, a dedicated `~/.config/gdt-chrome` profile with human login, fixed viewport and scroll offsets, and the existing `gdt-shot` filing format plus measured geometry and timings.
- Fixed late-loading outline and toast controls found during trials; the final five-copy benchmark captured 48 views at 1.11 seconds/view on first load and 1.13 seconds/view warm, including setup. Restarting Chrome preserved login.
- Exported the six supplied micro Docs with the work account and rendered PDFs at 150 dpi. Aligned crops agree on text, line breaks, bullets and footnote placement; these cases do not establish fidelity for comments, suggestions or chips. PDF export plus rendering took 7.82 seconds total versus 21.01 seconds for browser capture.
- Saved original captures, timings, side-by-side evidence, reproduction scripts and install notes. Seven local tests passed; all 11 document modification timestamps stayed unchanged. Committed on `fidelity-tests` without pushing, as requested.

Agent session 01a06e9e-61f8-7b20-be13-a1e8759790b0 · Commits 9a115e8
