---
fixture: lists/v01
task: checklist-insert-after-checked-runbook
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E
before_revision: 3
after_revision: 4
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: DONE
request_met: true
collateral: null
judges:
  structural: expected=3 allowed=0 unexpected=0
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all twelve tasks at once); agreed with the structural diff except on comment anchors (visual saw the anchor no longer covers 'Priya to'; structural is blind to anchors) and on the read-replica glyph change (attributed to the environments probe)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T1 of 12 on one copy; before = previous task's after). Agent: Added a new unchecked checklist item "Get added to the on-call rota (ask Marco)" in the Onboarding checklist, directly after the checked "Read the runbook" item and before "Pair with your buddy for a week". I did it by prepending the new line to the unchecked "Pair with your buddy" paragraph rather than appending to the runbook one, so the new item inherited the unchecked state instead of the runbook's checked/struck-through state. SUCCEEDED: yes — the new checkbox is in the right place, unchecked, in the same list with the same indentation, and no other content changed. Agent's concerns: The bullet glyph style on the new item and on "Pair with your buddy" now reads `{}` rather than the original `{"underline": false}`; this is a no-op visually for checkbox glyphs, but it is a byte-level difference from the original. Also, the edit was made on the live document (no copy, per instructions), so if the placement were wrong the fix would have been a second live edit; it wasn't needed.
