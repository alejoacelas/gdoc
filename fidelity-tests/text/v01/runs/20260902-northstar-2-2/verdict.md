---
fixture: text/v01
task: northstar-2-2
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1kP7USBo5sRqaUXTN5q9Umvy4DyJnUw4X7-p9aTfewZE
before_revision: 1
after_revision: 4
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
  structural: expected=3 allowed=0 unexpected=6
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: repros.md#text-v01-edit-resets-paragraph-style
---

Three careful `gdoc edit` calls, including an NBSP-exact `--old-file/--new-file` for the
`Northstar⍽2.1` twin (preserved) and leaving the H1 alone as asked. The first edit flattened
the four-font justified paragraph: Courier New 9 on the auto-linked filename and `(more
soon...)`, Georgia 13 on the Slack quote, Times New Roman on the landing-page copy all gone,
and the paragraph is no longer justified; the second edit dropped the 1.5 line spacing on the
formula paragraph. Diff: 3 expected, 6 unexpected. The agent reported the font loss itself
(from `structure`) and correctly said gdoc has no way to restore it. Cause: `cli`.
