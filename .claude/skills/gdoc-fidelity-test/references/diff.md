# Structural diff: normalisation and output

`bin/gdt-diff before/ after/ --task tasks.md#<slug>` is the primary judge. It compares
`structure.json`, `cat.md` and `comments.json` and classifies every difference against
the task's Target and Allowed fields.

## Normalisation

Drop only what changes on every save and carries no meaning:

- `revisionId`, `documentId`, `suggestionsViewMode`
- `startIndex` / `endIndex` — but keep paragraph **order** and each paragraph's
  **length**; a length change is a real change
- comment `htmlContent`; comment `modifiedTime` is kept but classified `allowed` when
  the task's Allowed field says so (it differs even between a fixture and a fresh copy)

Keep everything else, in particular things that look invisible but are damage:

- `listId` and nesting level — same-looking numbering on a different list is a change
- named range and bookmark ids — link targets break silently
- comment `anchor` and `quotedFileContent` — an anchor that moved is a change
- inline object ids and their `objectId` references in the body
- `namedStyleType` behind identical direct formatting
- link `url`, header/footer ids, tab ids

`bin/gdt-diff` implements this; it also has a tiny locator language for Target (`table N,
cell [r,c]`, ``paragraph beginning `X` ``, `comment`). Normalisation has its own tests: a fixture pair where only an id changed must produce
an item, and a pair where only indices shifted after an earlier insertion must not.

## Paths

Every item has a stable semantic path, so a run can be compared to a previous run of
the same task: `tab[<title>]/para[<n>:<first 30 chars>]/runs[<k>].textStyle.bold`,
`tab[..]/table[<n>]/cell[r,c]/para[..]`, `comments[<id>].resolved`,
`namedRanges[<name>]`. Paragraph numbers are positions in the normalised body; the text
prefix disambiguates when order changes.

## Output (`diff.json`, rendered to `diff.md`)

```json
{
  "task": "repeated-phrase",
  "items": [
    {
      "path": "tab[Main]/para[14:Budget for Q3 is]/runs[2].content",
      "before": "£12,000", "after": "£14,000",
      "class": "expected",            // expected | allowed | unexpected
      "visible": true,
      "needs_visual_review": false
    },
    {
      "path": "tab[Main]/para[14:Budget for Q3 is]/runs[1].textStyle.bold",
      "before": true, "after": null,
      "class": "unexpected",
      "visible": true,
      "needs_visual_review": false,
      "note": "bold dropped on the run before the target"
    }
  ],
  "cat_diff": "…unified diff…",
  "comments_diff": [],
  "needs_visual_review_reasons": [],
  "summary": {"expected": 1, "allowed": 0, "unexpected": 1, "visible_unexpected": 1, "invisible_unexpected": 0}
}
```

**Classification.** An item is `expected` if its path is inside the task's Target and
its after-value matches Expected; `allowed` if it matches an Allowed pattern (list
renumbering, revision list growth, `modifiedTime`); otherwise `unexpected`. Any
`unexpected` item makes the run COLLATERAL. Zero `expected` items with the Target
unchanged means the request was not met.

**Visible vs invisible.** Invisible covers link targets, bookmarks, comment anchors,
named style behind identical-looking formatting, list identity behind identical
numbering. It is recorded per item so COLLATERAL can say which kind it was.
