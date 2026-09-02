---
fixture: text/v01
task: launch-to-release-window
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1bAhK5W2tB8t8l-UKqHyuKMRpuVw4DdsE_W3lhRNDadk
before_revision: 1
after_revision: 8
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: COLLATERAL
request_met: true
collateral: 
  visible: false
  invisible: true
  agent_read_would_reveal: false
judges:
  structural: expected=15 allowed=0 unexpected=1
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true (no visible difference; the unexpected item is an invisible heading id)
  human: null
issue: null
repro: repros.md#text-v01-edit-all-demotes-heading
---

`gdoc edit --all --case-sensitive "launch window" "release window"` replaced five occurrences and
demoted the H1 to Normal text, stripped bold and italic, shrank the FAQ link to ` FAQ` and
un-bolded `checklist` in a paragraph it also touched. The agent noticed all of it via `cat` and
`structure` and repaired in six further edits (`# …` to re-promote the heading, markdown for
bold/italic/links, one whole-span rewrite). Final text and visible formatting match Expected
(visual judge: yes/no), but the re-promoted heading has a new `headingId`, so any bookmark or
link to the title now points nowhere: one invisible unexpected item, COLLATERAL by policy.
Eight revisions for one rename. Cause: `cli`.
