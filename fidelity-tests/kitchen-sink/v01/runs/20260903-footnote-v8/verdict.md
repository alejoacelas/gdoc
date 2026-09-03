---
fixture: kitchen-sink/v01
task: footnote-v8
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1MJvElMkEM1D_djAardtYrKWISmZm6fNINw87nybxyxA
before_revision: 5
after_revision: 5
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: n/a (no edit made; structure identical)
outcome: GAP-CLI
request_met: false
collateral: null
judges:
  structural: expected=0 allowed=0 unexpected=0
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..03 (all seven tasks at once); agreed with the structural diff on every task (highlight lost on next-steps-effort, red lost on rollout-to-launch-window; footnote not in view)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T4 of 7 on one copy; before = previous task's after). Agent: Nothing. The footnote still reads "Finance sheet v7, tab “Q3”, pulled 28 Aug by Tomás." SUCCEEDED: no — `gdoc edit` (and `suggest`) only match body text and cannot see footnote content, and the only commands that could touch the footnote (`write`/`push`) rewrite the entire document from markdown, which would put a table, tab-aligned status lines, strikethrough, checkboxes and link chips at risk for a one-line fix, so I left the doc untouched. No change made; outcome follows the earlier single run (GAP-CLI) with the same reasoning. Agent's concerns: - This looks like a real gdoc gap: the Docs API `replaceAllText` request does replace inside footnotes, but gdoc's pre-match step scans only the body and returns "no match found" before calling the API. Adding footnote text to the matchable corpus (or a `--footnote` target) would make this request a one-liner.
- The pre-flight banner reported the doc moving v17 → v18 → v19 "edited by Alejandro Acelas" while I was working, yet `cat` output was byte-identical each time and none of my commands wrote anything. Either something else on this account is touching the doc concurrently, or the revision counter advances on non-content events; worth checking before trusting that version tracking for con
