---
fixture: tables/v01
task: acme-cost-49000
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1DoaABtJiJrPMo0cZIfcWslPz0xVFSHLsUD1SYX4TT0U
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
  structural: expected=2 allowed=1 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

The agent chose `gdoc edit --table 0 --cell 1,1 "**49,000**"` over a text replace because
`48,500` occurs three times, and re-applied bold via markdown. Diff: two expected text items in
the cell and one allowed pagination hint; the intro and callout `48,500` untouched. Visual judge
agrees. `--cell` is the right tool here and the agent found it.
