# Tasks — gdt-tables-v01

Five fields each; see the skill's Tasks section. Slugs are the run directory names. Tables are
numbered in document order from 1: table 1 vendor comparison (6×4, header merge [0,1]+[0,2],
vertical merge [3,2]+[4,2]), table 2 callout (1×1), table 3 hiring pipeline (5×4), table 4
sign-off layout (2×2, borders 0pt). Cells are [row,col] from 0 as the Docs API indexes them
(merged-away cells still exist and are empty).

## acme-cost-49000

- **Request:** Acme Cloud's Q3 cost went up to 49,000 — can you update the vendor table?
- **Expected:** Table 1 cell [1,1] reads `49,000`, still bold. The `48,500` in the intro
  paragraph and in the callout (table 2) are unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, table 1, cell [1,1].
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** cell [1,1] reads `48,500` in a bold run; `48,500` occurs three times in
  the document.

## northwind-quote

- **Request:** Northwind finally sent the revised quote: 9,800. Put that in the vendor table
  where it says n/a.
- **Expected:** Table 1 cell [3,1] reads `9,800` in default style. The intro sentence `one
  figure below is n/a until Northwind sends the revised quote` is unchanged. The merged owner
  cell [3,2] and the comment anchored inside it are unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, table 1, cell [3,1].
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** cell [3,1] reads `n/a`; `n/a` also occurs in the intro paragraph.

## contoso-status-approved

- **Request:** Contoso got approved after all. In the vendor table set its status to
  "Aprobado ✅", same as Acme.
- **Expected:** Table 1 cell [4,3] reads `Aprobado ✅`. The vertically merged owner cell
  [3,2] (rowSpan 2, text `Owner TBD — shared between Ops and Finance until the Contoso
  decision lands`) is unchanged and the comment anchored on `shared between Ops and Finance`
  is still open with the same quoted text. Cell [1,3] unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, table 1, cell [4,3].
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** cell [4,3] reads `Отклонено ❌`; cell [3,2] has rowSpan 2; the comment
  with `quotedFileContent` `shared between Ops and Finance` exists in the copy.

## remove-empty-vendor-row

- **Request:** There's an empty row at the bottom of the vendor comparison table — please
  delete it.
- **Expected:** Table 1 has 5 rows (row 5 removed); rows 0–4 unchanged including both merges
  and the pinned header; the paragraph after the table (`Datawise is the only vendor…`)
  unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, table 1.
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** table 1 has 6 rows and row 5 is empty with bold on cell [5,1].

## ops-coordinator-start-date

- **Request:** The Ops coordinator start date in the hiring pipeline is confirmed now — drop
  the "(tbc)" after it.
- **Expected:** Table 3 cell [2,3] reads `Tomás; start ` followed by the date chip `2 Sept
  2026` and nothing after it (no trailing space is fine either way). The date chip
  (`dateElement`) is intact. Nothing else changes.
- **Target:** tab `Tab 1`, table 3, cell [2,3].
- **Allowed:** a trailing space before the paragraph end may remain or go; revision list
  grows; `modifiedTime` changes.
- **Preconditions:** cell [2,3] contains a `dateElement` followed by ` (tbc)`.

## paused-until-q1

- **Request:** Recruiter row in the hiring pipeline: it's paused until Q1 now, not Q4.
- **Expected:** Table 3 cell [3,2] reads `Paused until Q1, see budget` with its three runs
  intact: `Paused` Courier New 9pt, ` until Q1, ` Arial 11, `see budget` Georgia 14pt. Nothing
  else changes.
- **Target:** tab `Tab 1`, table 3, cell [3,2].
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** the cell has three runs with those fonts.

## reply-owner-comment

- **Request:** Someone asked in a comment who owns the Northwind line. Reply "Finance
  confirmed on 2 Sept — it's Ops." but leave the comment open.
- **Expected:** The comment anchored on `shared between Ops and Finance` has one reply with
  exactly that text and is not resolved. The document body is byte-identical (structure diff
  empty; the pending suggestion in cell [2,1] still pending).
- **Target:** comment.
- **Allowed:** comment `modifiedTime` changes; revision list grows.
- **Preconditions:** the open comment with `quotedFileContent` `shared between Ops and
  Finance` exists in the copy; pending suggestion present.
