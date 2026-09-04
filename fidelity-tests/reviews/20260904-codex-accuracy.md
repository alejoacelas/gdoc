# Fidelity harness accuracy review — 4 September 2026

The harness demonstrates real paragraph-formatting damage, but its completion and safety rates are not yet reliable measurements of the stated contract. It accepts changes without checking Expected, counts chained runs whose preconditions have disappeared, and paints some unchanged cells as successful edits. The remaining character-alignment artefacts affect both false alarms and missed damage.

I read the review brief first, the fidelity-test skill and references, corrections, reports, tasks, fixture descriptions, harness scripts, and repros. I independently inspected raw before/after structures for the eight runs below, exercised the diff functions with synthetic inputs, recounted all verdicts, and read two live painted copies through `gdoc structure --account alejandro.acelas-contractor@80000hours.org`. I also inspected the saved before/after JPEG pair for the lists link-retarget case. No Google document or harness file was changed.

Paths below are relative to `fidelity-tests/`, except paths explicitly beginning `gdoc/` or `.claude/`. Raw captures are compact JSON on line 1; paragraph text and API indices identify the evidence within that line. Findings are ranked by likely effect on rates or a reviewer's interpretation. Synthetic counterexamples establish implementation defects, not additional observed failures in existing runs.

## 1. “Expected” does not establish that the request was completed

**False success; high impact.** In [the classifier](../bin/gdt-diff), lines 356–388, `expected` is read but never used. A text item anywhere inside Target becomes `expected` regardless of its value. My direct call with Target `paragraph beginning alpha`, Expected `beta`, and a replacement `alpha → WRONG` returned `expected`.

[Batch verdict generation](../bin/gdt-batch-verdicts), lines 39–44, promotes any positive expected count with no unexpected items to DONE, including when the agent did **not** say yes. Lines 61–62 infer `request_met: partial` from a positive count for collateral runs; a count cannot distinguish full, partial, or incorrect completion. Signature-date, for example, fully changes the requested date while losing alignment; “partial” obscures that distinction.

**Smallest fix:** keep “inside target” separate from “Expected satisfied”; require an explicit assertion result for text, styles, comments and suggestion state before DONE. Until assertions exist, require a recorded judge check of each Expected clause. Never infer completion from the number of diff items or the agent's success claim.

## 2. Chained runs violate their preconditions and still count as DONE

**Observed false validity/success.** Two raw examples:

- [Marta quote, batch](../text/v01/runs/20260903-marta-quote-tuesday-afternoon/before/structure.json), paragraph starting at 777: the before already says `Northstar 2.2`; Georgia 13 pt, Courier New 9 pt, Times New Roman and JUSTIFIED alignment are already gone. The task explicitly requires those fonts and alignment. The after merely inserts ` afternoon`. Its [verdict](../text/v01/runs/20260903-marta-quote-tuesday-afternoon/verdict.md), lines 14–18, says preconditions pass, DONE, request met.
- [Key dates, batch](../text/v01/runs/20260903-key-dates-en-dash-slip/before/structure.json), paragraph starting at 144: the v2 range already uses an en dash, `"beta"` is already `"preview"`, and `launch window` is no longer bold. The declared precondition requires three distinct dash variants and bold; Expected still specifies the original v2 hyphen. The run is nevertheless DONE.

Under the written gate-first contract, both should be INVALID, not another charge of collateral to the later agent. The earlier task owns the damage, but that does not make the later test equivalent to its pristine counterpart. Merely excluding these two changes the displayed text fixture from completion/safety **6/22 to 4/20**, before any other corrections.

`gdt:77–85` copies the previous after into before and only prints precondition hints. `gdt-verdict:34–37` defaults `preconditions_present` to pass. This is the mechanism, not an isolated reporting typo.

**Smallest fix:** execute precondition assertions at every batch step; reset or split a chain when they fail. If cumulative editing is an intended separate experiment, version its task contract and label its rates separately. Preserve the original frozen-task result.

## 3. Pagination properties are silently exempted from the safety contract

**Observed false negatives under the written policy.** `gdt-diff:376–378` allows all changes to `avoidWidowAndOrphan`, `keepLinesTogether`, and `keepWithNext`, even outside Target and even with Allowed “none.” Lines 24–27 call them invisible; line 434 does not request visual review for them. These are layout controls, not save metadata.

Eight recorded DONE runs have `avoidWidowAndOrphan: false → absent`, with the NORMAL_TEXT named style supplying `true`: both dates of `tables/acme-cost-49000`, `tables/merged-owner-cell-interim`, `tables/data-engineer-owner-handover`, and `kitchen-sink/budget-cloud-credits`. The raw Acme cell at index 515 proves both the explicit false before and its removal after. The tasks only allow revision/modified-time changes. The policy remains an unresolved decision in CORRECTIONS.md.

Strictly applying “nothing else changes” would turn those eight DONEs into COLLATERAL: tables completion **18/22 → 12/22**, safety **20/22 → 14/22**; kitchen-sink agent completion **8/14 → 6/14**, safety **10/14 → 8/14**. This is a policy sensitivity calculation, not a claim that eight documents visibly repaginated.

**Smallest fix:** allow these only when explicitly declared; otherwise record the structural change and request visual review where layout matters. If they are deliberately exempted globally, change the contract and headline description before reporting rates.

## 4. Identical text sends paint to the wrong table cell

**Observed false-positive and false-negative paint.** [The live painted tables copy](https://docs.google.com/document/d/1Od_ShiE9_IINibY9OM1cGLNcf2Wc1U8SYod6uScA2ZU/edit) has four `Aprobado ✅` cells in table 1. My structure read found:

| Cell [row,col] | Meaning | API paragraph start | Paint |
|---|---|---:|---|
| [1,3] | Acme, unchanged | 2721 | Green across `Aprobado ✅\n` |
| [2,3] | Datawise, edited | 2782 | None |
| [4,3] | Contoso, edited | 2946 | None |
| [5,3] | New Globex row | 2992 | None |

The [painter](../bin/gdt-paint), lines 47–56 and 82, chooses the first exact-text paragraph anywhere in the document. It discards the diff's tab/table/cell path; the `used` parameter is unused. All three new status values select Acme.

**Smallest fix:** resolve the structural container first, then match text only within that container. Fail on ambiguity. Add this existing four-cell example as a range-mapping regression.

## 5. Another shared-letter artefact survives the June/September fix

**Observed false-positive diff item.** Both text `drop-old-plan` runs report `.style@"T"` as collateral. In the [batch diff](../text/v01/runs/20260903-drop-old-plan/diff.md), lines 5–10, the supposed edit is deletion of `he old plan was to ship in August; t`, while the first `T` is treated as unchanged and losing bold/strikethrough.

The raw result is the requested `The new plan…`: the old struck-through sentence was removed and the new sentence capitalized. Matching the old sentence's first letter to the new sentence's first letter is not evidence of protected formatting loss. Five other style-loss items are real, so COLLATERAL stands; **six** unexpected items overstates it.

The fix at `gdt-diff:250–261` only folds short equal fragments **between** edits. It misses boundary fragments like this `T`. A synthetic `Change Monday please → Change Friday please` also yields a `day` style item if Monday is bold and Friday plain; whether that's damage depends on the replacement's required style, not their shared suffix.

**Smallest fix:** align declared replacement spans as edits before comparing protected text. Treat ambiguous alignment as uncertain rather than asserting continuity from a shared character. Add the old-plan case alongside June/September.

## 6. The same alignment heuristic hides actual style and suggestion changes

**Demonstrated false negatives; one recorded disputed DONE.** Text replacement items at `gdt-diff:277–282` carry text but no before/after styles or suggestion metadata. Inserted paragraphs at lines 226–232 also omit run styles. My synthetic bold `48,500 → 49,000`, preserving bold on the matched `4` and `00` but dropping it on `9,0`, produces only one text item. The missing bold on the new amount is never checked. A separate `aXb → cXd` probe with protected bold `X` losing bold also produces only text: the short-equal folding erased the evidence.

In [collab next-review-september-2](../collab/v01/runs/20260903-next-review-september-2/after/structure.json), index 2353, `September` is committed text with **no** suggestedInsertionIds; `March` still has suggestedDeletionIds. Rejecting the remaining deletion gives `SeptemberMarch`. This is neither explicit Expected alternative: resolved `September`, or pending `{+September+}{-March-}`. The [runner's note](../collab/v01/runs/20260903-next-review-september-2/verdict.md) broadened “amended” to accept this after the run. I disagree with an unqualified DONE under the frozen Expected field; use FAIL-AGENT/request not fully met, or explicitly record a human contract amendment. Correcting only that DONE makes collab completion **4/10 instead of 5/10**; it need not reduce safety because Target allows modifying that suggestion.

**Smallest fix:** carry and validate style/suggestion state across replaced and inserted spans. Separate proposed, accepted and rejected text projections; compare them with explicit permitted outcomes. Removing a one-letter false alarm must not remove the underlying state check.

## 7. Mentioning a style licenses its loss, and unrelated paragraph changes

**Demonstrated false negatives.** `gdt-diff:365–370` accepts any changed style key mentioned in Request or Allowed, ignoring polarity, direction and scope. “Change alpha to beta, **keep bold**” classified bold true → absent as expected in my probe. “Point this link at X” likewise permits any URL, not just X; `underline` is also licensed by “link.”

Paragraph properties are even broader: lines 380–386 accept **any** paragraph property if **any** style word matches. The same “keep bold” probe permits `indentStart.magnitude: 0 → 72`. “Renumber” outside Target exempts all `.bullet` and `/lists` changes at lines 389–392, not only displayed numbering.

**Smallest fix:** replace vocabulary permissions with property-specific allowed transitions and ranges. Retain “keep” requirements as assertions. Never let a link request excuse indentation or an unrelated list identity/glyph change.

## 8. Locators do not enforce tab, subrange or comment identity

**Demonstrated broad false negatives and observed stale-target false positives.** `gdt-diff:328–349` ORs substring predicates. It ignores the named tab, truncates paragraph locators to 30 characters, ignores “the run …” qualifiers, and treats any mention of footnote/header/footer/comment as permission for every object of that kind. My `Tab 1` target also matched a `tab[Wrong tab]` style item.

Comments at lines 415–422 are compared as whole records. A comment task can alter/delete an unrelated thread and still get “expected”; the supposedly supported `.modifiedTime` allowance never matches these whole-comment paths. Expected's exact reply count/text/open state is not checked.

The stale `Northstar 2.1` locator makes the batch Marta insertion unexpected even though it touches the intended `Northstar 2.2` paragraph. The runner overrides the verdict, leaving the diff—and its red paint—unchanged.

**Smallest fix:** resolve unique typed locators against before, including tab/cell/comment identity and protected subranges; carry that identity into after. Reject zero/multiple matches before running. Diff comment properties separately and map copied thread identities through verified quote/context matches.

## 9. Normalisation and flattening omit meaningful structure

**Demonstrated false negatives.** `gdt-diff:15–16,34–39` removes every start/end index, including named-range endpoints. In a synthetic pair, moving a named range's end from 3 to 5 without changing its ID/text gives **zero items**. This loses the relationship the range represents, rather than merely suppressing downstream index shifts.

`flatten:130–166` selects fields rather than preserving everything else as promised. A tabId-only change also gives zero items. Child tabs are not traversed. Paragraph-level fields outside elements/paragraphStyle/bullet are discarded. Section breaks share one path: changing the first section's `columnSeparatorStyle` while the final section retains that key/value produced zero items in my probe. Separating paragraph and table sequences also loses their relative interleaving.

**Smallest fix:** explicitly represent container order, tab properties, paragraph metadata and unknown fields; recurse into child tabs. Translate ranges to semantic endpoints relative to aligned content instead of dropping them. Give each section break its own identity. Test omitted-field changes independently of rendering.

## 10. Canonicalisation compares overrides rather than effective formatting

**Demonstrated false alarm; incomplete equivalence policy.** `gdt-diff:42–75` removes values equal to each snapshot's named style. That usefully removes explicit default noise when the inherited style is unchanged. But I tested a run explicitly `bold:false` in both snapshots while the named style changes false → true: the diff invents a paragraph `.style@"alpha⏎"` change from `{}` to `{bold:false}`, although that paragraph stays non-bold. Other paragraphs inheriting the style are not given corresponding per-paragraph effective-style changes.

It also stops at the immediate named style and assumes the same inheritance for table text. Google's [TextStyle and ParagraphStyle reference](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents#TextStyle) documents inheritance through NORMAL_TEXT and possible table-style inheritance. I have not demonstrated a table-inheritance failure on a live fixture; the broad “rendering is identical” claim is therefore stronger than the implementation supports.

**Smallest fix:** retain raw overrides separately and compare resolved effective properties through the inheritance chain. Keep changes in override/inheritance semantics available as a distinct structural result. Only collapse equivalences the resolver can prove.

## 11. The two judges do not provide two independent, completed checks

**Evidence limitation and rate uncertainty.** The visual judge is a model reading JPEG viewports, not a browser assertion or pixel-diff oracle. The skill requires exact prompt/response and crop provenance; sampled verdicts instead summarize agreement. `gdt-batch-brief:6–13` shows structural counts to the visual judge and supplies the same before-all/after-all images for every task. Those images cannot establish which task caused a transient change, damage later repaired, or damage inherited by a later task.

I inspected lists `20260902-relink-rotate-keys` before/after `view-03.jpg`: the pale highlight around `Marco to` is consistent with the reported shrink, while the Cyrillic anchor portion remains. But that is one visual observation; the captured comment JSON has no anchor geometry to corroborate it. `shot.json` says “comments closed” although the image displays cards, so capture metadata is not a dependable description of review state either.

There are **five** verdicts still carrying `human: requested`: lists key-rotation-owner-to-priya and relink-rotate-keys on both dates, plus collab's single handbook-link-notion. All count as final COLLATERAL. This is conservative for safety but does not meet “judges must agree; disagreement goes to a human.” The five unresolved cases alone span five agent-safety numerator decisions out of 92; other blind spots mean this is not a total error bound.

**Smallest fix:** record complete judge input/output and image hashes; mark adjudication pending in the index until resolved. Capture per-step images for overlapping batches, and explicitly measure anchor coverage where it is a precondition. Merely adding a Drive `anchor` field is not proof that it tracks native Docs UI anchors; validate that experiment against a known moved anchor.

## 12. INDEX arithmetic is correct for the labels, but pools different experiments

**Misleading interpretation, not an arithmetic bug.** I independently recounted the stored verdicts:

| Population | Valid runs | Completion | Safety |
|---|---:|---:|---:|
| Agent, isolated | 46 | 23/46 | 30/46 |
| Agent, chained | 46 | 24/46 | 28/46 |
| Agent, pooled | 92 | 47/92 | 58/92 |
| Command, selected repros | 5 | 0/5 | 0/5 |

`gdt-index:23–29,40–51` reproduces the fixture totals in INDEX.md. It neither separates batch mode nor identifies pending adjudications. Chained trials have different before states; repeating a task weights it again. Command runs are selected failure repros, not a representative sample of commands. Thus 0/5 is a repro result, not a general CLI failure probability. The plan's claim that batch rates are “unchanged in meaning” is false for overlapping targets.

Saved material is also inconsistent: the batch Marta verdict says DONE with structural unexpected=1, and several verdict count summaries predate the alignment fix (e.g. batch co2 says expected=2, while current diff/batch.json says 1). These discrepancies do not all change outcome counts, but they prevent a reader from reproducing a verdict from its stated evidence.

**Smallest fix:** stratify isolated/chained/repro populations; show pending decisions and policy versions. Attach input/diff hashes to verdicts and invalidate/regenerate derived summaries after a judge change. Label the rates as observed task outcomes for this chosen suite.

## 13. Batch T numbers are alphabetical, not execution order

**Observed misleading attribution.** `gdt-batch-end:17–30` sorts directories by name; `gdt-batch-verdicts:56` calls that “Tn of …”. In text batch.json, T1 beta starts at Drive revision 12, T2 co2 at 2, T7 Marta at 7, T8 northstar at 4, and T10 signature at 1. Signature actually precedes those tasks. The JSON has no explicit chronological sequence field.

This makes “before = previous task's after” false if “previous” means the preceding displayed T number. It also determines painting order, so overlapping colours can be overwritten in alphabetical rather than execution order.

**Smallest fix:** persist predecessor run ID and sequence at run-start; validate before equals predecessor after; generate T numbers and paint from that order. `--continue` should verify the current live copy still matches the saved predecessor before attributing later differences to the next task.

## 14. Paint uses stale snippets and ambiguous character searches

**Observed wrong ranges and lost warnings.** In the [live text review copy](https://docs.google.com/document/d/15cUmAI2cwe_pTuJOoWsYpzcfnHdbmJ7EhAp6DVvYHSE/edit), ` afternoon` at UTF-16 range **3455–3465** is red even though its verdict was manually changed to DONE. That is the stale locator's unexpected item, not a formatting failure at those characters.

In the formula paragraph, the `Northstar 2.2` occurrences paint the **first** `2`, not the changed digit after the decimal. `gdt-paint:98–104` falls back to the first occurrence of the after fragment (`2`) inside nearby context. Earlier co2 surgery and the footnote placeholder representation prevent the exact-paragraph path from being dependable. Diff pseudo-elements use strings such as `⟨footnoteReference⟩`; the painter uses one U+FFFC character (`gdt-diff:84–85,284`; `gdt-paint:31`), so full-text equality fails around objects.

The lost-bold `launch window` from the beta task also cannot be found after a later rename to `release window`; the final paragraph shows green `release`, with no red indication there. Deletion paint marks unchanged surrounding text green, which the legend calls “change the task asked for, present.” Style fallback paints at most the 40-character snippet, not necessarily the full damaged run (`gdt-diff:271`; `gdt-paint:95–96`).

**Smallest fix:** map ranges through every subsequent edit using typed tokens and structural identity. Carry explicit before/after endpoints and deletion annotations; do not use first-occurrence searches for short fragments. Keep an overlap ledger and list every omitted/unresolved item in the review header. Apply human classification corrections to the diff consumed by paint.

## 15. Review copies promise anchored, exhaustive annotations they do not supply

**Misleading review UI.** `gdt-paint:143` calls `gdoc comment --quote`; [comment creation](../../gdoc/api/comments.py), lines 126–146, stores quotedFileContent and explicitly says it will not be visually anchored in Docs. Google's [Drive comment documentation](https://developers.google.com/workspace/drive/api/guides/manage-comments) also says Workspace editors treat API-defined anchors as unanchored. Yet the generated legend, lines 151–153, says every numbered comment is anchored where the task edited.

The painter skips comments and footnotes at lines 76–81, silently skips items lacking after_para_text (including many list/object changes and deleted paragraphs), and has no planned grey “request not met” annotation. It reports only some skips as “unlocated.” A first border wins permanently at lines 110–112, so a later red property loss cannot override an earlier amber/green border. Paint also replaces original background colours and adds borders/padding; it is an annotation artifact, not evidence that the original formatting or pagination survived.

**Smallest fix:** accurately label comments as document-level notes with quotes, show every unpaintable item and unmet request in the header, and retain explicit task-linked damage descriptions. Use severity-aware overlaps and distinguish the painted overlay from the unpainted evidence. Do not claim exhaustive or native anchored review until verified.

## Independent verdict checks from raw captures

These judgments came from raw paragraph text, run styles, paragraph properties and suggestion fields, then comparison with the saved verdict. All paired links below address line 1 of their structure.json files. The indices are UTF-16 start indices in that run's before capture, not positions in the painted copy.

| Run (under the named fixture's `v01/runs/`) | Raw evidence | My judgment |
|---|---|---|
| kitchen-sink `20260902-next-steps-effort-2` — [before](../kitchen-sink/v01/runs/20260902-next-steps-effort-2/before/structure.json), [after](../kitchen-sink/v01/runs/20260902-next-steps-effort-2/after/structure.json) | At 1459, effort 3→4; strikethrough on `v2 migration script` and yellow background on `Estimated effort` disappear. Superscript `[1]` survives. | **Agree COLLATERAL**, request text met; two real protected style losses. |
| text `20260903-signature-date` — [before](../text/v01/runs/20260903-signature-date/before/structure.json), [after](../text/v01/runs/20260903-signature-date/after/structure.json) | At 1679, 2→3 Sept; alignment END removed. Explicit lineSpacing 115 also removed, matching the named default. | **Agree COLLATERAL**, date fully met; alignment genuinely lost. |
| text `20260903-co2-formula` — [before](../text/v01/runs/20260903-co2-formula/before/structure.json), [after](../text/v01/runs/20260903-co2-formula/after/structure.json) | At 1087, styled `H2O`→`CO2`; subscript 2 and superscript x2 remain, footnote reference remains. lineSpacing 150 disappears; named default is 115. | **Agree COLLATERAL** for spacing; the formula itself is correct. |
| text `20260903-drop-old-plan` — [before](../text/v01/runs/20260903-drop-old-plan/before/structure.json), [after](../text/v01/runs/20260903-drop-old-plan/after/structure.json) | Old sentence removed; new sentence capitalized. Highlight, small caps, red text, underline and green highlight on surviving text disappear. | **Agree COLLATERAL**, but reject the additional one-letter T style item. |
| tables `20260903-acme-cost-49000` — [before](../tables/v01/runs/20260903-acme-cost-49000/before/structure.json), [after](../tables/v01/runs/20260903-acme-cost-49000/after/structure.json) | Cell [1,1], index 515: 48,500→49,000, bold retained. Explicit defaults drop; avoidWidowAndOrphan changes false→inherited true. | **Disagree DONE under written Allowed**; COLLATERAL structurally. DONE is defensible only under an explicitly approved pagination exemption. |
| text `20260903-marta-quote-tuesday-afternoon` — [before](../text/v01/runs/20260903-marta-quote-tuesday-afternoon/before/structure.json), [after](../text/v01/runs/20260903-marta-quote-tuesday-afternoon/after/structure.json) | At 777, only ` afternoon` inserted. Georgia 13 pt and other required fonts/justification missing before and after; prefix already 2.2. | **Disagree DONE for this test: INVALID** preconditions. Agree that this individual edit added no new formatting damage. |
| text `20260903-key-dates-en-dash-slip` — [before](../text/v01/runs/20260903-key-dates-en-dash-slip/before/structure.json), [after](../text/v01/runs/20260903-key-dates-en-dash-slip/after/structure.json) | At 144, first date becomes 15–19. Before already lacks bold, v2 already uses en dash, badge already says preview. | **Disagree DONE: INVALID** under declared preconditions, despite correct local date edit. |
| collab `20260903-next-review-september-2` — [before](../collab/v01/runs/20260903-next-review-september-2/before/structure.json), [after](../collab/v01/runs/20260903-next-review-september-2/after/structure.json) | At 2353, suggested June disappears; September is committed; March's pending deletion survives with the original suggestion ID. | **Disagree unqualified DONE**: the frozen Expected alternatives are not met. Preserve the runner's permissive interpretation as an explicit adjudication, not an automatic success. |

These disagreements should not be mechanically combined into one “corrected” headline rate: some require invalidating trials, some require settling an unresolved policy, and some require human interpretation of Expected. The isolated structural corruption findings remain well supported.

## Reproducing the review checks

Load functions without invoking script main: `d = runpy.run_path('fidelity-tests/bin/gdt-diff')`. For each synthetic document pair, call `normalise`, `canonicalise`, `flatten`, then `diff_leaves + compare_paragraphs`; pass each item to `classify` with `target_matcher(task)`. The concrete mutations in findings 1, 5–10 specify the inputs and observed results. These probes ran locally in memory; no scratch Google document was needed.

To inspect the paint examples again, run `gdoc structure --account alejandro.acelas-contractor@80000hours.org DOC_ID` for the two linked review documents and traverse `tabs[].documentTab.body.content`, including tables. Read backgroundColor on the table cells and text ranges listed above. The fetched paint uses quantized colours (green approximately 0.7216/0.9294/0.7216, red 1/0.702/0.702), which is normal colour storage, not a mapping error.

The report uses the repository snapshot reviewed in this session. Live review documents can subsequently change; quoted cell coordinates describe my 4 September read. No claim here certifies every run or every visual anchor.
