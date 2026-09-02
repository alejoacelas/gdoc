---
fixture: tables/v01
task: datawise-status-approved
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1C3vgCkLEhAFpqbDJJpMTljULic-jBDzgxfEZRE7rhX8
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

`gdoc edit --table 0 --cell 2,3 "Aprobado ✅"` replaced the whole cell (`Pendiente: ` + italic
`pending legal review`). Diff: del/new pair in the cell, expected; the other two `pending legal
review` (intro plain, callout bold) and the pending suggestion in the neighbouring cell are
untouched. Visual judge agrees.
