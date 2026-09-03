---
fixture: tables/v01
task: northwind-quote
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8
before_revision: 3
after_revision: 4
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: DONE
request_met: true
collateral: null
judges:
  structural: expected=3 allowed=0 unexpected=0
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all eleven tasks at once); agreed with the structural diff on every task (only paused-until-q1 lost its three fonts)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T7 of 11 on one copy; before = previous task's after). Agent: In the vendor comparison table (first table, "Northwind" row, "Cost (GBP) & owner" column) I replaced `n/a` with `9,800`. Nothing else was touched — the intro sentence "one figure below is n/a until Northwind sends the revised quote" is unchanged, as are the other rows, the heads-up box, the hiring table and the sign-off block. SUCCEEDED: yes — the Northwind cost cell now reads 9,800 and the second read shows no other differences. Agent's concerns: The intro paragraph still says one figure is "n/a until Northwind sends the revised quote", and the total "48,500 GBP across three suppliers" no longer matches the table (49,000 + 12,950/12,750 + 9,800); the colleague asked only for the table cell, so I left both alone but they may want to update them. The edit's pre-flight reported a revision bump (v11 → v12) by my own account between my read and my edit that I didn't make — most likely Google's revision consolidation or the state tracker, and the verification read shows nothing else changed, but worth knowing. `cat` can't show cell formatting, so I could not confirm 9,800 kept the same font/alignment as the old n/a.
