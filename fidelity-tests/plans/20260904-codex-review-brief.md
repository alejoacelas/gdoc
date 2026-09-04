# Brief for external reviewers of the gdoc fidelity-test suite (2026-09-04)

You are reviewing a test harness, not fixing gdoc. Two reviewers work in parallel with
different focuses (yours is named in your prompt); both read this brief first.

## What the suite is

`fidelity-tests/` tests whether an agent holding the `gdoc` CLI can carry out realistic edit
requests on messy Google Docs without collateral damage. Read, in this order:

1. `.claude/skills/gdoc-fidelity-test/SKILL.md` and its `references/` (the contract: tasks,
   gates, two judges, outcome taxonomy).
2. `fidelity-tests/CORRECTIONS.md` (everything that was fixed or fudged while running).
3. `fidelity-tests/plans/20260902-overnight-report.md` (what ran, results, the three most
   interesting failures) and `plans/20260903-review-batches.md` (the batch + painted-copy design).
4. `fidelity-tests/INDEX.md` (rates per fixture and track) and `REVIEW.md` (every run with its
   request, outcome and edited copy; the five painted review copies at the top).
5. The harness: `fidelity-tests/bin/` — `gdt` (run-start/run-end/capture/gates), `gdt-diff`
   (the structural judge; normalisation + classification rules), `gdt-paint` (paints a review
   copy from the diffs), `gdt-verdict`, `gdt-batch-*`, `gdt-review`, `gdt-index`.
6. Fixtures: `fidelity-tests/<area>/v01/{prompt,built,tasks,fixture}.md`, `baseline/`, and
   `runs/<run>/{transcript,diff,verdict}.md` plus `before/` and `after/` captures
   (`structure.json` is the raw Docs API document; `view-NN.jpg` are screenshots).
7. `fidelity-tests/repros.md` and `references/known-cli-behaviours.md` for what has been found.

## Access

- gdoc CLI is installed. Always pass `--account alejandro.acelas-contractor@80000hours.org`
  after the subcommand. `fidelity-tests/config.yaml` is git-ignored; copy it from
  `/Users/alejo/best/work/tools/active/gdoc/cli/fidelity-tests/config.yaml` if a script needs it.
- Read-only please: `gdoc cat/structure/comments/revisions/export` on any doc linked from
  INDEX.md or REVIEW.md. Do NOT edit any fixture, run copy or review copy; if you want to
  experiment, `gdoc cp` a run copy with a title starting `SCRATCH codex-review` and edit that.
- Browser: Orca's built-in browser (`orca goto/snapshot/screenshot --json`) may or may not be
  signed into Google; try it on a review-copy URL. If it is not, the `view-NN.jpg` screenshots
  in each run's `before/` and `after/` folders show the same documents.
- gdoc's own issue tracker: `gh issue list -R LucaDeLeo/gdoc --state all --limit 100` and
  `gh issue view -R LucaDeLeo/gdoc <n>`; issues 57 and 59 are directly relevant. Also skim
  gdoc's README and `--help` output to see what users are told they can do.

## Deliverable

Write your review as Markdown at `fidelity-tests/reviews/20260904-codex-<focus>.md` in your
worktree and commit it on your branch (`git add fidelity-tests/reviews && git commit`). Be
concrete: cite file paths and line numbers, run ids, and specific diff items; for each
finding say what is wrong, how you verified it, and the smallest change that would fix it.
Rank findings by how much they would change the reported numbers or mislead a reader.
Prefer fifteen sharp findings to fifty vague ones. Do not rewrite the harness yourself.
