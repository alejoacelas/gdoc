---
fixture: collab/v01
task: resolve-fake-heading-comment
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1d2i9p2B2vuiOFVZ0Fme9U73rf0lY3c7WzgWl_UBz7a4
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
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..05 (all five tasks at once); agreed except handbook-link-notion where the visual judge saw the comment card disappear (structural is blind to anchors)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T4 of 5 on one copy; before = previous task's after). Agent: Resolved comment `#AAACFLVgk4E` (the one asking to turn the bold "What changes" line into a real Heading 2) with the reply "Leaving as is for v3." in a single resolve-with-message action. No document text or formatting was changed; the other seven open comments were not touched. SUCCEEDED: yes — the comment is resolved with the exact requested reply, and the "What changes" line remains as it was. Agent's concerns: none. The only judgment call was using `resolve -m` (one API action, reply attached to the resolution) rather than a separate `reply` followed by `resolve`; the end state is the same and matches how Google Docs' own "Reply and resolve" behaves.
