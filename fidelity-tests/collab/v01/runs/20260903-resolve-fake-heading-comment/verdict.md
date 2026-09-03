---
fixture: collab/v01
task: resolve-fake-heading-comment
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1_ZF9_ODEESn_A316ORMLVlr8QUmkiNgPUkg1ZmQjX-U
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

`gdoc resolve --message "Leaving as is for v3."` in one call, verified with `comment-info`
(`[resolved]`, one reply, exact text) and a re-list showing the other seven still open. Diff:
one expected comment item; body identical, `What changes` still bold 14pt Normal. Visual judge:
the card and its anchor highlight are gone from the margin as a resolved comment should be;
the reply text is confirmed by `comments.json`, not by the screenshot.
