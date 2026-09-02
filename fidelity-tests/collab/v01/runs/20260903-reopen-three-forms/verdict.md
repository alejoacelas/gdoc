---
fixture: collab/v01
task: reopen-three-forms
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1txCEE5AxJbnBEWQeQ7MJF0Ou0Yl1-dRoDJ7fZP3v7es
before_revision: 1
after_revision: null
gates:
  source_matches_baseline: pass
  preconditions_present: fail — the copy has 8 comments; the resolved comment AAACFLVgk4I (quoted 'three forms') was not copied
  before_capture: pass
  after_revision_later: not reached
outcome: INVALID
request_met: null
collateral: null
judges:
  structural: null
  visual: null
  human: null
issue: null
repro: null
---

File > Make a copy with "Copy comments and suggestions" copies open comments and pending
suggestions but not resolved comments: the fixture's resolved `three forms` comment is absent
from every collab copy. This task's precondition needs it, so no edit was attempted. Harness
consequence: tasks that need a resolved comment cannot be run on a copy at all; they need a
fixture whose comment is resolved *by the task agent* on the copy, or a per-run fixture. Noted in
CORRECTIONS.md.
