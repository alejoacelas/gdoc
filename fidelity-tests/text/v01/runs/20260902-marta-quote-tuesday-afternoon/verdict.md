---
fixture: text/v01
task: marta-quote-tuesday-afternoon
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1HqwzQHIEiWa7SGa_2RVLf4phIhmymhmcRyzCw3Zo7VI
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
  structural: expected=1 allowed=0 unexpected=6
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: repros.md#text-v01-edit-resets-paragraph-style
---

One exact edit on the quote's tail (`everyone’s Tuesday”` → `… Tuesday afternoon”`), matched
with the right curly characters. The insertion is right, but the whole justified four-font
paragraph was flattened to Arial 11 left-aligned (diff: 1 expected, 6 unexpected: fonts on four
runs, alignment JUSTIFIED → default; visual judge lists the same). The agent's plain-text diff
showed one change and it reported success, flagging only that it could not see fonts. Cause:
`cli`.
