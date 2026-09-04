---
fixture: collab/v01
task: next-review-september
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1d2i9p2B2vuiOFVZ0Fme9U73rf0lY3c7WzgWl_UBz7a4
before_revision: 7
after_revision: 9
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

Batch run (20260903-batch, T2 of 5 on one copy; before = previous task's after). Agent: In the last line, replaced the word "June" with "September". Nothing else in the document was touched. Note the line's state: "September" is now committed text, and the pre-existing suggestion to delete "March" is still pending, so the line reads "Next review: September" once that suggestion is accepted. SUCCEEDED: partially — the month now says September, but the original suggestion's strikethrough of "March" is still awaiting acceptance in the Docs UI. Structural diff: 1 unexpected item(s): /para[22:Next review: JuneMarch. Owner:].style@"e". Agent's concerns: "June" was not committed text but a pending suggested insertion (someone had suggested March → June). The gdoc CLI (and the Docs API) cannot accept or reject suggestions, so the edit replaced the suggested "June" with plain "September" while leaving "March" as a pending deletion. If a reviewer accepts the remaining suggestion the line is correct; if they reject it, it will read "SeptemberMarch". Someone with the doc open should accept that one suggestion. Also, the doc header asks reviewers to leave feedback in comments rather than edit directly; I treated the colleague's explicit "fix" as authorisation to edit.

Runner's note (2026-09-04): re-judged after a diff fix. The single 'unexpected' item was a one-character style artefact (the shared 'e' of June/September aligned as unchanged text). The agent replaced the suggested 'June' with plain 'September' and left the pending deletion of 'March' in place — an amended rather than cleanly resolved suggestion, which the task's Allowed permits. DONE; a human may prefer to call the half-resolved suggestion untidy.
