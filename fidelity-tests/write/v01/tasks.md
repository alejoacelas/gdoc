# Tasks — gdt-write-v01

One task, command track. The fixture's only trait is the bullet on the tab's terminal empty
paragraph (see built.md); the task is the plain rewrite that trips over it.

## rewrite-tab-after-ui-bullet

- **Request:** Replace the whole "Repro" tab with the contents of rewrite.md (a heading, a
  plain paragraph, a two-item bullet list, a closing plain paragraph). Command track:
  `gdoc write --tab Repro <copy> rewrite.md`.
- **Expected:** The tab reads, in order: HEADING_1 `Rewritten heading`; NORMAL_TEXT `Plain
  paragraph after the heading.`; list items `first bullet` and `second bullet`; NORMAL_TEXT
  `Closing plain paragraph.`. Only the two list items carry a `bullet`; the heading and the
  plain paragraphs have no list indent.
- **Target:** tab `Repro`, whole body.
- **Allowed:** revision list grows; `modifiedTime` changes; a new `listId` for the new list;
  empty paragraphs between blocks (gdoc's markdown writer emits them).
- **Preconditions:** the tab's terminal (last, empty) paragraph carries a `bullet`
  (`build.sh` creates it; the Docs UI leaves one whenever a list is the last thing typed).
