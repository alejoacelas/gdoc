---
fixture: kitchen-sink/v01
task: reply-and-resolve-v3-comment
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1MvuelNtyr-OXHxrtVuO8McZ_tH9PZ9ZJkmWZgt501fQ
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
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

The agent used `gdoc resolve -m "…"` to post the reply and resolve in one call, then verified
with `comment-info`. Diff: one expected item (the comment gains the reply and `resolved: true`);
the body structure is identical, the pending suggestion still pending. Visual judge: the comment
card and its anchor highlight are gone from the margin (resolved), nothing else differs. A UI
copy was needed here; `gdoc cp` would have dropped the comment.
