---
fixture: text/v01
task: signature-date
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1CcjnJ_WpnmfW1tPoSHqNvSA0f7_pHeDttwy33Bi9aqU
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
  structural: expected=1 allowed=0 unexpected=1
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: repros.md#text-v01-edit-resets-paragraph-style
---

One exact `gdoc edit "Marta, 2 Sept 2026" "Marta, 3 Sept 2026"`, anchored to miss the other
`Sept 2026`. The date is right; the paragraph's `alignment: END` was dropped and the signature
now sits at the left margin (diff: 1 expected, 1 unexpected; visual judge confirms). A plain
text replace should never touch paragraph alignment. Cause: `cli`.
