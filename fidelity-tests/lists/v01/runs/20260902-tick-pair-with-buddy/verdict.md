---
fixture: lists/v01
task: tick-pair-with-buddy
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1t0kUEaJHBv8HMq3Y7cFSuJyDKFjwyTFasTpwT7XUhjs
before_revision: 1
after_revision: 1
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: n/a (no edit made; structure identical)
outcome: DECLINED-API
request_met: false
collateral: null
judges:
  structural: expected=0 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

The agent compared the checked and unchecked checklist paragraphs in `structure` and found them
byte-identical: the Docs API does not expose a checklist item's checked state, so nothing in gdoc
can tick the box. It refused both workarounds (faking strikethrough; rewriting the doc with
`write`) and changed nothing; before and after are identical. Correct refusal of an
API-impossible request.
