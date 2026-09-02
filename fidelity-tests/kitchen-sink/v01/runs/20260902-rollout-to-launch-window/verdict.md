---
fixture: kitchen-sink/v01
task: rollout-to-launch-window
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1qSJ9ILLnsJRdbKe6bjZi53gGQ9yzMQHu8V7tApfGuIw
before_revision: 1
after_revision: 6
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
  structural: expected=9 allowed=0 unexpected=3
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..03), agreed=true
  human: null
issue: null
repro: repros.md#kitchen-sink-v01-edit-all-strips-run-styles
---

The agent ran `gdoc edit --all "rollout window" "launch window"` (3 occurrences) and saw in
`cat` that bold, italic and the link were all stripped. It repaired them with three
markdown-bearing edits, found each one reset the paragraph again, and finally replaced the whole
paragraph via `--old-file/--new-file` with `**…**`, `*…*` and `[…](url)` markers. Text and
bold/italic/link are right, but the second occurrence lost its red colour (`#ff0000`), which
markdown cannot carry. The structural diff reports that as three unexpected style items on the
same run (difflib splits the run at the shared letters); the visual judge saw italic black where
before was italic red. The agent flagged this exact risk ("colour, highlight, font size … may
have flattened") but could not see it: `gdoc cat` does not render colour, so this collateral is
visible on the page and invisible to the agent's own read. Six write revisions for one rename.
Cause: `cli` (edit rewrites run styles; see also the first run's strikethrough loss).
