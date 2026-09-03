---
fixture: text/v01
task: hyphen-date-fix
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1dzI_lcHqKgetVer2YVs0kS0t_2ALWmv0Vh3YHlA8X-4
before_revision: 13
after_revision: 14
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
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all eleven tasks at once); agreed with the per-task structural diffs — in a chain, formatting lost by an earlier task is not counted again against a later task on the same paragraph
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T4 of 11 on one copy; before = previous task's after). Agent: In the "Key dates and labels" paragraph, the sentence "…not 14-18 Sept as the v2 draft said…" now reads "…not 14–18 Sept as the v2 draft said…" — the hyphen (U+002D) was replaced with an en dash (U+2013), matching the range earlier in the same sentence. The em-dash range attributed to the CMS ("14—18 Sept") and the en-dash range in the later "The new plan is 14–18 Sept." sentence were left untouched. SUCCEEDED: yes — the single hyphen was replaced and a before/after text diff confirms nothing else in the document text changed. Agent's concerns: The sentence was contrasting three renderings of the range ("14–18 … not 14-18 as the v2 draft said and not 14—18 as the CMS rendered it"). With the hyphen now an en dash, the first two renderings are visually identical, so that clause has lost its point — the colleague may want to reword it or drop the "not 14–18 Sept as the v2 draft said" clause. I made the change exactly as requested rather than second-guess it. Also, my verification is text-only (`cat --plain`); I did not inspect run-level formatting, so I cannot rule out a formatting-boundary shift at the edited position, though the edit spanned only five characters within one word-like token. The document showed a v24 → v25 edit by the
