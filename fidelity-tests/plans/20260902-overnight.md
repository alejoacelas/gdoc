# Overnight run — 2026-09-02

Brief for the agent running the first full suite. Read the skill first
(`.claude/skills/gdoc-fidelity-test/SKILL.md` and its `references/`), then
`fidelity-tests/CORRECTIONS.md`, then the completed run in
`fidelity-tests/kitchen-sink/v01/runs/` as the worked example.

## Goal

By morning, one Google Doc named `gdt INDEX` in the Drive root
(`fidelity-tests/config.yaml: drive_root`) that links every fixture doc and every run copy,
with each run's outcome, so the reviewer can open before/after side by side. `INDEX.md`
in the repo says the same thing. Every run has `diff.md` and `verdict.md`.

## Scope

Take the untested angles in `fidelity-tests/IDEAS.md`. Build one fixture per area, each
carrying the baseline mess, in this order (stop cleanly wherever time runs out; a
finished fixture with four runs beats six half-built ones):

1. `lists/v01` — the three-lists-that-look-like-one problem, checklists, manual `1)`.
2. `tables/v01` — nested bullets in cells, chips and links in cells, merged cells.
3. `text/v01` — repeated phrase in different formatting, mixed fonts, fake headings,
   curly/straight quotes and en dash/hyphen twins.
4. `collab/v01` — comments across formatting boundaries, pending suggestions, a resolved
   comment on text that changed.
5. `objects/v01` — footnotes, horizontal rules, images, drawings, headers/footers.

Then, on `kitchen-sink/v01`, run the remaining task (`budget-cloud-credits`) and write
three to five more tasks from the trap list in `built.md`.

For every fixture: `prompt.md`, builder agent in its own browser tab, `built.md` with a
trap list, freeze (named version `frozen`), `gdt capture` + screenshots, `gdt
validate-fixture`, five to ten tasks in the five-field format, then run each task on
the **agent track** (fresh agent, request + URL only). Run the **command track** only
where an agent run produced COLLATERAL, to isolate the command. Reduce failures into
`repros.md`; open issues on the configured tracker only for clear CLI defects, and check
for duplicates first.

## Rules that bit us today

- Copies: File > Make a copy in the Docs UI with "Copy comments and suggestions" ticked
  whenever a task's preconditions need either; `gdoc cp` drops both. Move the copy into
  the fixture's `runs/` folder with `gdoc mv`.
- One doc, one agent, one browser tab. Never type into a doc another agent has open.
- `--quiet` is rejected by `gdoc ls/mkdir/mv`.
- Screenshots: `resize_window` 1440×1200, scrollTop 0/650/1300… via JavaScript,
  `screenshot` with `save_to_disk`, then `bin/gdt-shot`.
- Any failed gate → INVALID verdict, move on. Do not fudge a partial run into a verdict.
- Always pass `--account` from `config.yaml`.

## Recording

- After each run: `bin/gdt-index`, then push `INDEX.md` to the `gdt INDEX` doc. Create
  it once with `gdoc new` in the Drive root and store its URL in `fidelity-tests/INDEX-doc.md`;
  update with `gdoc write --force`. Include the copy URL for every run so each row is
  clickable.
- Commit on the `fidelity-tests` branch after each fixture and after each batch of
  runs; push to `fork`. Never commit `config.yaml`.
- Append anything you had to fix in the harness to `CORRECTIONS.md`, same format.
- Leave a `plans/20260902-overnight-report.md` at the end: what got built, what ran,
  headline completion and safety per fixture, the three most interesting failures, and
  what you could not finish.
