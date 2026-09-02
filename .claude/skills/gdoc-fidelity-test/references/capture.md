# Screenshots and the visual judge

## Why screenshots

Always Google Docs screenshots, never PDF export. Export drops comments, suggestion
colours, chip rendering and the pagination a reader sees.

## Procedure

The browser tool captures the viewport, not a page, so captures are **views** at fixed
scroll offsets. The driving agent does this with the claude-in-chrome tools:

1. Resize the window to 1440×1200 (`resize_window`; the viewport comes out ~1440×780).
   100% zoom, print layout on, outline panel collapsed, suggestions shown inline.
2. For offset in 0, 650, 1300, … until past `scrollHeight`: set
   `document.querySelector('.kix-appview-editor').scrollTop = offset` with
   `javascript_tool`, then `computer` → `screenshot` with `save_to_disk: true`.
3. `bin/gdt-shot OUTDIR [--step 650] <saved paths in order>` files them as
   `view-01.jpg …` and writes `shot.json` (views, step, window, zoom, timestamp).

Before and after are captured from the **same copy** at the **same offsets**, so any
shift in a view means the edit moved something. A capture set without `shot.json` is
incomplete and the run is INVALID.

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
