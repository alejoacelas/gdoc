---
fixture: collab/v01
task: handbook-link-notion
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1d2i9p2B2vuiOFVZ0Fme9U73rf0lY3c7WzgWl_UBz7a4
before_revision: 1
after_revision: 6
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
  structural: expected=1 allowed=0 unexpected=0
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..05 (all five tasks at once); agreed except handbook-link-notion where the visual judge saw the comment card disappear (structural is blind to anchors)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T1 of 5 on one copy; before = previous task's after). Agent: Changed the URL behind the words "finance handbook" (Eligibility and amounts section) from https://handbook.example.org/finance/expenses to https://www.notion.so/people-ops/expenses. The visible text, its link styling, and everything else in the document are unchanged. SUCCEEDED: yes — the single link now points at the Notion page and the wording is untouched. Agent's concerns: The document has 12 pending suggestions and 7 open comments; none were touched (verified by structure and comments diffs). Comment [b] (AAACFLVgk3g) asks for exactly this change; I left it open since resolving it wasn't requested. The comments API reports the anchor text as unchanged, but that field is a creation-time snapshot, so it cannot strictly prove the anchor is still attached — the paragraph's unchanged indices and runs make detachment unlikely, but a glance in the Docs UI would confirm it.

Runner's note: same result as the single run — the link URL changed with text and styling intact, but the visual judge found the comment card anchored on `handbook` gone from the margin. `gdoc comments` still lists it as open, so the structural diff shows nothing. Cause: `cli` (delete+insert under a comment anchor).
