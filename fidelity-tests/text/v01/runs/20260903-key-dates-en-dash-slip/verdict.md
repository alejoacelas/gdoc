---
fixture: text/v01
task: key-dates-en-dash-slip
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4
before_revision: 14
after_revision: 15
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: DONE
request_met: true
collateral: null
judges:
  structural: expected=2 allowed=0 unexpected=0
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all eleven tasks at once); agreed with the per-task structural diffs — in a chain, formatting lost by an earlier task is not counted again against a later task on the same paragraph
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T5 of 11 on one copy; before = previous task's after). Agent: In the "Key dates and labels" paragraph, the opening sentence now reads "The launch window opens 15–19 Sept 2026, not 14–18 Sept as the v2 draft said and not 14—18 Sept as the CMS rendered it." The v2 and CMS examples kept their original text and dash characters (en dash and em dash respectively), and the "The new plan is 14–18 Sept." paragraph further down is untouched. SUCCEEDED: yes — a single exact-match replacement changed only the dated range in the first sentence, verified by a before/after diff of the document text. Agent's concerns: none of substance. The new range uses the same en dash (U+2013) as the original, so the formatting is consistent. The pre-flight banner said the doc had been edited (v26 → v27) 37 seconds before my first read, so someone else was in the doc moments earlier; my export was taken after that revision, and the diff confirms my edit is the only difference since then. I did not verify character formatting (e.g. bold/link runs) beyond plain text, but `edit` replaces text in place within a single run so formatting should be preserved.
