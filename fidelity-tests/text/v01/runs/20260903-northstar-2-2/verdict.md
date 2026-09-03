---
fixture: text/v01
task: northstar-2-2
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4
before_revision: 4
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
  structural: expected=3 allowed=0 unexpected=5
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all eleven tasks at once); agreed with the per-task structural diffs — in a chain, formatting lost by an earlier task is not counted again against a later task on the same paragraph
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T8 of 11 on one copy; before = previous task's after). Agent: Replaced "Northstar 2.1" with "Northstar 2.2" in the three body-copy occurrences: the opening of the announcement copy paragraph, and both mentions in the style-rule sentence (keeping the non-breaking space in the "headlines" one and the plain space in the "body copy" one). Left the title untouched, as asked. Left the link text/URL `release-notes-2.1.md` untouched since it is a filename/URL, not prose. SUCCEEDED: partially — the text change is correct and complete, but the first edit flattened character formatting elsewhere in that paragraph. Structural diff: 5 unexpected item(s): /para[9:Northstar 2.1 is the biggest r].paragraphStyle.alignment; /para[9:Northstar 2.1 is the biggest r].style@"release-notes-2.1.md"; /para[9:Northstar 2.1 is the biggest r].style@" (more soon...) "; /para[9:Northstar 2.1 is the biggest r].style@"as Marta put it in #lau; /para[9:Northstar 2.1 is the biggest r].style@"and the landing-page dr. Agent's concerns: - Collateral damage from edit #10: the run-level diff shows the rest of the copy paragraph lost its fonts. Before: the `release-notes-2.1.md` link and "(more soon...)" were Courier New 9pt, the Marta quote was Georgia 13pt, and "Faster sync. Fewer surprises. More soon…" was Times New Roman. After: all of that is default styling (the link kept its URL, blue color and underline). The doc itself says Tomás pasted that text "hence the fonts", so the mixed fonts were deliberate. The gdoc CLI has no command to set fonts, so I could not restore them. Edits #11 and #12 caused no such damage (that paragraph had no mixed styling).
- The `release-notes-2.1.md` link still says 2.1. If the release notes
