---
fixture: lists/v01
task: insert-migration-step
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1PjSTDvCHTuhruqJNuzkLitQRMEd63h9qE_AE1sIbu8o
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
  structural: expected=3 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

`gdoc insert` cannot place text inside a list, so the agent used `gdoc edit --old-file/--new-file`
to append `\nRun the DB migrations on staging (Priya)` to step 4. Docs made the new paragraph an
item of the same list (`kix.ehmbnlna9fov`, nesting 0) and renumbered 5–6 to 6–7 as allowed. Diff:
three expected items, all on the new paragraph; list C still restarts at 1. Visual judge agrees.
The agent noted that "steps 4 to 6" in Priya's note is now stale and left it, correctly.
