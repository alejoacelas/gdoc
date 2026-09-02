---
fixture: tables/v01
task: fill-empty-vendor-row
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1ERvkyuWiArSdxaZEfI6rg4k_8ZS61qTOJ0iTkFcJaHg
before_revision: 1
after_revision: 5
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: DONE
request_met: true
collateral: null
judges:
  structural: expected=12 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

Four `gdoc edit --table 0 --cell 5,c` calls filled the empty row (Globex / 3,200 / Sign SOW
(Priya) / Aprobado ✅). Diff: twelve expected items (each cell's paragraph replaced), zero
unexpected; the header merge, the owner merge with its comment, and the pending suggestion
survive. The agent left `3,200` plain (only Acme's figure is bold) and did not continue the
cross-cell numbered list, both within Expected.
