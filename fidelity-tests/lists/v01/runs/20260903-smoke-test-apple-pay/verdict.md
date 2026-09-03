---
fixture: lists/v01
task: smoke-test-apple-pay
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E
before_revision: 1
after_revision: 2
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: DONE
request_met: true
collateral: null
judges:
  structural: expected=1 allowed=0 unexpected=0
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all twelve tasks at once); agreed with the structural diff except on comment anchors (visual saw the anchor no longer covers 'Priya to'; structural is blind to anchors) and on the read-replica glyph change (attributed to the environments probe)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T9 of 12 on one copy; before = previous task's after). Agent: In the "Release plan (v2.14)" section, step 5 changed from "Smoke test the payment flow (card + SEPA)" to "Smoke test the payment flow (card + SEPA + Apple Pay)". Nothing else was touched; no copies or other Drive files were created. SUCCEEDED: yes — the single targeted replacement landed and a re-read shows the rest of the document unchanged. Agent's concerns: none. The only wrinkle was that the list numbering in the doc restarts after Priya's note, but "step 5" is unambiguous (there is exactly one item numbered 5 and one "Smoke test" line), and the exact-match replace could only hit that one occurrence.
