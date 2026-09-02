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

<!-- The four tasks below were written by a second agent that read the document cold (CLI only). -->

## fill-empty-vendor-row

- **Request:** Add Globex to the vendor table — 3,200 a quarter, Priya to sign the SOW, status approved (Aprobado ✅, same as Acme). There's an empty row at the bottom you can use.
- **Expected:** Table 1 still has exactly 6 rows and 4 columns. Row 5 reads: [5,0] `Globex`, [5,1] `3,200`, [5,2] `Sign SOW (Priya)`, [5,3] `Aprobado ✅`. Bold on [5,1] is optional (the empty cell carried a bold run); [5,2] may be plain text or a third item of the numbered list shared by [1,2] and [2,2] — either is fine. Header cell [0,1] `Cost (GBP) & owner` still spans 2 columns; [3,2] still spans 2 rows; the pending suggestion in [2,1] (`12,950` inserted, `12,750` deleted) is still pending; the comment on `shared between Ops and Finance` is still open. The intro sentence still says `across three suppliers`. Nothing else changes.
- **Target:** tab `Tab 1`, table 1, cells [5,0], [5,1], [5,2], [5,3].
- **Allowed:** revision list grows; `modifiedTime` changes; the numbered list used by [1,2] and [2,2] may gain a third item.
- **Preconditions:** table 1 has an all-empty sixth row (index 5); [0,1] has `columnSpan: 2`; [3,2] has `rowSpan: 2`; the suggestion in [2,1] is unresolved.

## merged-owner-cell-interim

- **Request:** In the vendor table, the owner cell that straddles Northwind and Contoso: swap "Owner TBD" for "Owner: Ops (interim)" and keep the rest of the sentence as is.
- **Expected:** Table 1 cell [3,2] reads exactly `Owner: Ops (interim) — shared between Ops and Finance until the Contoso decision lands` (em dash preserved). The cell still has `rowSpan: 2` covering rows 3 and 4; the table is still 6×4 and [4,2] is still the covered/empty position. Comment `#AAACGePZQas` ("Who actually owns this line? …") is still open and its anchor text `shared between Ops and Finance` is still present in that cell. The pending suggestion in [2,1] is still pending. Nothing else changes.
- **Target:** tab `Tab 1`, table 1, cell [3,2].
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** [3,2] has `rowSpan: 2`; an open comment anchored on `shared between Ops and Finance`; a pending suggestion in [2,1].

## datawise-status-approved

- **Request:** Datawise cleared legal on Friday. Update its status in the vendor table to Aprobado ✅ (same as Acme).
- **Expected:** Table 1 cell [2,3] reads exactly `Aprobado ✅` (the italic `pending legal review` run is gone; no italics remain in the cell). The phrase `pending legal review` still appears twice elsewhere, unchanged: in the intro paragraph (`two contracts are still pending legal review`) and in bold inside the yellow callout (table 2, `every Contoso number in this doc is **pending legal review** until Sarah signs off.`). In the same row, [2,1] still carries the pending suggestion (`12,950` as suggested insertion, `12,750` as suggested deletion — neither accepted nor rejected) and [2,2] is still the numbered-list item `Renew NDA (Tomás)`. Nothing else changes.
- **Target:** tab `Tab 1`, table 1, cell [2,3].
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** [2,3] contains `Pendiente: ` followed by an italic `pending legal review`; the suggestion in [2,1] is unresolved; `pending legal review` also occurs in the intro paragraph and bold in table 2.

## data-engineer-owner-handover

- **Request:** Priya's off the data engineer search, Tomás is running it now — can you update the doc?
- **Expected:** Table 3 cell [1,3] reads `Tomás. JD on Notion`, where `JD on Notion` is still a hyperlink to `https://www.notion.so/ops/jd-senior-data-engineer` with its underline and link colour intact; only `Priya` became `Tomás`. Table 3 cell [1,1] still holds the smart-chip/dropdown that renders as `In progress`; [1,2] still has the nested bullets `Schedule panel` › `Book room 4B`, `Send take-home`. Table 1 cell [1,2] still reads `Sign MSA (Priya)` — that Priya is the vendor MSA owner, not the search. Table 4 (`Prepared by` / `Reviewed by`) is unchanged. Nothing else changes.
- **Target:** tab `Tab 1`, table 3, cell [1,3].
- **Allowed:** revision list grows; `modifiedTime` changes.
- **Preconditions:** [1,3] contains `Priya. ` followed by the `JD on Notion` link; [1,1] contains a non-text chip element (no `textRun`) rendering `In progress`; `Priya` also occurs in table 1 [1,2].
