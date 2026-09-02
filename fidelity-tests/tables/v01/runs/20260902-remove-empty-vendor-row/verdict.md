---
fixture: tables/v01
task: remove-empty-vendor-row
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1HCthEBYg9HxhN6DgnuXul1kUoFcjXvQHhoSITG8AMoQ
before_revision: 1
after_revision: 1
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: n/a (no edit made; structure identical)
outcome: GAP-CLI
request_met: false
collateral: null
judges:
  structural: expected=0 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

The agent surveyed every gdoc write path and found none that deletes a table row; it refused
`write`/`push` as a whole-document rewrite and changed nothing (before and after identical). The
Docs API has `deleteTableRow`, so this is a CLI gap. Correct refusal.
