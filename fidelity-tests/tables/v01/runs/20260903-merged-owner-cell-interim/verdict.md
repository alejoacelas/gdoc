---
fixture: tables/v01
task: merged-owner-cell-interim
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8
before_revision: 6
after_revision: 7
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

Batch run (20260903-batch, T6 of 11 on one copy; before = previous task's after). Agent: In the vendor comparison table, the merged owner cell spanning the Northwind and Contoso rows: replaced the two words "Owner TBD" with "Owner: Ops (interim)". The em dash and the remainder of the sentence ("— shared between Ops and Finance until the Contoso decision lands") are unchanged. Nothing else in the document was touched. SUCCEEDED: yes — the one intended occurrence was replaced and the follow-up read shows the full sentence intact with no other differences. Agent's concerns: The pre-flight banner on the first read reported an edit by Alejandro Acelas 41 seconds earlier (v14 → v15), before my change; I take that to be fixture setup, not a conflict, since the cell text I read matched the request. Also, `gdoc cat` is a markdown export, so I could confirm text but not that the cell's formatting (merge, styling) survived — Docs' replace-text operates on text runs and should preserve both.
