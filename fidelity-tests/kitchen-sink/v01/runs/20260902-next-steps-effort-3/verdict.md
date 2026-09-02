---
fixture: kitchen-sink/v01
task: next-steps-effort
track: command
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1G-ZtJ-yw3zA_HfgCHmdTSaoFrUwXDlBG-_ls8YvikOY
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
  structural: expected=1 allowed=0 unexpected=2
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..03), agreed=true
  human: null
issue: null
repro: repros.md#kitchen-sink-v01-edit-strips-paragraph-styles
---

Command track for the first collateral case, on a UI copy with the comment and suggestion
present: one `gdoc edit "Estimated effort: 3 dev-days" "Estimated effort: 4 dev-days"`. Same
result as the agent run: 1 expected, 2 unexpected (strikethrough on `v2 migration script` and
highlight on `Estimated effort` gone); the comment anchor on `script v3` and the pending
suggestion in the next paragraph survive. The CLI alone reproduces the damage; no agent choice
involved.
