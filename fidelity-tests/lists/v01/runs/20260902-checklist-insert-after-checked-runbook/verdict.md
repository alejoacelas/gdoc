---
fixture: lists/v01
task: checklist-insert-after-checked-runbook
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1cdQX3-1OK_OkBFg0uh6tgMZuHRxden7pUTsdUHvrPvM
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
  structural: expected=3 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

The agent deliberately anchored the insertion at the start of the unchecked `Pair with your
buddy` item rather than the end of the checked runbook item, so the new paragraph inherited the
unchecked, non-struck state. Diff: three expected items on the new paragraph (text, bullet in
`kix.i11mp0ghmsa2`, paragraphStyle); the empty checklist item survives. Visual judge: new
unchecked box in the right place, checked items still struck.
