# gdt-text-v01 — prompt

I'm testing a CLI against this doc, so build a document that uses a bunch of the
formatting and functionality available in Google Docs for **inline text**, the way a real
internal doc looks after several people have pasted into it for months. Use browser
control and pick things you think will be hard to replicate for a tool connected through
the Docs API. Make it messy rather than a feature demo: combine at least two of these in
most paragraphs.

- one phrase that appears five times: bold, italic, inside a link, in a heading, and in
  plain text; plus a near-duplicate that differs only by case
- twins that differ only by curly vs straight quotes, en dash vs hyphen vs em dash,
  ellipsis character vs three dots, non-breaking space vs space
- one paragraph with four fonts and three sizes, as pasted from Word, Slack and a web page
- bold 14pt Normal text imitating a heading, directly above and below real headings;
  a real heading whose text is also bold+underlined by direct formatting
- superscript and subscript inside a word (H₂O, x², a typed `[1]` next to a real footnote)
- highlight colours, coloured text, strikethrough that spans a formatting boundary,
  small caps, a run of underline that includes the trailing space
- a link whose visible text differs from its URL; a bare URL that Docs auto-linked; a link
  split across two runs of different formatting
- emoji mid-word, a combining-accent character, Japanese and Cyrillic mid-sentence,
  right-to-left text (Arabic or Hebrew) in one paragraph
- empty paragraphs carrying bold/heading formatting, trailing spaces, tabs for alignment,
  two spaces after a full stop, a paragraph that is just a tab
- a comment anchored across a formatting boundary; a pending suggestion that replaces one
  word with a differently-formatted word
- line spacing, indentation and alignment changed on individual paragraphs
- anything else about inline text you find hard to do

Two to three pages is plenty. Write real-sounding content (a policy memo, a product
announcement draft, a style guide), not lorem ipsum.
