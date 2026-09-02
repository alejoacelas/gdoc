# Screenshots and the visual judge

## Why screenshots

Always Google Docs screenshots, never PDF export. Export drops comments, suggestion
colours, chip rendering and the pagination a reader sees.

## Procedure (`bin/gdt-shot DOC out/`)

- Same browser window size every time (record it in `out/shot.json`), 100% zoom, print
  layout on, comments sidebar open, suggestions shown inline.
- Scroll page by page; one PNG per page, `page-01.png` onwards, full resolution.
- Before and after are captured from the **same copy**, so pagination starts identical
  and a shift means the edit moved something.
- Write `out/shot.json`: doc id, revision id at capture, window size, zoom, page count,
  timestamp. A capture without `shot.json` is incomplete and the run is INVALID.

## When the visual judge runs

Only for diff items the structural diff flags `needs_visual_review`, plus one sweep of
the whole document as thumbnails. Typical reasons: a chip whose rendered value is not in
the structure dump, a suggestion whose state only shows as colour, a repagination that
may or may not have moved a floating object.

## Judge prompt

For each flagged item, crop the matching region from before and after at full
resolution. Give the model: the task's **Request** and **Expected** fields, the crop
pair, and then the full pages as thumbnails. Ask exactly:

> Is the expected change present in the after image? Does anything else differ between
> before and after, other than what the task lists as allowed? Answer for each question
> with yes, no or cannot tell, then explain what you see. Reason from the content of the
> crops, not from their pixel position; a line-break shift moves everything below it.

Record in `verdict.md`: model id, the prompt as sent, the response verbatim, and which
crops were shown. "Cannot tell" sends the run to a human.
