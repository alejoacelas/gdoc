# gdt-collab-v01 — prompt

I'm testing a CLI against this doc, so build a document that uses a bunch of the
formatting and functionality available in Google Docs for **collaboration** (comments and
suggestions), the way a real internal doc looks after several people have reviewed it for
weeks. Use browser control and pick things you think will be hard to replicate for a tool
connected through the Docs API. Make it messy rather than a feature demo; the body text
should carry the usual mess (emoji in headings, a fake bold 14pt heading, a phrase
repeated with different formatting, one table, one list).

- five or more comments: one anchored across a formatting boundary (bold → plain), one on
  a whole paragraph, one on a single word inside a link, one inside a table cell, one on a
  list item; one of them with a reply thread of two replies
- a resolved comment whose anchored text was edited after it was resolved
- a comment whose anchored text was deleted (so it is orphaned)
- pending suggestions of every kind: an insertion, a deletion, a replacement, a formatting
  change (make a word bold in suggesting mode), a suggested new list item, a suggestion
  inside a table cell, two adjacent suggestions on the same sentence
- a suggestion that overlaps a comment anchor
- an accepted suggestion and a rejected one (so revision history has them)
- the same phrase in three places, one of which is inside a pending suggestion
- an assigned action item comment ("@" is fine to type but do NOT pick a real person; if
  the picker insists on a person, skip the assignment)
- anything else about comments and suggestions you find hard to do

Switch back to Editing mode when done. Two pages is plenty. Write real-sounding content
(a draft blog post under review, a policy under discussion), not lorem ipsum.
