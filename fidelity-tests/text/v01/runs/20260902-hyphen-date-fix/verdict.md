---
fixture: text/v01
task: hyphen-date-fix
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1JgkCn051KdkR4UCEUcgUa1MGM-p4djiAtRfe7u_wxk8
before_revision: 1
after_revision: 3
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
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

`gdoc edit "14-18 Sept" "14–18 Sept"` (exact hyphen, no `--normalize`) hit exactly the v2-draft
twin. The edit stripped the bold on `launch window` 20 characters earlier; the agent found it
through `gdoc diff --rev prev`, restored it with `**…**`, and verified three runs in
`structure`. Final diff: one expected item, nothing else; the em-dash twin and the highlighted
`14–18 Sept` later in the doc untouched. Visual judge agrees.
