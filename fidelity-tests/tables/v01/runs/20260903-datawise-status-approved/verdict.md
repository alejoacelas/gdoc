---
fixture: tables/v01
task: datawise-status-approved
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1qTULReZ9fMsbm0dzsc-epg7kxTae2hQFvexKNabmPN8
before_revision: 5
after_revision: 6
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

Batch run (20260903-batch, T4 of 11 on one copy; before = previous task's after). Agent: In the first table ("Vendor comparison"), the "Estado · ステータス" cell of the Datawise Ltd row went from "Pendiente: *pending legal review*" to "Aprobado ✅" (plain text, matching the Acme row). Nothing else in the document was touched. SUCCEEDED: yes — the Datawise status cell now reads exactly like Acme's, and a before/after structural diff shows no collateral changes. Agent's concerns: The doc's intro paragraph still says "two contracts are still pending legal review" and the Datawise cost cell contains what looks like a paste glitch ("12,95012,750"); I left both alone since they weren't part of the request, but the colleague may want to update the intro sentence.
