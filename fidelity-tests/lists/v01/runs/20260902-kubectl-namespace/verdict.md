---
fixture: lists/v01
task: kubectl-namespace
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1rmfBG6B1s2eoeFxMUR6Lu9r3jzMF_q6oK7OPXGe43UU
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
repro: repros.md#lists-v01-edit-across-font-boundary-flattens-run
---

`gdoc edit "deploy/api -n staging" "deploy/api -n staging-eu"` — a match that starts inside the
Courier New 10pt run and ends in the Arial run. "OK replaced 1 occurrence"; the namespace is
right and the other three `staging` untouched, but the whole item is now one default-style run:
Courier New and 10pt gone from `Kubectl rollout restart deploy/api`. Diff: one expected text
item, one unexpected style item. Visual judge: monospace gone. `gdoc cat` does not show fonts,
so the agent's own read could not reveal it. Cause: `cli`.
