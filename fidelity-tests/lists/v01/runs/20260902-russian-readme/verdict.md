---
fixture: lists/v01
task: russian-readme
track: agent
date: 2026-09-02
gdoc_version: 0.21.0
account: config.yaml
copy_id: 12Srh6sbRZ7OfhHMjYPmU1zrOSx99I18MT1jlpvp9M_Q
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
  structural: expected=2 allowed=0 unexpected=0
  visual: model=claude-fable-5-1 (judge subagent, before/after view-01..04), agreed=true
  human: null
issue: null
repro: null
---

One `gdoc edit "Cyrillic README" "Russian README"` in the paragraph that also holds the pending
`12`→`19` suggestion. Diff: two expected text items (difflib splits the word swap); the
suggestion's `suggestedInsertionIds`/`suggestedDeletionIds` survive and the visual judge sees
the green suggestion mark-up intact. The agent noticed "1912 Sep" in the export and correctly
left it alone.
