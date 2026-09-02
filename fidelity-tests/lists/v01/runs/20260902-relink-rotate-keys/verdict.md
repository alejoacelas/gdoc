---
fixture: lists/v01
task: relink-rotate-keys
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1ySUMvKECwMRaFvHHAG2SMQrsylcFrc7wOzlAKxSLyJ8
before_revision: 1
after_revision: 2
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: COLLATERAL
request_met: true
collateral: 
  visible: true
  invisible: true
  agent_read_would_reveal: false
judges:
  structural: expected=1 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=false — visual saw the comment anchor shrink; structural cannot see anchors (gdoc comments has no anchor field)
  human: requested — judges disagree (structural blind to anchors)
issue: null
repro: null
---

The agent replaced the whole sentence `Marco to rotate the API keys before Friday` with a
markdown version carrying the new URL; "OK replaced 1 occurrence". The link now points at
`https://example.com/runbooks/rotate-keys`, text and link colour unchanged, the five other
`rotate the API keys` untouched. Structural diff: one expected item (the link url) and nothing
else. But the visual judge saw the open comment's anchor highlight shrink: before it covered
`спросить Дмитрия` + `Marco to`, after only `спросить Дмитрия`. The edit rewrote text under a
comment anchor that the request never asked to touch, so the anchor lost its second half.
`gdoc comments` exposes no `anchor` field, so the structural judge cannot see this class of
damage (CORRECTIONS.md). Collateral is visible on the page (anchor highlight) and invisible to
`gdoc cat`; the agent could not have detected it. Cause: `cli` (paragraph rewrite under an anchor).
