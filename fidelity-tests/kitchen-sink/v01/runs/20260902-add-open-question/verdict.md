---
fixture: kitchen-sink/v01
task: add-open-question
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 11lWl1NRjf1Yh5ypjPGwL4Bzl71OaZrhzYAG9XjLEHaE
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
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..03), agreed=true
  human: null
issue: null
repro: null
---

`gdoc insert` cannot place text inside a list, so the agent used `gdoc edit
--old-file/--new-file` to replace the unique tail `Finance? © 2026` with itself plus a newline
and the new question. Docs made the new paragraph an item of the same list `kix.5hgdvulx3csg`
(glyph `%0)`, nesting 0). The diff shows only the new paragraph (text, bullet, paragraphStyle);
the Budget heading and the empty paragraph before the table are unchanged. The agent then
diffed every paragraph itself and reported the same. Visual judge: new `4)` item present,
content below shifts one line (allowed).
