---
fixture: tables/v01
task: remove-empty-vendor-row
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8
before_revision: 7
after_revision: 7
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
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all eleven tasks at once); agreed with the structural diff on every task (only paused-until-q1 lost its three fonts)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T10 of 11 on one copy; before = previous task's after). Agent: Nothing. The document is untouched. SUCCEEDED: no — gdoc 0.21.0 has no way to delete a table row in a Google Doc short of rewriting the whole document from markdown, which I judged unacceptable. No change made; outcome follows the earlier single run (GAP-CLI) with the same reasoning. Agent's concerns: The only available route (`gdoc write`/`push` with the row removed from the markdown) would flatten the doc: it would resolve or drop the pending suggestion in the Datawise cost cell (12,950 → 12,750), lose the bold header cell in the empty row and the rest of the table, the shaded heads-up callout table, the deliberately borderless sign-off table, the tab-separated text in the Head of People row, and likely the link/emoji fidelity. The empty row itself is confirmed truly empty (no hidden text, suggestions, or objects), so deleting it manually in the Docs UI (right-click → Delete row) is safe and takes a few seconds; alternatively the CLI would need a native `deleteTableRow` batchUpdate, whi
