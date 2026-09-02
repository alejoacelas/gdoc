---
fixture: kitchen-sink/v01
task: rollout-to-launch-window
track: command
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 11u7dM6gcu0epIsitLmmL9y_V4iB-cbozOIXHVPpH_F8
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
  agent_read_would_reveal: true
judges:
  structural: expected=9 allowed=0 unexpected=9
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..03), agreed=true
  human: null
issue: null
repro: repros.md#kitchen-sink-v01-edit-all-strips-run-styles
---

Command track: one `gdoc edit --all --case-sensitive "rollout window" "launch window"`, no
repair pass. Text is right in all three places; bold, italic+red and the link are all gone
(diff: 9 expected text fragments, 9 unexpected style items; visual judge sees three plain black
runs). `gdoc cat` would show the missing `**`, `*` and `[…](…)`, so this one is self-detectable
by the agent, which is why the agent run recovered everything except the red colour.
