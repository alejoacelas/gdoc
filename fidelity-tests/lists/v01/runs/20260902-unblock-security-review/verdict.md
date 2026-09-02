---
fixture: lists/v01
task: unblock-security-review
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1eoLP2JuxOMiwtN37bPK2IaPg1xqN2yXRXxOvfxos1QA
before_revision: 1
after_revision: 2
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: DONE
request_met: true
collateral: null
judges:
  structural: expected=15 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

The agent inspected the run styles with `structure`, then did one `gdoc edit` replacing the
whole item text. Because gdoc's edit rewrites the paragraph's runs, the yellow highlight (the
requested removal) and the red on `BLOCKED:` (allowed either way) both went. Diff: 15 expected
items (text, bullet highlight, style items whose only differing keys are backgroundColor and
foregroundColor, both named in Request/Allowed), 0 unexpected. Visual judge agrees; the empty
bullet and the fake `Appendix` heading below are unchanged. Here the run-flattening behaviour
happened to do what was asked.
