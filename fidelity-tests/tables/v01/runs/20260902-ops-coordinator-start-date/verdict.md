---
fixture: tables/v01
task: ops-coordinator-start-date
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1imMt92cJ_DJSwMIu04GA68UQkyEMYmn3pWQz2JldAQw
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
  structural: expected=1 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

The first attempt (`"2 Sept 2026 (tbc)" → "2 Sept 2026"`) found no match because the date is a
smart chip, not text; the agent read `structure`, understood the chip, and deleted only the
` (tbc)` run. Diff: one expected text item; the `dateElement` is untouched. Visual judge: chip
renders identically, `(tbc)` gone. Good example of a read-before-edit success next to an object
the API cannot create.
