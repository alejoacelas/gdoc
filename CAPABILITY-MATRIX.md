# Markdown task routes and shared interfaces

The product contract applies equally to CLI and MCP: reliable requested Markdown changes, then agent simplicity, then whole-task completion time. The general route is a complete native Markdown read of a selected tab, modification of that Markdown, and a revision-pinned native replacement of that tab. Targeted edits retain richer neighbors. Default reads identify their first-tab scope; sibling tabs are never implicitly collapsed.

## Integration choice

Modify the existing combined fixes at `90c10f0`, compared with upstream `dbfa4c3`. Retain range/Unicode targeting, single-send transport, revision-pinned staged writes, comment outcomes and meaningful regression tests. Extend representation and remove obsolete core refusal expectations. Selective rebuilding would reassemble those same intertwined safety layers before addressing the missing capabilities. Historical PR packaging does not constrain implementation.

## Task routes

| Tasks | Route and representation | Required evidence |
| --- | --- | --- |
| T01, T05, T13 | Targeted native edits; parsed inline styles with exact UTF-16 ranges. General rewrite only when requested. | Requested styles/text plus untouched supported and richer neighbors; no automatic rich rewrite. |
| T02, T03 | Native tab replacement of revised Markdown; paragraph boundaries and all moved blocks reconstructed. | Split/merge/move task success alongside protected sibling tabs. |
| T04, T08 | Shared native exporter/parser for default and selected-tab Markdown; code, quotes and rules retain explicit identity. | Changed combination round trip as well as unchanged content; literal code/fences/whitespace. |
| T06 | Native list requests, nesting tabs and explicit parsed starts; native list semantics retained. | Mixed nesting, empty items, starts/restarts and displayed order. API-limited numbering must be reported separately. |
| T07 | Rectangular TableData plus column alignments; native table stages and inline cell formatting. | Row/column changes and semantic headers; no incidental header bolding during unrelated edits. |
| T09 | One exact-ID-first, ambiguity-checking resolver shared by all routes. | Same selection through CLI and MCP, including ID/title collisions. |
| T10, T12 | Per-tab content exposure pinned to Docs revisions; mutation responses carry acknowledged revisions. | Own successive writes, foreign edit, lost response, metadata/partial/full-read counterexamples. |
| T11 | Complete raw structure plus existing scoped selectors; complete export and explicit truncation metadata. | Actual locating and inspection task burden, without arbitrary default caps. |
| T14 | Parsed image references and native image operations; refresh existing references against current snapshot. | Insert/replace/move/remove and unrelated rewrite preservation; source limitations explicit. |
| T15 | Existing single-send comment routes and deterministic normalized matching. | Unicode-space annotation, early invalid-occurrence rejection, ambiguity/conflict outcomes. |

## Ownership and interface contract

1. Representation owner A owns `mdparse.py`, `lossy.py`, a new `markdown_export.py` if useful, and only the existing exporter helpers `flatten_tabs`, `_list_is_ordered`, `_style_run_markdown`, `_runs_markdown`, `_paragraph_markdown`, `_table_markdown`, `get_tab_text` in `api/docs.py`. Keep existing helper signatures compatible. A owns corresponding parser/export/loss tests.
2. Native owner B owns other `api/docs.py` mutation/selection helpers and native write operations in `api/drive.py`, plus their tests. Never edit A’s exporter helpers. Coordinator alone owns CLI, MCP, state, notifications, annotation, README and shared wiring. Acceptance owner C owns only `tests/acceptance/` and its synthetic fixtures.
3. Extend `ParsedMarkdown` additively. Images use `ImageData(plain_text_offset, uri, alt)` entries in `images`, with a single space placeholder in `plain_text`; offsets are Python code points before consumed nesting tabs, converted to UTF-16 at request generation. Add `removed_tabs_before` to image entries for native placement. Native replacement of each placeholder by an image preserves width. External Markdown image references use HTTP(S); exported existing objects may use a documented internal reference resolved only in the current document snapshot. No private image publication.
4. Extend `TableData` with `alignments: list[str | None]`, default empty for compatibility. Native table owner applies paragraph alignment to cells; exporter writes separator alignment. Cell text remains canonical inline Markdown. Header semantics must not require adding bold to existing unbolded text.
5. Code/quote/rule identity must survive changed writes. A defines canonical recognition and emits existing `StyleRange` annotations and, only if native style cannot disambiguate semantics, a narrowly scoped named-range representation. No general document framework. A must notify coordinator and B before any extra data-model or marker dependency.
6. Native result dictionaries add `input_revision_id`, `acknowledged_revision_id`, and `rebased`. Never substitute a later sampled Drive version for acknowledged content. B supplies these for general replacement and targeted edits; coordinator advances only previously exposed tab baselines matching the input revision and only without rebasing. A successful full tab replacement establishes that tab’s sent content baseline.
7. Coordinator stores `read_revision_ids` by tab. Complete native content reads set covered tabs to their snapshot revision; metadata, summaries and truncated reads do not. Writes compare selected-tab baseline with the guard snapshot and send that exact revision as `requiredRevisionId`. Explicit force can authorize a new overwrite snapshot, never an unpinned mutation.
8. Both interfaces use these shared handlers. MCP materializes inline Markdown temporarily and rejects host-local file references; equivalent image tasks need URL/reference inputs and cannot depend on shell-only commands.

## Phase 0 uncertainties

Official API feasibility review is in progress for list starts/restarts, mixed native list presets and image retrieval/reuse. Dependent implementation must not claim these are solved or label code defects as API gaps. A verified gap requires current official references, credible alternatives, exact best reliable behavior, tests and an explicit user-visible shortfall. Independent acceptance preparation is underway.
