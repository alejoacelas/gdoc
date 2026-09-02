# gdt-objects-v01 — prompt

I'm testing a CLI against this doc, so build a document that uses a bunch of the
formatting and functionality available in Google Docs for **non-text objects**, the way a
real internal doc looks after several people have pasted into it for months. Use browser
control and pick things you think will be hard to replicate for a tool connected through
the Docs API. Make it messy rather than a feature demo; the body text should carry the
usual mess (emoji in headings, a fake bold 14pt heading, a phrase repeated with different
formatting, one list).

- three footnotes: one on a heading word, one whose text contains a link and bold, one
  placed mid-word; a typed `[2]` next to a real footnote reference
- a header and a footer with page numbers, a different first-page header, text with a tab
  and right alignment in the footer
- two horizontal rules, one directly after a heading and one between two list items
- an inline image (Insert > Image > By URL, e.g. https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png) with alt text, and the same image again resized smaller; one image wrapped with text (not inline) if Docs lets you
- a drawing (Insert > Drawing > New: a box with text and an arrow) sitting between two
  paragraphs; a paragraph with the same phrase right before and right after it
- a page break, a section break (Insert > Break > Section break), a column layout on one
  section (Format > Columns, two columns) with text in both columns
- a bookmark and an internal link to it; a table of contents (Insert > Table of contents)
  that is already out of date because a heading was renamed after inserting it
- an equation (Insert > Equation) inside a sentence; a special character inserted via
  Insert > Special characters; an emoji reaction if available
- a comment anchored on the image; a pending suggestion that deletes a footnote reference
- anything else about objects you find hard to do

Two to three pages is plenty. Write real-sounding content (a research memo with figures,
a formatted report), not lorem ipsum. Switch back to Editing mode when done.
