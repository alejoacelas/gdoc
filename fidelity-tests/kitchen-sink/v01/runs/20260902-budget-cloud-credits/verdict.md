---
fixture: kitchen-sink/v01
task: budget-cloud-credits
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1GnVEZoRVxJwtB6L-eEtAOj-EhQXps-WYX1io6mfV59E
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
  structural: expected=1 allowed=1 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..03), agreed=true
  human: null
issue: null
repro: null
---

The agent read the doc with `gdoc cat`, ran one `gdoc edit '$12,400' '$12,900'` ("OK replaced 1
occurrence") and re-read. The cell now reads `$12,900`; the Finance note's `12,400 spent` is
untouched. The structural diff has one expected item (the cell text) and one allowed invisible
item: the cell paragraph's explicit `avoidWidowAndOrphan: false` was dropped by the edit and now
inherits `true` from Normal text (a pagination hint, no visible effect; policy in
CORRECTIONS.md). The visual judge saw only the cell change. The agent's report was accurate.
