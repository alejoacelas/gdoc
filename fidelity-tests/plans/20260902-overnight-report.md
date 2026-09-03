# Overnight run — report (2026-09-02 → 03)

Brief: `plans/20260902-overnight.md`. Reviewable from one link: the `gdt INDEX` doc
(`INDEX-doc.md`), which mirrors `INDEX.md` and links every fixture and every run copy.

## What got built

| Fixture | Doc | Built by | Tasks | Notes |
|---|---|---|---|---|
| kitchen-sink/v01 | existing | — | 7 (2 → 7) | five tasks added from the trap list |
| lists/v01 | `gdt-lists-v01` | browser agent, ~20 min | 12 (8 builder-side + 4 cold-read) | three lists that render as one, checklist with ticked items, ●○■ + dash levels, H3 and fake heading inside a list, Georgia run across two items, comment across two items, pending suggestion |
| tables/v01 | `gdt-tables-v01` | browser agent, ~28 min | 11 (7 + 4) | merged header and owner cells, comment inside the merge, suggestion in a cell, dropdown and date chips, nested bullets and checkboxes in cells, three fonts in a cell, borderless layout table, yellow callout |
| text/v01 | `gdt-text-v01` | browser agent, ~19 min | 11 (7 + 4) | `launch window` ×5 + case twin, curly/straight quote twins, en/em/hyphen twins, `…` vs `...`, NBSP, four fonts in a justified paragraph, sub/superscript, small caps, underline with trailing space, comment across bold→plain, suggestion replacing a word with a differently-formatted word |
| collab/v01 | `gdt-collab-v01` | browser agent, ~20 min | 6 | 9 comments (7 open, 1 resolved-then-edited, 1 orphaned; one thread with 2 replies), 12 pending suggestions of every kind, one accepted and one rejected |
| objects/v01 | blank doc created, `prompt.md` written | not built | — | ran out of night |

Every fixture: `prompt.md`, `built.md` with trap list, named version `frozen`, CLI baseline
(structure/cat/comments/revisions), screenshots at fixed offsets, `validate-fixture` ok.

## What ran

| Fixture | Tasks | Runs valid/invalid | Agent completion / safety | Command completion / safety | Outcomes (agent track) |
|---|---|---|---|---|---|
| collab/v01 | 6 | 5/1 | 2/5 / 4/5 | – / – | COLLATERAL 1, DECLINED-API 1, DONE 2, GAP-CLI 1 (+1 INVALID) |
| kitchen-sink/v01 | 7 | 9/1 | 4/7 / 5/7 | 0/2 / 0/2 | COLLATERAL 2, DONE 4, GAP-CLI 1 |
| lists/v01 | 12 | 14/0 | 5/12 / 8/12 | 0/2 / 0/2 | COLLATERAL 4, DECLINED-API 1, DONE 5, GAP-CLI 2 |
| tables/v01 | 11 | 11/0 | 9/11 / 10/11 | – / – | COLLATERAL 1, DONE 9, GAP-CLI 1 |
| text/v01 | 11 | 11/0 | 3/11 / 3/11 | – / – | COLLATERAL 8, DONE 3 |

**Overall, agent track: 46 valid runs, completion 23/46, safety 30/46. Command track: 4 runs
(one gdoc command each, the four isolated collateral cases), completion 0/4, safety 0/4.**

Agent track = fresh agent, request + copy URL only, told to work from an empty scratch
directory. Command track = the single gdoc command from `repros.md`, run by the runner on a
fresh copy, to isolate the CLI from the agent. All 50 runs have `transcript.md`, `diff.md`,
`verdict.md`, before/after captures and screenshots; every verdict has both judges recorded.

## The three most interesting failures

1. **`gdoc edit` rewrites the whole paragraph, not the match.** Every COLLATERAL tonight is
   this one behaviour. A one-word replace drops bold, italic, strikethrough, highlight, colour,
   font and size on runs up to 25 characters outside the match (`kitchen-sink next-steps-effort`,
   `lists kubectl-namespace`, `lists legal-approval`, `tables paused-until-q1`), and it also
   drops paragraph-level style: right alignment (`text signature-date`), 1.5 line spacing
   (`text co2-formula`), a 36pt indent and — with `--all` — the HEADING_1 named style itself
   (`text launch-to-release-window`). The command track reproduces all four cases we isolated
   with a single command. Agents that re-read with `gdoc structure` caught it and repaired
   bold/italic/links via markdown (three text runs ended DONE that way), but nothing in gdoc can
   restore colour, font, size, small caps, underline, alignment or spacing, so the rest stayed
   lost. `gdoc cat` cannot show any of those, which is why most agents reported success.
2. **Comment anchors shrink, and the structural judge cannot see it.** In `lists
   relink-rotate-keys` the agent replaced a sentence whose first words sat under a comment
   anchor; the anchor silently lost that half. `gdoc comments --json` returns
   `quotedFileContent` but no `anchor`, so the diff was clean and only the visual judge caught
   it. Two runs are recorded COLLATERAL with `human: requested` on this basis.
3. **Structure the API allows but gdoc cannot express.** Joining a paragraph to an existing
   list at a given nesting level (`lists staging-line-to-bullet`, `environments-nest`: the
   markdown-bullet path picks the level from the paragraph's indent and leaves literal tabs),
   deleting a table row (`tables remove-empty-vendor-row`), editing footnote text
   (`kitchen-sink footnote-v8`). All GAP-CLI; the agents refused cleanly and two of them made
   scratch copies to test on first, which they then could not delete.

The one honest DECLINED-API: ticking a checklist item (`lists tick-pair-with-buddy`); the
Docs API has no checkbox state, and the agent proved it by diffing checked and unchecked items.

## Harness changes made on the way (all in `CORRECTIONS.md`)

- `gdt-diff`: paragraph alignment by sequence (insertions no longer shift everything), style
  canonicalisation against named styles (killed 33 false items), multi-locator targets, a
  requested-style-change rule matched against Request/Allowed with word boundaries, typeless
  chip elements, long locators. Regression pin: the first run must stay 1 expected / 2 unexpected.
- `gdt run-start` / `run-end` / `gdt-transcript` / `gdt-verdict`: a run is now four commands
  plus screenshots.
- Screenshots and visual judging go through subagents so the driver's context survives;
  copies with comments go through a browser "copier" agent (File > Make a copy).
- Task agents get their own empty scratch directory (a shared one got clobbered).

## What I could not finish

- `objects/v01` was not built (doc and prompt exist).
- collab/v01 got 6 tasks and 5 valid runs, not the 5–10 tasks the plan asked for; the
  `reopen-three-forms` run is INVALID because the Docs-UI copy drops resolved comments.
- No issues were filed on the tracker: the dominant failure overlaps
  [LucaDeLeo/gdoc#57](https://github.com/LucaDeLeo/gdoc/issues/57) and needs a human to decide
  whether it is one issue ("edit rewrites the paragraph") or several; the repro lines are ready.
- Two "judges disagree" verdicts (anchor shrink) need a human call, and the
  pagination-hint/anchor policies in `CORRECTIONS.md` need a decision.
- Scratch copies made by two task agents were renamed `… SCRATCH … safe to delete` and moved
  into the runs folder; two unused `gdoc cp` copies are titled `SCRATCH unused …` in the Drive
  root. gdoc has no trash command; delete them by hand.
