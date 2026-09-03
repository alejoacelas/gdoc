---
fixture: collab/v01
task: reply-broadband-thread
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 15zKoeYqIQMuFqJ6k1h3SWYwfGqng41FeAr7Q3LdEQs8
before_revision: 1
after_revision: 1
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
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..05), agreed=true
  human: null
issue: null
repro: null
---

`gdoc comments --verbose` to find the thread, one `gdoc reply`, `comment-info` to confirm three
replies and `[open]`. Diff: one expected comment item; body identical; the `£15`→`£25`
suggestion in the same bullet still pending. Visual judge sees the third reply on the card and
every other card and highlight unchanged.
