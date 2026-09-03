---
fixture: text/v01
task: launch-to-release-window
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4
before_revision: 16
after_revision: 19
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: COLLATERAL
request_met: partial
collateral: 
  visible: false
  invisible: true
  agent_read_would_reveal: false
judges:
  structural: expected=15 allowed=0 unexpected=1
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all eleven tasks at once); agreed with the per-task structural diffs — in a chain, formatting lost by an earlier task is not counted again against a later task on the same paragraph
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T6 of 11 on one copy; before = previous task's after). Agent: Replaced all five lowercase "launch window" with "release window" in the single tab: the H1 heading ("Northstar 2.1 release window — announcement draft (v3)"), the three sentences in "Key dates and labels", and the FAQ link text. Left "Launch Window banner" as is. The Drive file title never contained the phrase, so it was not renamed. After the bulk replace I repaired two side effects it introduced: reapplied Heading 1 to the title paragraph and re-extended the FAQ hyperlink to cover the whole phrase "release window FAQ". SUCCEEDED: yes — all five instances are renamed, the product name is untouched, and the final export and structure match the original apart from the word swaps. Structural diff: 1 unexpected item(s): /para[0:Northstar 2.1 launch window — ].paragraphStyle.headingId. Agent's concerns: `gdoc edit --all` dropped the title paragraph's heading style and stripped the hyperlink from the replaced link text; I restored both, but I restored the heading as HEADING_1 (what the markdown `#` implied) and cannot rule out that it was originally the "Title" style, since there is no retained revision from immediately before my edit and `structure` has no revision option. Nothing else in the doc changed.
