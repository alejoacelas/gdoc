---
name: gdoc-fidelity-test
description: Test whether an agent holding the gdoc CLI can carry out realistic edit requests on messy Google Docs without collateral damage. Fixtures are built by hand in the browser; each test is a plain-language edit task run on a Drive copy; the verdict comes from before/after screenshots plus a structural diff. Use when the user wants to stress-test gdoc (or any Docs API tool), add a fixture or task, re-run tasks after a CLI change, or review results — e.g. "add a fidelity fixture for footnotes", "rerun the gdoc edit tests", "does gdoc survive editing next to a chip".
---

# gdoc-fidelity-test — can gdoc edit a messy document without breaking it?

The aim is not whether gdoc can read or recreate a document. It is whether an agent
using gdoc can do what a colleague asks — change a figure, rename a heading, fix a
footnote, reply to a comment — on the kind of document people actually have, and leave
everything else untouched.

So the unit of test is an **edit task**, not a document. Documents are **fixtures**,
built by hand in the browser so they contain what the API cannot create. A run copies
the fixture, hands one task to a fresh agent, and compares before with after. The
document is the oracle; there is no spec.

Everything lives in two places that mirror each other:

- Drive: folder `gdoc-fidelity-tests/` (work account), one sub-folder per fixture,
  with the fixture doc and a `runs/` sub-folder of copies.
- Local: `fidelity-tests/` at the root of this repo, same tree, holding prompts,
  accounts, tasks, screenshots, structure dumps, transcripts and verdicts. Scripts live
  in `fidelity-tests/bin/`.

## Naming

- **Fixture doc** — `gdt-<area>-v<NN>`, e.g. `gdt-tables-v01`. Area is one lowercase
  word (`text`, `structure`, `lists`, `tables`, `objects`, `layout`, `chips`, `collab`,
  `kitchen-sink`). A new version is a new doc; old runs stay reproducible.
- **Run copy** — `gdt-<area>-v<NN> run <YYYYMMDD> <task-slug>`, made with `gdoc cp`
  into the fixture's `runs/` folder. Never edit the fixture itself.
- **Local fixture folder** — `fidelity-tests/<area>/v<NN>/` with `prompt.md`,
  `built.md`, `tasks.md`, `baseline/` (`page-01.png …`, `structure.json`, `cat.md`,
  `comments.json`) and `runs/<YYYYMMDD>-<task-slug>/` (`after/` with the same files,
  `transcript.md`, `diff.md`, `verdict.md`).
- **Index** — `fidelity-tests/INDEX.md`: one row per fixture with its tasks and their
  latest verdicts, plus doc links. Regenerate with `bin/gdt-index` and push to the
  Google Doc `gdt INDEX` in the Drive root so the suite is reviewable from one link.

## Fixtures

### Ask for mess, not features
Isolated feature demos are too clean. Real documents are pasted together over months
by several people, and that is where tools break. Every fixture, whatever its area,
must carry a baseline of mess, and the prompt should say so. Ask the builder for
things like:

- emoji and non-Latin text in headings, list items and table cells, not just in prose
- a numbered list that turns into a checklist halfway, nested bullets inside a table
  cell, a list interrupted by a paragraph and continued
- text pasted from Word, Slack or Notion with its fonts and sizes still attached, so
  one paragraph has three fonts
- direct formatting that imitates a heading (bold 14pt Normal text) next to a real one
- a phrase that appears three times with different formatting, once inside a link
- empty paragraphs that carry formatting, trailing spaces, tabs used for alignment,
  manual "1)" numbering typed next to a real list
- a chip or a link inside a table cell, a comment anchored across a formatting boundary,
  a suggestion left pending
- whatever the builder finds hard to do; it should aim for "hard to reproduce through
  the API", and combine at least two such features per paragraph

`prompt.md` is one or two sentences plus that list. Today's ask worked: "I'm testing
a CLI against this doc, so build a document that uses a bunch of the formatting and
functionality available in Google Docs for <area>. Use browser control and pick things
you think will be hard to replicate for a tool connected through the Docs API."

### Build rules: one doc, one agent
Every incident so far came from agents sharing a document: keystrokes in another
agent's tab, a stray select-all wiping a shared tab, an undo removing someone else's
work, a click landing on the wrong paragraph after a concurrent edit reflowed the page.

- One builder agent (Fable) per fixture, in its own browser tab. It never opens
  another test doc.
- Before typing: screenshot, confirm the tab and caret. Menus, popups and `cmd+f`
  steal focus; use the menu-search box instead of shortcuts like `cmd+Return`.
- Never select-all in a document with anything worth keeping. Never undo past your
  own last action.
- Anything written into a shared document goes through the CLI, not the browser.

When done, the builder writes `built.md`: the exact text, what formatting sits where,
what it tried and could not do, every autocorrection Docs made (capitalisation, curly
quotes, `--` to a dash, `1.` to a list), and a **trap list**: the places it thinks an
API edit is most likely to damage. `built.md` is a reading aid for the judge, not a
contract.

### Freeze and baseline
Name the version in the browser (File > Version history > Name current version,
`frozen`). Google prunes unnamed revisions within hours. Then capture the baseline:

```
bin/gdt-shot DOC baseline/          # browser screenshots, see Judging
gdoc structure --account A DOC > baseline/structure.json
gdoc cat --account A DOC > baseline/cat.md
gdoc comments --all --account A DOC --json > baseline/comments.json
```

## Tasks

`tasks.md` holds five to ten requests per fixture, written the way a colleague would
ask, each with the effect it should have. Two authors:

- the builder contributes tasks aimed at its trap list;
- a second agent reads the document cold, without `built.md`, and writes the requests
  a person would actually make of it.

Do not filter tasks by what the API can do. Ask for whatever a colleague would ask,
including things the API probably cannot express, such as adding a suggestion or
resizing a drawing. Whether a failure was an API limit or a CLI defect is decided at
verdict time, not when writing the task. Include at least one task that needs a
correct read to do at all ("tick the third checklist item", "change the dropdown's
value"), one that rewrites a whole section, one adjacent to an object the API cannot
create, one whose target phrase also appears elsewhere, and one you expect to be
impossible.

## Running a task

1. `gdoc cp` the fixture into `runs/`, named as above. Check the copy kept comments
   and suggestions (`gdoc comments --all`; screenshot); note in `verdict.md` if not.
2. Capture `after/`-style baseline of the copy (screenshots, structure, cat, comments).
   Before and after come from the same copy so pagination starts identical.
3. Spawn a fresh agent (Fable) with only the request and the copy's URL. It may use
   any gdoc command. It must report what it did and whether it believes it succeeded.
   Save its report and the commands it ran as `transcript.md`.
4. Capture `after/`.

## Judging

Two judges, and they must agree.

**Structural diff** — `bin/gdt-diff before/structure.json after/structure.json`
normalises both (drops indices, revision and object IDs) and lists every paragraph
whose text, named style, run styles, bullets, table layout, inline objects, links or
bookmarks changed. It also diffs `cat.md` and `comments.json`. Each item is tagged
**visible** or **invisible**: invisible covers link targets, bookmarks, comment
anchors, named style behind identical-looking formatting, list identity behind
identical-looking numbering. The diff is a judge in its own right — anything it lists
that the task did not ask for is collateral — and it is the locator for the visual
judge.

**Visual** — always Google Docs screenshots, never PDF export, so comments,
suggestion colours and chips appear as a reader sees them. `bin/gdt-shot` documents
the procedure: same window size, 100% zoom, print layout on, scroll page by page. For
each diff item, crop the matching region from before and after at full resolution;
hand a model the request, the crop pairs one at a time, then the full pages as
thumbnails, and ask: is the requested change present, and does anything else differ?
A line-break shift moves everything below it; the model reasons from the crops, not
from pixel positions.

If the structural diff lists a change the visual judge did not see, or the other way
round, the run goes to a human.

`verdict.md` records one of:
- **PASS** — the requested change and nothing else.
- **COLLATERAL** — the change plus damage. Say whether the damage was visible or
  invisible, and whether the agent's own read afterwards would have revealed it. The
  silent case is the one that matters most; today every corruption came with
  "OK replaced 1 occurrence".
- **NOT DONE** — nothing changed, or the wrong thing did.
- **DECLINED** — the agent said it could not do it. This beats COLLATERAL; score it so.

Every verdict other than PASS also carries a **cause**: `api` when the Docs API has no
way to express the request (check the API reference, not the CLI's help), `cli` when
the API can but gdoc did not, or `agent` when gdoc could but the agent did not find the
way. DECLINED with cause `api` is the correct outcome and counts as a pass in the
index. DECLINED with cause `cli` or `agent` is a gap to fix.

## Reduce and file

Isolation comes after failure, never before. Start with the loaded fixtures; when a
task fails, reduce it:

1. Find the single gdoc command that reproduces the damage on the fixture, and append
   it to `fidelity-tests/repros.md`. That file is the regression suite: it runs
   without an agent and without judging.
2. If the cause is unclear, build a small isolation fixture (`gdt-iso-<slug>-v01`)
   containing only the construct involved, and rerun the command there. Isolation
   fixtures are cheap and can be created by the CLI when the construct allows it.
3. If the cause is the CLI rather than an API limit, open an issue on `LucaDeLeo/gdoc`
   (check for duplicates) and link it from the verdict and the repro.

## Record

Update `INDEX.md`, push it to `gdt INDEX`, commit on the `fidelity-tests` branch of this
fork. Keep old runs.

## Known CLI behaviours
- `gdoc edit` parses the replacement as markdown: a leading `1. ` or `# ` restyles the
  whole paragraph (issue #57); `_word_` becomes italic. Use `--old-file/--new-file`.
- `gdoc edit` rewrites the whole paragraph's runs, so bold or italic elsewhere in the
  paragraph can be lost.
- `gdoc write` from markdown misplaces paragraph styles after emoji and other non-BMP
  characters; looks like Python length versus UTF-16 index arithmetic.
- `gdoc cat` refuses `--tab` with `--comments`; use `gdoc comments --all`.
- The default account may not see work docs; always pass `--account`.
- Revision export ignores `--tab`.
