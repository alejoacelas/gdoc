---
fixture: text/v01
task: beta-badge-straight-quotes
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1ZKZe1veY5CoZeso7giZevp5Ylqs8SGoZnzzoe1IvJUU
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

`gdoc edit --case-sensitive '"beta"' '"preview"'` matched only the straight-quoted twin, then the
agent saw in `cat` that the paragraph's bold `launch window` had gone and re-applied it with a
markdown edit; its `structure` check showed three runs again. Final diff: two expected text
items, zero unexpected; curly `“beta” label` and all dash twins intact. DONE only because the
agent diffed before/after itself and repaired; the first command alone would have been
COLLATERAL (see hyphen-date-fix and key-dates-en-dash-slip, same paragraph, same recovery).
