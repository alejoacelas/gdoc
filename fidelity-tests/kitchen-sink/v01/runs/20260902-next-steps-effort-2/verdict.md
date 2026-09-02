---
fixture: kitchen-sink/v01
task: next-steps-effort
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1q5d2UtyfPlUytPjTwOwp7gN4UpxfFjsCKTHcXelLJyw
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
  invisible: false
  agent_read_would_reveal: true
judges:
  structural: expected=1 unexpected=2
  visual: model=claude-fable-5-1 (runner, from before/view-03.jpg vs after/view-03.jpg), agreed=true
  human: null
issue: null
repro: repros.md#kitchen-sink-v01-edit-strips-paragraph-styles
---

The agent used a single `gdoc edit` with a 28-character match and got "OK replaced 1
occurrence". `3` became `4` as asked. Two style runs on text the edit did not touch were
flattened: the strikethrough on `v2 migration script` (25 characters before the match)
and the yellow highlight on `Estimated effort` (inside the match but unchanged text).
The structural diff lists exactly those two items as unexpected; the screenshots show the
strikethrough gone and the highlight gone. The agent's own `gdoc cat` afterwards showed
the missing `~~…~~`, and the agent reported it, so this is the visible, self-detectable
kind of collateral. Everything else, including the pending suggestion in the next
paragraph and the comment anchor, survived.

Cause: `cli`. The Docs API can replace a range while leaving sibling runs alone; gdoc's
edit path rewrites the paragraph's runs. Overlaps known-cli-behaviours entry 2; issue
not yet filed (check #57 for overlap first).
