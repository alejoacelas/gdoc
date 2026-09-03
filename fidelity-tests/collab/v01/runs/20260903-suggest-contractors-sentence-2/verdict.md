---
fixture: collab/v01
task: suggest-contractors-sentence
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1d2i9p2B2vuiOFVZ0Fme9U73rf0lY3c7WzgWl_UBz7a4
before_revision: 6
after_revision: 7
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: COLLATERAL
request_met: partial
collateral: 
  visible: true
  invisible: false
  agent_read_would_reveal: false
judges:
  structural: expected=1 allowed=0 unexpected=2
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..05 (all five tasks at once); agreed except handbook-link-notion where the visual judge saw the comment card disappear (structural is blind to anchors)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T5 of 5 on one copy; before = previous task's after). Agent: Added "Legal will confirm by 15 Sept." to the contractors paragraph in Open questions as a suggested edit (no direct edit). It sits right after "...half the platform team are contractors.", which is the end of the paragraph's accepted text. Because gdoc suggest is find/replace, the suggestion shows as strike-out of the anchor "team are contractors." plus re-insertion of that anchor with the new sentence, rather than a clean insertion. SUCCEEDED: partially — the sentence is in the paragraph as a suggestion, but it lands before someone's pending suggested sentence ("People Ops has no strong view either way.") rather than after it, and it's a replace-anchor suggestion rather than a pure insertion. Structural diff: 2 unexpected item(s): /para[20:Should contractors be eligible].style@"team are contractors."; /para[20:Should contractors be eligible].style@" ". Agent's concerns: - The paragraph already ended with a pending suggestion (" People Ops has no strong view either way."); gdoc refuses to anchor inside suggested text, so I could only append after the last accepted sentence. If a reviewer accepts both suggestions, the order will be "...are contractors. Legal will confirm by 15 Sept. People Ops has no strong view either way." — the new sentence won't be the final one. Rejecting the other suggestion leaves it at the end as requested.
- The new suggestion was reported under the same ID as the pre-existing one (`suggest.iejv39er8zdg`), so Docs appears to have merged them into one suggestion; a reviewer accepting or rejecting will act on both sentences together an
