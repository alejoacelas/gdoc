---
fixture: tables/v01
task: reply-owner-comment
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1uWlRDfjojfBdmYycc1axvyBiRi_Vm5vYIWMNclGyKL4
before_revision: 1
after_revision: 1
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

`gdoc reply` on the only comment; `comment-info` confirms one reply and `[open]`. Diff: one
expected comment item, body identical, suggestion still pending. Visual judge sees the reply in
the margin card and no body change.
