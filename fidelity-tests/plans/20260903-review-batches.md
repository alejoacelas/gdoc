# Plan — batches per document and at-a-glance review (2026-09-03)

Problem: 52 run copies with one edit each, and a reviewer must open before and after, find the
one sentence that changed, and then judge formatting by eye. Two changes fix this: run several
tasks on one copy, and give the reviewer a painted copy that shows what changed and whether it
was meant to.

## 1. Batches: 5–8 tasks per copy

- A **batch** is one Docs-UI copy of a fixture (comments and suggestions kept) on which the
  tasks run **one after another**, each by a fresh agent that sees only its own request. Task
  order is document order, one target per section, so edits never overlap and no task
  depends on another's result. Tasks that need the pristine state (a "resolve then reopen",
  a whole-section rewrite) go in a batch of their own or last.
- Judging stays per task: run k's after-capture is run k+1's before-capture (`gdt run-start
  --continue <batch>` instead of copying). `gdt-diff` still scores each task against its own
  before, so collateral is attributed to the task that caused it; the batch's final state is
  what the reviewer opens. Rates in `INDEX.md` are unchanged in meaning.
- Command track stays single-command-per-copy; it is for isolation, not review.
- Expected count: two batches per fixture instead of 11 copies; six fixtures → ~12 review
  docs plus the fixtures themselves.

## 2. At-a-glance: a painted review copy per batch

After the batch's last after-capture, the runner (never the agent) makes one more Docs-UI copy
of the batch — the **review copy** — and paints it from the diffs. The run copy stays pristine
as evidence.

- **Colours by class**, applied with the Docs API `updateTextStyle` (background colour) over the
  ranges named in each task's `diff.json`: green = expected change present; red = unexpected
  (collateral); amber = allowed side effect; **grey strikethrough note** where something that
  should have changed did not (request not met). Paragraph-level losses (alignment, spacing,
  heading demoted) get a red left border via `updateParagraphStyle` since they have no text
  range. Fixtures never use these three exact colours, so a painted mark is never ambiguous.
- **One comment per task**, anchored on the task's Target text, in document order and numbered
  `T1…Tn`: the request verbatim, then `Expected: …`, then `Outcome: DONE / COLLATERAL (what
  was lost)`. Unchanged-by-design targets (DECLINED/GAP) get the comment too, saying why.
- **A header block** inserted at the top of the review copy (not the run copy): batch name,
  fixture link, run-copy link, and a table `T# | request | outcome`. That makes the review copy
  standalone; `gdt REVIEW` then just links review copies.
- Optional and cheap: Tools > Compare documents (fixture vs batch copy) through the copier
  agent, giving a native Docs comparison with every text change as a suggestion. It misses
  formatting-only changes, which the paint covers, so keep both when reviewing text-heavy
  fixtures.

## Why not "all edits in bold, fixtures never bold"

Bold loss is the most common collateral we measure; making it the marker would hide it, and a
colleague never asks "change the date, and make it bold". The paint layer gives the same
one-glance signal without changing what the agent is asked or what the fixture contains.

## Harness work (in order)

1. `gdt run-start --continue BATCH` (before = previous after; no copy) and `gdt batch-end`
   (loop of `run-end`, then merge the per-task `diff.json` into `batch.json`).
2. `bin/gdt-paint REVIEW_COPY batch.json`: a ~150-line Python script on the Docs API
   (`google-api-python-client` is already a gdoc dependency; reuse gdoc's token) that maps
   each diff item back to a UTF-16 range in the review copy by text search within the located
   paragraph, then issues one `batchUpdate` with the style requests and one Drive
   `comments.create` per task with an anchored region. Colours are fixed constants and listed in
   `references/capture.md` so the visual judge ignores them.
3. `gdt-review` gains a column for the review copy and the Compare doc, and the header block
   text comes from the same generator.
4. Task authoring rule added to the skill: batches of 5–8, document order, one target per
   section, non-overlapping; say in `tasks.md` which batch a task belongs to.

## Rerun scope

Rerun the existing five fixtures as two batches each (their tasks already exist and can be
grouped as they stand, minus the three that need pristine state), then build `objects/v01`.
Roughly one browser-agent job per batch for the two copies and the paint, plus the agents.
