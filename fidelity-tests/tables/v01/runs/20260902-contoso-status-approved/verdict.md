---
fixture: tables/v01
task: contoso-status-approved
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1Hm3RLoZl3vZQig5wtbMJOZFh_xTM7Fwh0pOwH00e6Sw
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

One `gdoc edit "Отклонено ❌" "Aprobado ✅"` (unique string). Cell [4,3] replaced; the vertical
merge, the comment anchored on `shared between Ops and Finance` and the pending suggestion in
[2,1] all survive (visual judge confirms the anchor highlight and the green suggestion). A UI
copy was needed for the comment precondition.
