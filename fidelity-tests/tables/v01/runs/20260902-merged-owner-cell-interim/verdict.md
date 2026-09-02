---
fixture: tables/v01
task: merged-owner-cell-interim
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1BlKNohENUHdLKiyVS9-NXtrEAXH-_wJ-3wI3Lwp75YQ
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

`gdoc edit --case-sensitive "Owner TBD" "Owner: Ops (interim)"` inside the rowSpan-2 cell. Diff:
two expected text items and one allowed pagination hint; rowSpan intact, and the visual judge
sees the comment anchor highlight still on `shared between Ops and Finance` and the merge
intact. The longer text reflows one line (layout, not content). The agent also noticed the
shared scratch directory being clobbered by a sibling agent (CORRECTIONS.md).
