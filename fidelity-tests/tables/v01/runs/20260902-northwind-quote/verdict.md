---
fixture: tables/v01
task: northwind-quote
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1dZ4zsTLV16risYF8S_D7z04K5Lv9hpmhFWiL7cQ39P8
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

`gdoc edit --cell Northwind --table 0 "9,800"` — the agent used the row-label form of `--cell`
to avoid the `n/a` in the intro paragraph. The diff shows the cell paragraph replaced
(del/new pair, both expected); the merged owner cell and its comment are untouched. Visual judge
agrees.
