These tests exercise human editing tasks through real CLI dispatch and MCP
`tools/call`, with Google service boundaries replaced and socket connections
blocked. They intentionally fail on missing capabilities: no xfails or loss
consent turn a refusal into success. Production code is unchanged.

At product baseline `90c10f0`, the new suite has **38 passes and 41 failures**;
35 failures exercise existing gaps and six exercise the proposed heading/table
selectors. The full suite has **3,139 passes and those same 41 failures**:
all 3,101 existing tests still pass. The exact historical bindings select 485
passing existing cases. Scoped lint and the no-stubs check pass. These are
acceptance-preparation results, not a release-ready verdict.

Run from the repository root:

```sh
uv sync --extra dev
uv run pytest tests/acceptance -q --acceptance-results /tmp/acceptance.json
uv run python tests/acceptance/run_bindings.py --existing-only
uv run ruff check tests/acceptance
```

`finding-bindings.json` maps 38 historical families and 16 deferred items to
exact test functions and the assertions they establish. It also names gaps.
F8 is an observation rather than a demonstrated defect; D03 is a documentation
correction; D04 is test-library style. Those three deliberately have no runtime
fix assertion. `run_bindings.py` resolves parametrized cases and blocks sockets
for the existing tests too. It accepts extra pytest arguments after `--`.

`baseline-results.json` records the baseline product pin, test-file hashes,
individual outcomes and actual interface sequences. Captured output bodies are
omitted from that compact artifact; rerunning with `--acceptance-results`
retains them, including complete raw structure. Bytes count captured UTF-8
output and notes, not model tokens. Times are single-run offline Python timings,
not Google latency or agent reasoning time. `docs_api_attempts` counts mocked
Docs execute calls; `mocked_boundary_calls` separately counts Drive/comment
helper calls, not their internal HTTP attempts. No live API attempts occurred.

The fixtures are invented. `harbor-before.md` and `harbor-after.md` specify the
full combination and section-movement target for integration: retain the list,
formatted aligned table, code, quote, rule and image while moving Arrival,
changing one phrase and adding Sign-off. They are preparation fixtures, not
proof that the current writer can reconstruct that document. They deliberately
avoid prescribing unresolved native representation details or permanent image
URLs.

| Task | Executable evidence in test_workflows.py | Remaining evidence before full task closure |
| --- | --- | --- |
| T01 | Targeted wording beside heading/link/nested list; replay text and inspect untouched ranges | Native styled readback |
| T02 | Split and merge by rewrite; reuse existing UTF-16 text applier and reread simulated split | Paragraph-style preservation through native reconstruction |
| T03 | Moved/inserted section request order and bullets | Execute full table-containing movement fixture and reread structure |
| T04 | Changed and unchanged heading/link/emphasis/list reconstruction requests | Full combination fixture, including table/code/quote/rule/image, with native readback |
| T05 | Remove stale URL, apply combined emphasis and retarget URL using existing style-mask applier | Backend readback of styled result |
| T06 | Mixed list/empty item/start/restart rewrite sequence | Successful hierarchy/order result; agreed numbering best effort is still pending |
| T07 | Table creation, styled cell text and alignment requests against fixed post-insert snapshot | Actual row/column add/remove/reorder and final native table semantics |
| T08 | Literal fence with closed span, blank line, quote and rule write requests | Changed native code/quote/rule identity; CRLF parser probe is separate |
| T09 | Read/edit exact-ID precedence over title decoy | Case-collision native resolver has existing bindings; full interface ambiguity sequence remains |
| T10 | Successive own writes, foreign revision refusal, lost-response single send | Integrated acknowledged revision results; targeted edit advancement and push route |
| T11 | Raw/scoped output; heading discovery and format inspection within 400 paragraphs | Candidate direct target selector comparison and agent-driven timing |
| T12 | Prefix, other-tab and metadata exposure followed by rewrite; complete-read control | Integrated coverage schema and intentional force-overwrite counterpart |
| T13 | Local edit beside image/footnote and rich-footnote rebuild refusal | Native objects unchanged after execution; richer chips covered by existing native guards |
| T14 | Insert/move/replace/remove Markdown image sequences with invented native objects | Successful image requests/readback, source retrieval and current-snapshot reference reuse |
| T15 | Unicode annotation, ambiguous-quote refusal, zero-call invalid occurrence | Existing bindings cover normalized matching, deterministic occurrence and honest fallback; no new backend anchoring claim |

Text and style appliers are reused from the existing paragraph/style regression
files. They model only those request effects. The table test supplies one fixed
empty-table response for its fill stage; it is request evidence, not an emulator
or native end-result test. No test result in this directory establishes live
Google fidelity.

Measured baseline findings and proposed interfaces:

1. Raw structure for the two-tab fixture produces approximately 131 KB. Selecting
   its known short tab uses one command and approximately 400 bytes. Keep both
   routes; this does not justify changing the raw default.
2. Within one 400-paragraph tab, `toc --tab draft` locates the named heading in one
   command and approximately 280 bytes. Inspecting its paragraph style with
   `structure --tab draft` still emits approximately 134 KB. Optional
   `structure --heading TEXT` and `--table N` selectors are agreed for integration;
   new expectations require `document.revisionId`,
   `document.scope.complete: false`, selected native content and cross-tab
   heading ambiguity errors in both interfaces. A known
   target should not require a preliminary overview.
3. Prefix and metadata reads incorrectly permit whole writes on this baseline.
   The other-tab case refuses due to tab-collapse protection, which does not
   establish correct read provenance. Record covered tab IDs and revision from
   the content snapshot; neither metadata nor truncated output authorizes an
   unseen tab. Preserve explicit truncation and retrieval information.
4. The second different write after an acknowledged first write refuses unless
   reread. Advance only justified tab baselines from the mutation's input and
   acknowledged revisions; never infer authorship from a later Drive version.

Each T11 alternative requires one command when the tab or heading is known.
The combined heading-discovery-plus-style-inspection sequence requires two.
T12 uses two commands and zero recovery retries; an accepted unsafe write is a
failure, not a favorable speed result. Candidate measurements must rerun the
same fixtures and distinguish a successful task from a shorter refusal.
