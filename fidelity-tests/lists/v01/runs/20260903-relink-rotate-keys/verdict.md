---
fixture: lists/v01
task: relink-rotate-keys
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E
before_revision: 4
after_revision: 5
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: COLLATERAL
request_met: partial
collateral: 
  visible: false
  invisible: false
  agent_read_would_reveal: false
judges:
  structural: expected=1 allowed=0 unexpected=0
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all twelve tasks at once); agreed with the structural diff except on comment anchors (visual saw the anchor no longer covers 'Priya to'; structural is blind to anchors) and on the read-replica glyph change (attributed to the environments probe)
  human: requested — judges disagree (structural blind to anchors)
issue: null
repro: null
---

Batch run (20260903-batch, T7 of 12 on one copy; before = previous task's after). Agent: Only the hyperlink URL on "rotate the API keys" in the action item "Marco to rotate the API keys before Friday", from https://example.com/rotate-keys to https://example.com/runbooks/rotate-keys. Visible text, link styling, list membership and every other occurrence of "rotate the API keys" are untouched. I chose the match "rotate the API keys before Friday" (unique) rather than the whole line so the comment anchor on "Marco to" was never deleted/reinserted. SUCCEEDED: yes — the link now points at the new runbook URL and a full before/after structure diff shows no other content change. Agent's concerns: The before/after structure diff shows one incidental change besides the URL: the bullet glyph's `textStyle` on that list item went from `{"underline": false}` to `{}` (the explicit "no underline" on the bullet marker was dropped, so it now inherits the default). This should render identically since the paragraph text itself is not underlined, but it is a real, if cosmetic, side effect of how `gdoc edit` rewrites the run. Also, someone else edited the doc (v14→v15) less than a minute before I started; my edit is v16 and applied cleanly on top.

Runner's note: structural diff shows only the link url change. In the batch's final state the comment anchor no longer covers the item's first words; it cannot be told from screenshots whether this run or key-rotation-owner-to-priya (T12) caused it, and in the single run this task alone did. Recorded COLLATERAL (invisible to structural), human review requested.
