---
fixture: kitchen-sink/v01
task: fix-double-numbering
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 14LWsMKgyxKJJ_U1MswfFbROe_LgUwA2OGZnWi-_sRwo
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
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..03), agreed=true
  human: null
issue: null
repro: null
---

The agent confirmed with `structure` that the three items share list `kix.5hgdvulx3csg` and
that items 2 and 3 carry a literal `2) `/`3) `, then removed each prefix with a targeted `gdoc
edit` (two commands, both "OK replaced 1 occurrence"). The diff has exactly two expected text
items; the three trailing spaces after `replica?` and `© 2026` survive, the list ids and every
other list are unchanged. The bullet's explicit `underline: false` became absent, which the
canonicalisation treats as equal to the inherited default. Visual judge: numbering reads 1) 2)
3), nothing else moved.
