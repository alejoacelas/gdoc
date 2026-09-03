---
fixture: lists/v01
task: environments-nest-stray-lines-under-production
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E
before_revision: 13
after_revision: 15
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: COLLATERAL
request_met: false
collateral: 
  visible: false
  invisible: false
  agent_read_would_reveal: false
judges:
  structural: expected=0 allowed=9 unexpected=0
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all twelve tasks at once); agreed with the structural diff except on comment anchors (visual saw the anchor no longer covers 'Priya to'; structural is blind to anchors) and on the read-replica glyph change (attributed to the environments probe)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T2 of 12 on one copy; before = previous task's after). Agent: Nothing intended. I could not nest the two lines under Production: gdoc has no command to change a paragraph's list membership or nesting level, and a probe with `edit` using an indented markdown bullet only inserted a tab character (which I reverted). The one residual side effect I could not undo is cosmetic: the "Also a read replica…" line's bullet glyph is now ● instead of - (it is still a separate list at the same 108pt indent). Text and all other formatting are unchanged from the original. SUCCEEDED: no — the request needs a list/nesting operation (moving two paragraphs into the Production list at nesting level 1), which gdoc's edit/suggest/insert/write commands cannot express short of rewriting the whole document from markdown, which would damage this doc's strikethroughs, checkboxes, tabs and mixed lists. Agent's concerns: (1) The probe changed the read replica bullet from a dash to a filled dot; it is visually minor and the line was already a stray, but it is a change the requester did not ask for and I cannot revert it with gdoc. (2) `gdoc edit` silently accepts markdown indentation and turns it into a literal tab rather than a nesting level — worth knowing before anyone tries the same trick. (3) The fix itself is a 10-second job in the Docs UI (select the two lines, press Tab, and drag the read replica line into the bullet list), so I'd hand it back to the requester rather than force it through `gdoc write`.

Runner's note: the agent probed with `gdoc edit --old-file/--new-file` on the real copy (indented markdown bullet on the read-replica line) and reverted the text, but the read-replica list's glyphs stayed changed (`-` → ●/○/■ per level), which the visual judge saw. That is collateral from a probe the task never asked for; `gdt-diff` classed those items `allowed` because the task's Allowed mentions the lists map. Cause: agent (probing on the live copy) plus CLI (no way to set nesting).
