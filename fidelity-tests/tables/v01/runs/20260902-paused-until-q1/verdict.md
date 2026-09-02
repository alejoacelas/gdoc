---
fixture: tables/v01
task: paused-until-q1
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1dhBqDTCQl5ww7f6G3EVZNqS9CbSTRUpiXkn10XGQzeo
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
  structural: expected=1 allowed=1 unexpected=2
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: repros.md#lists-v01-edit-across-font-boundary-flattens-run
---

`gdoc edit "Paused until Q4" "Paused until Q1"` — the match spans the Courier New 9pt `Paused`
and the Arial ` until Q4`. The text is right but the whole cell paragraph was flattened to Arial
11: Courier New 9 on `Paused` and Georgia 14 on `see budget` (outside the match) both gone.
Diff: one expected, two unexpected style items, one allowed pagination hint. Not visible in
`gdoc cat`; the agent reported "nothing to lose" because the export showed plain text. Same CLI
behaviour as the lists kubectl/legal runs. Cause: `cli`.
