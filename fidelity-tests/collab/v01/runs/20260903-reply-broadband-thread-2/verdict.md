---
fixture: collab/v01
task: reply-broadband-thread
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

Batch run (20260903-batch, T3 of 5 on one copy; before = previous task's after). Agent: Added one reply, "Agreed, going with £25 — finance signed off on 3 Sept.", to comment thread `#AAACFLVgk3k` (the £15 broadband cap thread) in the document. The thread was left open; no document text was touched and no other comments were modified. SUCCEEDED: yes — the reply appears on the correct thread with the exact requested wording and the thread remains unresolved. Agent's concerns: The verification banner reported "doc edited (v10 → v11)" right after the reply; that is Drive's file version bumping because a comment reply counts as a modification, not a change to the document body — I made no text edits. Also, the reply is attributed to Alejandro Acelas (the authenticated account), same as every other comment in the doc, so it reads as the same person replying to their own thread; that is inherent to the account in use, not something I could change.
