---
fixture: lists/v01
task: key-rotation-owner-to-priya
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E
before_revision: 15
after_revision: 16
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: COLLATERAL
request_met: partial
collateral: 
  visible: false
  invisible: false
  agent_read_would_reveal: false
judges:
  structural: expected=2 allowed=0 unexpected=0
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all twelve tasks at once); agreed with the structural diff except on comment anchors (visual saw the anchor no longer covers 'Priya to'; structural is blind to anchors) and on the read-replica glyph change (attributed to the environments probe)
  human: requested — judges disagree (structural blind to anchors)
issue: null
repro: null
---

Batch run (20260903-batch, T4 of 12 on one copy; before = previous task's after). Agent: In "Action items from the 28 Aug sync", changed "Marco to rotate the API keys before Friday" to "Priya to rotate the API keys before Friday". I matched only the two words "Marco to" so the hyperlink on "rotate the API keys" was not disturbed (a match spanning into the link would have re-styled it). Nothing else was edited. SUCCEEDED: yes — the key-rotation action item now names Priya, the runbook link survived, and no other text changed. Agent's concerns: - The orphan sub-bullet "Owner: Marco" a few lines below (nested under "Contact for infra questions", after the kubectl and Legal items) is ambiguous — it may or may not refer to the key rotation. I left it as is; worth a quick human look.
- The open comment asking "who picks them up?" for the Dmitry README item and the key rotation is anchored partly on the text I changed. It is still open and I did not reply to it; the reporter may want to answer "Priya" there, and the Russian README item still has no owner.
- Pre-flight reported a v31 → v32 edit by Alejandro Acelas between my first two read commands, before I had written anything — something else touched the doc in that window.

Runner's note: text change exact, link intact; the comment anchor covers only `спросить Дмитрия` afterwards (visual judge). Same as the single run; human review requested on whether replacing anchored text should keep the anchor.
