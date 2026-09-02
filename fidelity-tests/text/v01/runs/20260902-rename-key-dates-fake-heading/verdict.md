---
fixture: text/v01
task: rename-key-dates-fake-heading
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1-kOq8bcbBro3eRPioKNjD9jeFR1Q_GwRmve0gllmYvU
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
  agent_read_would_reveal: true
judges:
  structural: expected=1 allowed=0 unexpected=2
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: repros.md#text-v01-edit-drops-font-size
---

`gdoc edit --case-sensitive "Key dates" "Key dates and labels"` dropped both bold and 14pt from
the fake heading; the agent saw the empty textStyle in `structure`, restored bold with `**…**`
and correctly declined to promote it to a real heading. 14pt cannot be set with gdoc, so the
fake heading now renders at body size (diff: 1 expected, 2 unexpected fontSize items; visual
judge: smaller than `Summary`). The agent reported this precisely. Cause: `cli`.
