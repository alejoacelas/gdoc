---
fixture: tables/v01
task: data-engineer-owner-handover
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1aTmkASrLa9j3nAHhvxhElPRU-zx7UuAUizXNcTk6BS8
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
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

Vague request, one precise edit: `gdoc edit --case-sensitive 'Priya.' 'Tomás.'` matched only the
owner cell (the `Sign MSA (Priya)` cell has no full stop). Diff: one expected text item and one
allowed pagination hint; the `JD on Notion` link and the dropdown chip in the same row are
intact. Visual judge agrees.
