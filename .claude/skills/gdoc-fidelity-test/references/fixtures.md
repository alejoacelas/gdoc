# Building and baselining a fixture

## Ask for mess, not features

Isolated feature demos are too clean. Real documents are pasted together over months by
several people, and that is where tools break. Every fixture, whatever its area, carries
a baseline of mess, and the prompt says so. Ask the builder for things like:

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
- whatever the builder finds hard to do; aim for "hard to reproduce through the API",
  and combine at least two such features per paragraph

`fidelity-tests/IDEAS.md` has more; take from it and strike through what gets built.

## Prompt template

`prompt.md` is the brief handed to the builder and nothing else — no URLs, no account.
Those go in `fixture.md`. The brief that worked:

> I'm testing a CLI against this doc, so build a document that uses a bunch of the
> formatting and functionality available in Google Docs for <area>, the way a real
> internal doc looks after several people have pasted into it for months. Use browser
> control and pick things you think will be hard to replicate for a tool connected
> through the Docs API. Make it messy rather than a feature demo: combine at least two
> of these in most paragraphs. <list> Two to three pages is plenty. Write real-sounding
> content, not lorem ipsum.

The runner supplies the doc URL and account from `fixture.md` and `config.yaml` when
spawning the builder.

## Build rules: one doc, one agent

Every incident so far came from agents sharing a document: keystrokes in another
agent's tab, a stray select-all wiping a shared tab, an undo removing someone else's
work, a click landing on the wrong paragraph after a concurrent edit reflowed the page.

- One builder agent per fixture, in its own browser tab. It never opens another test
  doc.
- Before typing: screenshot, confirm the tab and caret. Menus, popups and `cmd+f` steal
  focus; use the menu-search box instead of shortcuts like `cmd+Return`.
- Never select-all in a document with anything worth keeping. Never undo past your own
  last action.
- Anything written into a shared document goes through the CLI, not the browser.

## built.md

When done, the builder writes `built.md`: the exact text, what formatting sits where,
what it tried and could not do, every autocorrection Docs made (capitalisation, curly
quotes, `--` to a dash, `1.` to a list), and a **trap list**: the places it thinks an
API edit is most likely to damage. It is a reading aid for the judge and a source of
tasks, not a contract.

## fixture.md

Durable metadata, separate from the brief:

```
doc: https://docs.google.com/document/d/<id>/edit
folder: https://drive.google.com/drive/folders/<id>
frozen_revision: frozen            # the named version
frozen_revision_id: <from gdoc revisions --json>
created: YYYY-MM-DD
gdoc_version: <gdoc --version at baseline>
```

## Freeze and baseline

Name the version in the browser (File > Version history > Name current version,
`frozen`). Google prunes unnamed revisions within hours. Then:

```
bin/gdt-shot DOC baseline/                                   # see capture.md
gdoc structure --account $A DOC > baseline/structure.json
gdoc cat --account $A DOC > baseline/cat.md
gdoc comments --all --account $A DOC --json > baseline/comments.json
gdoc revisions --account $A DOC --json > baseline/revisions.json
```

Then re-run `gdoc structure` once more and confirm it is byte-identical to the first
dump. If it is not, something is still editing the doc; wait and repeat.
