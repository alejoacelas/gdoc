---
fixture: collab/v01
task: next-review-september
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1EFNaYQbifeqD537t9dmho7geEcZbZPzPuCGsltTVv2g
before_revision: 1
after_revision: 1
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: n/a (no edit made; structure identical)
outcome: DECLINED-API
request_met: false
collateral: null
judges:
  structural: expected=0 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..05), agreed=true
  human: null
issue: null
repro: null
---

The agent read `structure` and found that `June` exists only as a pending suggested insertion
over a suggested deletion of `March`; `cat --plain` shows `March`, `cat` shows `JuneMarch`. It
declined: a text edit would leave a dangling half-suggestion (`SeptemberMarch` on reject), and
neither gdoc nor the public Docs API can accept or reject a suggestion. Nothing changed; before
and after identical. A deliberately ambiguous task; the refusal and the explanation are what a
careful colleague would give.
