# gdt-tables-v01 — prompt

I'm testing a CLI against this doc, so build a document that uses a bunch of the
formatting and functionality available in Google Docs for **tables**, the way a real
internal doc looks after several people have pasted into it for months. Use browser
control and pick things you think will be hard to replicate for a tool connected through
the Docs API. Make it messy rather than a feature demo: combine at least two of these in
most cells.

- a table with merged cells (a header spanning two columns, a cell spanning two rows)
- nested bullets two levels deep inside one cell; a numbered list that spans two cells
- a link, a date chip and a dropdown chip inside cells; a checkbox list inside a cell
- a cell whose text has three fonts and sizes (pasted from Word); a cell with a heading style
- a column of numbers where one is text (`n/a`), one has a trailing space, one is a
  formula-looking string like `=SUM(B2:B4)`
- the same figure appearing in two cells and once in prose, one of them bold
- a two-row table used purely for layout (no borders), a one-cell table used as a callout
  with a background colour, and a real data table with a pinned header row
- emoji and non-Latin text (Japanese, Cyrillic, Spanish accents) in cells and column headers
- a comment anchored to a cell's contents; a pending suggestion that changes a cell value
- an empty row, an empty cell that carries formatting, tabs inside a cell, a cell with a
  soft line break, a table right after a heading with no paragraph between
- a tiny 1×1 table nested inside another table's cell, if Docs lets you
- anything else about tables you find hard to do

Two to three pages is plenty. Write real-sounding content (a hiring pipeline, a vendor
comparison, a quarterly budget), not lorem ipsum.
