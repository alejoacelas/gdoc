---
fixture: text/v01
task: co2-formula
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1l9YR63VcYsDzwQ51QPULyyGfOdVD7ObWnMZ4qOYlftc
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
  agent_read_would_reveal: false
judges:
  structural: expected=2 allowed=0 unexpected=1
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: repros.md#text-v01-edit-resets-paragraph-style
---

The agent read the sub/superscript runs in `structure` and replaced only the plain runs around
the subscript `2` (two edits after a first mistaken `CO₂O`), keeping the subscript and
superscript intact — a good read-before-edit. But the paragraph's 1.5 line spacing was reset to
default (diff: 2 expected, 1 unexpected `lineSpacing 150 → ∅`; visual judge sees the tighter
lines). Nothing in `cat` or the run-level `structure` check the agent did shows paragraph
spacing. Cause: `cli`.
