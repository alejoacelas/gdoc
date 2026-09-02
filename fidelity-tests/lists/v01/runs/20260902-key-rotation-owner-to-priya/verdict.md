---
fixture: lists/v01
task: key-rotation-owner-to-priya
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1lQj4IUjhYEEoIjxjZSru1I-cPqaK5Ct4UyAH3fg--_c
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
  invisible: true
  agent_read_would_reveal: false
judges:
  structural: expected=2 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=false — visual saw the comment anchor shrink; structural cannot see anchors (gdoc comments has no anchor field)
  human: requested — judges disagree; Expected's anchor clause may be too strict
issue: null
repro: null
---

The agent replaced only `Marco to ` with `Priya to `, leaving the linked run alone; the link, the
other four `Marco` and five `rotate the API keys` are untouched (diff: two expected text items,
0 unexpected). The visual judge found the open comment's anchor no longer covers the item's
first words: before `спросить Дмитрия` + `Marco to` were highlighted, after only `спросить
Дмитрия`. The task's Expected says the anchor should span through `Priya to`; whether replacing
anchored text should keep the anchor is arguably a Docs behaviour rather than a gdoc defect
(delete+insert under an anchor shrinks it in the UI too), so this needs a human call. Recorded
COLLATERAL because a protected property (the anchor) changed and the structural judge cannot
see anchors at all.
