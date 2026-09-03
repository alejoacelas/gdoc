---
fixture: tables/v01
task: ops-coordinator-start-date
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8
before_revision: 11
after_revision: 12
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
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all eleven tasks at once); agreed with the structural diff on every task (only paused-until-q1 lost its three fonts)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T8 of 11 on one copy; before = previous task's after). Agent: In the Hiring pipeline table, Ops coordinator (Madrid) row, "Owner & links" cell, I deleted the trailing text " (tbc)" after the start-date smart chip. The cell now reads "Tomás; start 2 Sept 2026" with the date chip preserved. Nothing else was modified. SUCCEEDED: yes — the "(tbc)" is gone, the date chip is intact, and the unrelated uppercase "TBC after the Q3 board" was left alone. Agent's concerns: (1) The doc is being edited concurrently by an automated run under the same account (v19→v20 landed between my read and first edit, with vendor-table changes unrelated to this task); my change is scoped to a single text run so it shouldn't collide, but the doc's other content is shifting under whoever reviews it. (2) The start date is a Google Docs date chip, so `gdoc cat` output ("2 Sept 2026") is not literally matchable text — anyone editing that cell by text search will hit "no match"; I replaced only the adjacent " (tbc)" run rather than rewriting the cell, to avoid destroying the chip. (3) My first failed `edit` attempt made no change (exit 3, nothing written).
