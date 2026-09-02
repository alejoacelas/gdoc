---
fixture: lists/v01
task: kubectl-namespace
track: command
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 12sT33c2-eoUwm3SIbTpE7vklDU6tlYcjhnBG96mCoPk
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

Command track: one `gdoc edit "deploy/api -n staging" "deploy/api -n staging-eu"`. Same as the
agent run: text right, Courier New 10pt on `Kubectl rollout restart deploy/api` flattened to
Arial 11 (1 expected, 1 unexpected). Not visible in `gdoc cat`.
