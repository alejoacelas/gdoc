# Ideas for fixtures and tasks

Untested angles. Take from here when writing a prompt or a task list; strike through what
has been built. The baseline mess every fixture must carry (emoji in headings, Word paste,
fake headings, manual numbering, a repeated phrase, a comment across a formatting boundary)
lives in the skill and is not repeated here.

Two kinds of idea. A **top-up** is bolted onto an existing task by tweaking the fixture or
rewording the request; it makes any test harder. An **own test** needs its own fixture
design or its own procedure. When a top-up keeps producing failures, promote it to an own
test.

## Top-ups (apply to any task)
- Repeat the same edit three times on one paragraph and diff the final state against the
  baseline, so run-rewriting decay shows up as a rate rather than a one-off.
- Plant a near-duplicate of the target that differs only by case, curly versus straight
  quotes, or en dash versus hyphen.
- Put an emoji or other non-BMP character earlier in the same paragraph as the target.
- Relocate the target inside a link, a bold run, a heading's first word, a table cell, a
  footnote, or a header.
- Move the target into a non-first tab and name the tab only in the request.
- Ask for the same edit as a suggestion instead of a direct change.
- Run the task as an account with comment-only access.
- Phrase the request the vague way a colleague would, then the precise way, and compare.

## Own tests (fixtures outside the skill's area list)
- Cat-blind fixture: every trap is invisible to `gdoc cat` and only shows in structure
  or screenshots, so a PASS-looking run can hide damage.
- Multi-tab fixture: three tabs plus a nested child, the same phrase in two tabs,
  comments in a non-first tab.
- Long document: fifty-plus pages with repeated tables, so locating the target is the
  hard part.
- Two agents editing the same copy at once, to exercise conflict detection.
- Fixtures copied from real internal docs on the work account, never committed.

## Notes for the area fixtures (beyond the skill's baseline)
- collab: comments to reply to, resolve and reopen; suggestions to accept, reject and
  suggest inside of; a resolved comment on text that has since changed.
- chips: tasks that need a correct read before any edit, such as ticking the third
  checklist item or changing a dropdown or date chip.
- lists: a numbered list that becomes a checklist halfway; insert a paragraph between two
  list items.
- objects: edits adjacent to drawings, images, footnotes, headers and footers; one request
  the API cannot express, such as resizing a drawing.

## Suite procedure
- Seeded-damage calibration: hand-corrupt a run copy in the browser with no task (drop a
  bold run, retarget a link, merge two list items) and feed it through both judges. Any
  seeded change a judge misses is a false-negative rate every PASS in the index inherits.

## Struck
- ~~Add a suggestion as an example of something the API cannot do~~ — `gdoc suggest`
  exists since PR #53; it is now a task, not an impossibility.
