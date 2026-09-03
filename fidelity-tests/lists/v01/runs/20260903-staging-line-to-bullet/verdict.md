---
fixture: lists/v01
task: staging-line-to-bullet
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E
before_revision: 10
after_revision: 13
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: FAIL-AGENT
request_met: false
collateral: null
judges:
  structural: expected=87 allowed=0 unexpected=0
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all twelve tasks at once); agreed with the structural diff except on comment anchors (visual saw the anchor no longer covers 'Priya to'; structural is blind to anchors) and on the read-replica glyph change (attributed to the environments probe)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T10 of 12 on one copy; before = previous task's after). Agent: Under Environments, the "Staging shares the prod cluster, namespace staging (yes, really)" paragraph is now a genuine Google Docs bullet and the typed "-" plus its tab are gone. The bullet is a top-level ● bullet (indent 36pt, its own list), i.e. it lines up with "Production", not with "Also a read replica" (which sits at 108pt with a "-" glyph in a separate list). SUCCEEDED: partially — the dash is dropped and the line is a real bullet, but I could not put it at the same indent level as "Also a read replica" because gdoc has no command to set list nesting or indent on an existing paragraph, and markdown indentation in `edit` replacement text is not honored on an already-bulleted paragraph (it produced literal tabs, which I reverted). Agent's concerns: (1) The level mismatch is visible: the new bullet renders one/two levels shallower than the read-replica line; someone needs to press Tab twice in the Docs UI (or use the Docs API `updateParagraphStyle`/list nesting) to finish the job. (2) The new bullet's glyph is ● rather than the "-" used by the neighbouring "Also a read replica" list, so even at the right indent it would look slightly different. (3) The paragraph's bullet textStyle went from `{'underline': False}` to `{}` — no visible effect. (4) Edits 8–10 were an unsuccessful detour that briefly left two tab characters in the line; the final state has no leftover tabs, and no other paragraph was touched.

Runner's note: the agent made the line a real bullet but in a new top-level list (● at 36pt) instead of joining the read-replica list at 108pt, then reverted the literal tabs its markdown attempt produced. Request not met, nothing outside the target damaged (the 81 list-object items are the new list the target paragraph now uses): FAIL-AGENT rather than COLLATERAL. In the single run the same agent declined instead.
