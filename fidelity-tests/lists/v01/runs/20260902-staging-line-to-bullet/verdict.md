---
fixture: lists/v01
task: staging-line-to-bullet
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1i5SotBYLGvmCbyTf2KImSs8YlTeY5XwtXnJSjAj_uc4
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
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: repros.md#lists-v01-markdown-bullet-ignores-nesting
---

The agent found no gdoc command that can join a paragraph to an existing list at a chosen
level, so it made a scratch copy with `gdoc cp` and tried `gdoc edit` with a markdown `- ` bullet
there: the line became a bullet in a NEW list (● at 36pt), not a sibling of `Also a read
replica` (dash list at 108pt). It left the real copy untouched; before and after are identical.
The Docs API can do this (createParagraphBullets over a range including the neighbour, then
indent), so GAP-CLI. The scratch copy was renamed `… SCRATCH (agent trial, safe to delete)` and
moved into the runs folder by the runner.
