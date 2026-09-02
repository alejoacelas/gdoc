---
fixture: text/v01
task: drop-old-plan
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1zTiD6HAm0xI2MicX-cikP44qWGV2tP_bOSuxnFY_X3I
before_revision: 1
after_revision: 3
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
repro: repros.md#kitchen-sink-v01-edit-strips-paragraph-styles
---

Two edits: delete `The old plan was to ship in August; ` (empty replacement so nothing inherits
bold+strike), then capitalise `the new plan`. Text is exactly Expected. Every inline style in
the paragraph is gone: yellow highlight on `14–18 Sept`, small caps on `internal only`, red on
`do not forward`, underline on `read this first ` and green highlight on `agreed with Legal`
(diff: 1 expected, 6 unexpected; the visual judge lists each). The agent saw a single unstyled
run in `structure`, said so, and noted gdoc cannot apply any of those styles back. Cause: `cli`.
