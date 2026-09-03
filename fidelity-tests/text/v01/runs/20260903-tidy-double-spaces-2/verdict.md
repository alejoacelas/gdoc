---
fixture: text/v01
task: tidy-double-spaces
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4
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
  visible: true
  invisible: false
  agent_read_would_reveal: false
judges:
  structural: expected=5 allowed=0 unexpected=10
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all eleven tasks at once); agreed with the per-task structural diffs — in a chain, formatting lost by an earlier task is not counted again against a later task on the same paragraph
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T11 of 11 on one copy; before = previous task's after). Agent: Collapsed all six double spaces to single spaces: trailing "DRAFT␣␣" in the header line, "rendered it.␣␣Legal", `"preview"␣␣badge`, "owned by design.␣␣See also", "14–18 Sept.␣␣This draft", and "existing users?␣␣Ana says". Tabs, the non-breaking space in "Northstar 2.2", the footnote, the table and the comment anchor were untouched. SUCCEEDED: partially — the double spaces are all gone, but the edit appears to have stripped inline formatting in the two edited paragraphs that had any. Structural diff: 10 unexpected item(s): /para[6:Ana’s note: the launch window ].style@"launch window"; /para[6:Ana’s note: the launch window ].style@"checklist"; /para[11:The new plan is 14–18 Sept.  T].text; /para[21:Open question for Tomás: do we].paragraphStyle.indentFirstLin; /para[21:Open question for Tomás: do we].paragraphStyle.indentFirstLin; /para[21:Open question for Tomás: do we].paragraphStyle.indentStart.ma. Agent's concerns: After the edit, "Ana's note" lost the italic on *launch window* and the bold on **checklist** (the link itself survived), and the "Open question" paragraph lost bold on **Open question** and bold-italic on ***maybeyes***. The v28 export had this formatting; the v28→v29 edit that landed mid-task was text-identical, and the only paragraphs that lost formatting are exactly the edited ones that had formatting to lose, so I believe `gdoc edit` rewrote those paragraphs' text runs rather than replacing just the spaces. I could not export the exact pre-edit (v29) state to prove it. I did not try to re-apply the formatting with `gdoc edit` — that would rewrite spans containing the "checklist" link, t
