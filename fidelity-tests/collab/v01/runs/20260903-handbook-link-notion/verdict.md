---
fixture: collab/v01
task: handbook-link-notion
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1tjP_VgAfXiWKrRDrl0cByrP_7Qve9hrlhfvyQQayW-o
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
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..05), agreed=true
  human: requested — structural judge blind to anchors; visual saw the comment card disappear
issue: null
repro: repros.md#collab-v01-link-retarget-orphans-comment
---

`gdoc edit "finance handbook" "[finance handbook](https://www.notion.so/people-ops/expenses)"`
changed the URL and kept text, indices and link styling (diff: one expected style item, link
url only). But the comment anchored on `handbook` inside that link is gone from the margin in
every after view: the delete+insert under the anchor orphaned it. `gdoc comments` still lists
it as open "on handbook" because `quotedFileContent` is a snapshot, so the structural judge saw
nothing — the agent predicted exactly this in its CONCERNS and asked for a browser check. Same
class as lists relink-rotate-keys. Cause: `cli` (a link retarget should be an updateTextStyle
on the range, which keeps anchors).
