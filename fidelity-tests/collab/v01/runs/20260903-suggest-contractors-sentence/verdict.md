---
fixture: collab/v01
task: suggest-contractors-sentence
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1i-5K3a9a0NsGiq9pCi87QqULKRJ_FuTYxKDlIVtk1Vs
before_revision: 1
after_revision: 1
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
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..05), agreed=true
  human: null
issue: null
repro: null
---

`gdoc suggest` refused: "match at index 2152 overlaps existing suggestion(s) … choose an anchor
outside the suggested text". The end of the paragraph exists only as someone else's pending
insertion, so the only anchor that keeps the requested order is inside it. The agent changed
nothing and named both ways forward. Classified GAP-CLI with a caveat: the public Docs API has
no write support for suggestions at all, and gdoc's `suggest` uses a preview API whose ability to
anchor next to a pending suggestion is unverified; the refusal here is gdoc's own guard.
