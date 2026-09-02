---
fixture: text/v01
task: key-dates-en-dash-slip
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1MVRtdjBISP14w02P-W98cLNg3am45R6m-w3M4J7_mPY
before_revision: 1
after_revision: 3
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: DONE
request_met: true
collateral: null
judges:
  structural: expected=2 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

`gdoc edit --case-sensitive 'opens 14–18 Sept 2026' 'opens 15–19 Sept 2026'` (exact en dash) hit
only the first sentence; the v2-draft hyphen, the CMS em dash and the highlighted `14–18 Sept`
in the old-plan paragraph are untouched. The edit stripped bold on `launch window`; the agent
caught it by diffing the export, restored it, and verified three runs in `structure`. Final
diff: two expected text items, zero unexpected. Visual judge agrees.
