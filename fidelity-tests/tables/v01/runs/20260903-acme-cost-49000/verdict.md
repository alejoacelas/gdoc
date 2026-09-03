---
fixture: tables/v01
task: acme-cost-49000
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8
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
  structural: expected=2 allowed=1 unexpected=0
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all eleven tasks at once); agreed with the structural diff on every task (only paused-until-q1 lost its three fonts)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T1 of 11 on one copy; before = previous task's after). Agent: In the "Vendor comparison" table, the Acme Cloud cost cell went from **48,500** to **49,000**, keeping the bold. Nothing else in the document was modified. SUCCEEDED: yes — the requested cell shows 49,000 in bold and a full before/after structural diff shows no other change. Agent's concerns: - `gdoc edit --cell` strips the cell's existing text formatting when given plain text; I had to re-run it with markdown `**49,000**` to restore the bold. Worth knowing for future table edits, and possibly a CLI fix.
- The document says "Total committed vendor spend this quarter is 48,500 GBP" in the intro and "Cap for the quarter stays at 48,500" in the heads-up box. I left both alone because the request was specifically the vendor table, but the intro total is now arithmetically stale (it would be 49,000 given Datawise and Northwind have no committed figure), and the new cost exceeds the stated quarterly cap. The colleague should decide whether to update the intro and whether the cap line n
