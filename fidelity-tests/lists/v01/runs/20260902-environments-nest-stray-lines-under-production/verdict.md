---
fixture: lists/v01
task: environments-nest-stray-lines-under-production
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1ad_keNXt0cvxhq_2gNTQqEJQG9FmZuE1I7NvDvUb8QU
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

The agent tried three markdown-bullet variants on a scratch copy: indented `  * ` joined the
Production list at level 2 (from the paragraphs' existing 108pt indent, not the markdown), an
unindented `* ` did the same, and a whole-block nested markdown list flattened everything to
level 0 with literal tabs left in the text. It changed nothing in the real copy. The Docs API
can set nesting (createParagraphBullets + indent), so GAP-CLI. Scratch copy renamed and moved
into the runs folder by the runner.
