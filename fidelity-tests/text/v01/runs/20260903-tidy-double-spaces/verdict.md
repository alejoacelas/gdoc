---
fixture: text/v01
task: tidy-double-spaces
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1MTD0MJav8tqasmSD2qKPpIGTUHJFjhU4Ie0iNZDAOeg
before_revision: 1
after_revision: 3
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: COLLATERAL
request_met: true
collateral: 
  visible: true
  invisible: false
  agent_read_would_reveal: true
judges:
  structural: expected=6 allowed=0 unexpected=17
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: repros.md#text-v01-edit-resets-paragraph-style
---

Vague request, well scoped by the agent (six double spaces found in `structure`, the NBSP left
alone), executed as `gdoc edit "DRAFT  " "DRAFT"` plus `gdoc edit --all "  " " "`. Every touched
paragraph was flattened: bold and italic `launch window`, bold `checklist` inside its link,
every style in the old-plan paragraph, bold `Open question`, the 36pt indent on that paragraph,
and the bold+italic on the pending suggestion `maybe` (its suggestion state survives). Diff: 6
expected, 17 unexpected; visual judge lists the same. The agent found all of it in `structure`,
declined to repair (gdoc cannot restore most of it) and recommended restoring from version
history. This is the run that best shows why `--all` on formatted text is unsafe today. Cause:
`cli`.
