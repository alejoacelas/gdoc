---
fixture: lists/v01
task: legal-approval-date-georgia-run
track: command
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1l6V-tx0gqet4jex-pZ6S_kNLF0aoiSKj-bVfYRsCmWg
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

Command track on a UI copy (comment and suggestion present): one `gdoc edit "Approved by Legal
on 14 Aug" "Approved by Legal on 21 Aug"`. Same as the agent run: Georgia 13pt on `21 Aug, see
the thread` flattened (2 expected, 2 unexpected); the Georgia `Owner` in the next item, the
comment anchors and the pending suggestion survive.
