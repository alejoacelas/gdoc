---
name: gdoc-fidelity-test
description: Test whether an agent holding the gdoc CLI can carry out realistic edit requests on messy Google Docs without collateral damage. Fixtures are built by hand in the browser; each test is a plain-language edit task run on a Drive copy; the verdict comes from a structural diff plus before/after screenshots. Use when the user wants to stress-test gdoc (or any Docs API tool), add a fixture or task, re-run tasks after a CLI change, or review results — e.g. "add a fidelity fixture for footnotes", "rerun the gdoc edit tests", "does gdoc survive editing next to a chip".
---

# gdoc-fidelity-test — can gdoc edit a messy document without breaking it?

The question is not whether gdoc can read or recreate a document. It is whether an
agent using gdoc can do what a colleague asks — change a figure, rename a heading, fix
a footnote, reply to a comment — on the kind of document people actually have, and
leave everything else untouched.

The unit of test is an **edit task**, not a document. Documents are **fixtures**, built
by hand in the browser so they contain what the API cannot create. A run copies the
fixture, hands one task to a fresh agent, and compares before with after.

**Two oracles.** The baseline copy is the oracle for what must *not* change: anything
outside the task's declared boundary that differs is collateral. The task itself is
the oracle for what *must* change: every task declares its expected outcome, target
and allowed side effects before anyone runs it (see [Tasks](#tasks)). Judging is the
intersection of the two, never a model's reading of the request after the fact.

## Status

One fixture (`kitchen-sink/v01`) is frozen and baselined, with runs. `fidelity-tests/bin/`
holds `gdt` (doctor, validate-fixture, capture, gates, index), `gdt-diff`, `gdt-index`
and `gdt-shot`. Screenshots still go through the driving agent's browser tool; there is
no `gdt run` yet, so the run steps below are done by hand in that order. Check
`fidelity-tests/INDEX.md` and `fidelity-tests/CORRECTIONS.md` before assuming anything.

## Configuration

The skill names no account, Drive folder, model or repository. Those live in
`fidelity-tests/config.yaml` (git-ignored; copy `config.example.yaml`): `account`
(always passed as `--account`; the default account may not see the fixtures),
`drive_root`, `issue_tracker`, and how to spawn the builder and task agents (default:
the current model via the Agent tool, with browser or gdoc access respectively).
Commit only when the calling project's instructions say to, on the branch they name.

## Layout

`fidelity-tests/` at the repo root mirrors the Drive tree under `drive_root`:

- `INDEX.md` (one row per fixture; `bin/gdt-index` regenerates it), `IDEAS.md`
  (untested mess and task angles), `repros.md` (one gdoc command per known failure —
  the agent-free regression suite), `config.yaml`.
- `<area>/v<NN>/` — `fixture.md` (URLs, frozen revision, created date), `prompt.md`
  (builder brief only), `built.md`, `tasks.md`, `baseline/`, `runs/<YYYYMMDD>-<slug>/`.
- Every capture set (`baseline/`, a run's `before/` and `after/`) holds `view-NN.jpg`,
  `structure.json`, `cat.md`, `comments.json`, `revisions.json`, `shot.json`. A run adds
  `transcript.md`, `diff.md`, `verdict.md`.

Fixture doc `gdt-<area>-v<NN>`; run copy `gdt-<area>-v<NN> run <YYYYMMDD> <slug>`. Area
is one lowercase word (`text`, `lists`, `tables`, `objects`, `layout`, `chips`,
`collab`, `kitchen-sink`). A new version is a new doc; never edit a fixture.

## Fixtures

Ask for mess, not features; one builder agent per document, in its own browser tab;
freeze with a named version; capture the baseline. The full recipe, the prompt
template, the browser safety rules and the capture commands are in
[references/fixtures.md](references/fixtures.md). Read it before building or
baselining anything.

## Tasks

`tasks.md` holds five to ten requests per fixture, written the way a colleague would
ask. Two authors: the builder, aiming at its trap list, and a second agent that reads
the document cold. Do not filter by what the API can do; whether a failure is an API
limit or a CLI defect is decided at verdict time.

Every task has five fields, and a run cannot start until all five are present:

- **Request** — the natural-language ask, verbatim. This is all the task agent sees.
- **Expected** — what the document should contain afterwards, precisely enough that
  a judge can check it without interpreting the request. Hidden from the task agent.
- **Target** — a structural locator for what should change: tab, paragraph text or
  heading, table cell, comment id. Everything outside it is protected.
- **Allowed** — secondary changes that are not collateral: automatic list renumbering,
  repagination, a `modifiedTime` bump, the revision list growing. Default is none.
- **Preconditions** — features the copy must still have for the task to mean anything
  (the pending suggestion, the comment, the chip). Lost in copying → the run is INVALID.

Include at least one task that needs a correct read to do at all, one that rewrites a
whole section, one adjacent to an object the API cannot create, one whose target
phrase also appears elsewhere, and one you expect to be impossible.

## Running a task

Two tracks, reported separately, so an agent's mistake never reads as a CLI regression:

- **Command track** — you run one named gdoc command on the copy and check that it
  makes only the declared mutation. This is what `repros.md` reruns.
- **Agent track** — a fresh agent gets only the request and the copy's URL and picks
  its own commands. Spawn it with an empty working directory: it must not be able to
  read `built.md`, `tasks.md` or this skill. It must report what it did and whether it believes it succeeded;
  save its report and every command as `transcript.md`.

The steps, in order, with the gate each one must pass:

1. **Source check.** `gdoc structure` of the fixture matches `baseline/structure.json`
   after normalisation, and the frozen revision is still listed by `gdoc revisions`.
   Otherwise stop: the fixture has drifted; build a new version.
2. **Copy.** If the task's preconditions mention comments or suggestions, copy in the
   Docs UI: File > Make a copy, tick "Copy comments and suggestions", untick "Share it
   with the same people", then `gdoc mv` the copy into the fixture's `runs/` folder.
   `gdoc cp` (Drive `files.copy`) silently drops both, so use it only when neither is
   needed. Record the copy's id.
3. **Precondition check.** Every feature the task's preconditions name is present in
   the copy (`gdoc comments --all`, `gdoc structure`, a screenshot for suggestions).
4. **Before capture** of the copy, every capture file. Record the copy's latest revision
   id, the `gdoc --version`, and the account.
5. **Edit** on the chosen track.
6. **After capture**, every capture file. Its revision must be later than the before
   revision on the same copy id.

A failed gate produces `verdict.md` with outcome INVALID and the gate that failed. It
never produces a partial verdict, and it does not count in any rate.

## Judging

Two judges, and they must agree; disagreement goes to a human.

**Structural diff** — `bin/gdt-diff before/ after/ --task tasks.md#<slug>` normalises
both structure dumps, lists every changed property with a stable path, classifies each
against the task as **expected**, **allowed** or **unexpected**, tags it **visible** or
**invisible**, and says whether visual review is needed and why. It also diffs `cat.md`
and `comments.json`. The normalisation policy and output schema are in
[references/diff.md](references/diff.md). The diff does most of the judging; its
unexpected items are collateral by definition.

**Visual** — Google Docs screenshots, never PDF export, so comments, suggestion colours
and chips appear as a reader sees them. Used only where the diff says structure cannot
settle it (a chip's rendered value, a suggestion's colour, a repaginated page), plus a
thumbnail sweep of the whole document. Procedure and the judge prompt are in
[references/capture.md](references/capture.md). Model judgements record model,
prompt and response verbatim.

## Outcomes

One outcome per run, recorded in `verdict.md` with the fields in
[references/verdict.md](references/verdict.md):

| Outcome | Meaning | Completion rate | Safety rate |
|---|---|---|---|
| **DONE** | Expected change present, no unexpected diff items | counts | counts |
| **DECLINED-API** | Agent refused; the Docs API cannot express the request (check the API reference, not gdoc's help) | no | counts |
| **GAP-CLI** | Agent refused or could not; the API can, gdoc cannot | no | counts |
| **FAIL-AGENT** | gdoc could; the agent did the wrong thing or nothing, without damage | no | counts |
| **COLLATERAL** | Unexpected diff items, whether or not the request was met | no | no |
| **INVALID** | A gate failed: fixture drift, lost preconditions, capture or revision error | excluded | excluded |

Two headline numbers, never one: **completion** = DONE over valid runs; **safety** =
everything but COLLATERAL over valid runs. A refusal is a good safety result and a bad
completion result, and the index shows both.

COLLATERAL also records whether the damage was visible or invisible, and whether the
agent's own read afterwards would have revealed it. The silent case matters most: so
far every corruption came with "OK replaced 1 occurrence".

## Reduce and file

Isolation comes after failure, never before.

1. Find the single gdoc command that reproduces the damage on the fixture; append it
   to `repros.md` with the fixture, the outcome and the date.
2. If the cause is unclear, build a small isolation fixture (`gdt-iso-<slug>-v01`) with
   only the construct involved and rerun the command there. The CLI can often create
   these.
3. If the cause is the CLI, open an issue on the configured tracker (check duplicates)
   and link it from the verdict, the repro and
   [references/known-cli-behaviours.md](references/known-cli-behaviours.md). Every
   entry there points at a repro line or an issue; entries with neither get deleted.

## Self-test

The harness contract, so the scripts get written to it and the skill can be checked
in one go once they exist:

```
bin/gdt doctor                                  # config, account, gdoc version, browser
bin/gdt validate-fixture fidelity-tests/<area>/v<NN>   # five task fields, baseline complete, frozen revision present
bin/gdt run <area>/v<NN> <task-slug> [--track command|agent]
bin/gdt index
```

Until then, validate the skill itself with the skill-creator validator and check
`INDEX.md` by hand after each run.
