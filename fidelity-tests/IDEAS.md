# Ideas for fixtures and tasks

Untested angles. Take from here when writing a prompt or a task list; strike through what
has been built.

Two kinds of idea. A **top-up** is bolted onto an existing task by tweaking the fixture
or rewording the request; it makes any test harder. An **own test** needs its own fixture
design or its own procedure. When a top-up keeps producing failures, promote it to an own
test.

## Top-ups (apply to any task)
- Repeat the same edit three times on one paragraph and diff the final state against the
  baseline, so run-rewriting decay shows up as a rate rather than a one-off.
- Plant the target phrase a second time elsewhere in the document with different
  formatting, once inside a link.
- Plant a near-duplicate that differs only by case, curly versus straight quotes, or en
  dash versus hyphen.
- Put an emoji or other non-BMP character earlier in the same paragraph as the target.
- Anchor a comment or a pending suggestion across the target's boundary.
- Paste the target paragraph from Word or Slack so it carries three fonts and sizes.
- Put bold 14pt Normal text imitating a heading next to the real heading the task names.
- Surround the target with empty paragraphs carrying formatting, trailing spaces, tabs
  used for alignment, and a manual "1)" typed next to a real list.
- Move the target into a non-first tab and name the tab only in the request.
- Ask for the same edit as a suggestion instead of a direct change.
- Run the task as an account with comment-only access.
- Phrase the request the vague way a colleague would, then the precise way, and compare.

## Own tests (need their own fixture or procedure)
- Cat-blind fixture: every trap is invisible to `gdoc cat` and only shows in structure
  or screenshots, so a PASS-looking run can hide damage.
- Multi-tab fixture: three tabs plus a nested child, the same phrase in two tabs,
  comments in a non-first tab.
- Suggestions fixture: pending suggestions to accept, reject, and suggest inside of,
  now that gdoc can author them; plus a resolved comment on text that has since changed.
- Chips and checklist fixture: tasks that require a correct read before any edit is
  possible, such as ticking the third item, changing a dropdown, or editing a date chip.
- Lists and tables fixture: a numbered list that becomes a checklist halfway, nested
  bullets and a chip inside a table cell, emoji and non-Latin text in headings and cells;
  tasks insert a paragraph between two list items and rewrite a whole section.
- Objects fixture: drawings, images, footnotes, headers and footers, with edits adjacent
  to each and one request the API cannot express, such as resizing a drawing.
- Long document: fifty-plus pages with repeated tables, so locating the target is the
  hard part.
- Two agents editing the same copy at once, to exercise conflict detection.
- Fixtures copied from real internal docs on the work account, never committed.

## Suite procedure
- Seeded-damage calibration: hand-corrupt a run copy in the browser with no task (drop a
  bold run, retarget a link, merge two list items) and feed it through both judges. Any
  seeded change a judge misses is a false-negative rate every PASS in the index inherits.

## Struck
- ~~Add a suggestion as an example of something the API cannot do~~ — `gdoc suggest`
  exists since PR #53; it is now a task, not an impossibility.
