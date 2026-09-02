---
fixture: lists/v01
task: legal-approval-date-georgia-run
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1nr4qVjh3QVsl5fV0j4MOjOt6GxFMKgs656wYhauhX1Y
before_revision: 1
after_revision: 2
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: COLLATERAL
request_met: true
collateral: 
  visible: true
  invisible: false
  agent_read_would_reveal: false
judges:
  structural: expected=2 allowed=0 unexpected=2
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: repros.md#lists-v01-edit-across-font-boundary-flattens-run
---

`gdoc edit "Approved by Legal on 14 Aug" "Approved by Legal on 21 Aug"`; the match ends one
character into the Georgia 13pt run (`14 Aug, see the thread`). The date is right, but the whole
Georgia run in this item was flattened to Arial 11; the Georgia `Owner` in the next item
survived. Diff: two expected text items, two unexpected style items. Visual judge agrees. Not
visible in `gdoc cat`. Cause: `cli`.
