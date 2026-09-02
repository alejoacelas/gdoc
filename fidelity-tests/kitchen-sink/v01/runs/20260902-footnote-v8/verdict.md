---
fixture: kitchen-sink/v01
task: footnote-v8
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1hfZ7nXKoxXOr24S2_V8mFY6oh0uiIDnf7h_vzdLLItw
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
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..03), agreed=true
  human: null
issue: null
repro: repros.md#kitchen-sink-v01-edit-cannot-reach-footnote
---

The agent found the footnote text with `cat` and `structure`, then tried `gdoc edit` three
times (full sentence, `--normalize`, a shorter substring): every attempt exited 3 "no match
found". It judged `write`/`push` too risky for a one-line fix and changed nothing; before and
after structure dumps are byte-identical. The Docs API can edit footnote text
(`deleteContentRange`/`insertText` with a footnote `segmentId`), so this is a CLI gap, not an
API limit. Side note from the agent: each failed edit still bumped gdoc's own version counter
("v8 → v9") although no revision was created.
