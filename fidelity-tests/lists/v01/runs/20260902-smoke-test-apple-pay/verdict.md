---
fixture: lists/v01
task: smoke-test-apple-pay
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1cDsJH3HR9ggjk7AnoqAAbfMTqzy7oM8sD5IltfcjlaQ
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
  structural: expected=1 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

One `gdoc edit` on the unique phrase; "OK replaced 1 occurrence". The item text changed in place,
list `kix.ehmbnlna9fov` and its neighbours' tab and trailing spaces intact. Diff: one expected
item. Visual judge: only step 5 changed.
