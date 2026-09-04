---
fixture: write/v01
task: rewrite-tab-after-ui-bullet
track: command
date: 2026-09-04
gdoc_version: 0.21.0
account: config.yaml
copy_id: 185pWbHuvuWkR20ppTRYTwLMSsBuq5aLfhFPf3k8nMiU
before_revision: 10
after_revision: 11
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: COLLATERAL
request_met: false
collateral:
  visible: true
  invisible: false
  agent_read_would_reveal: true
judges:
  structural: expected=0 unexpected=22
  visual: none (command track, no screenshots; structure settles it)
  human: null
issue: https://github.com/LucaDeLeo/gdoc/issues/59
repro: repros.md#write-v01-write-tab-inherits-terminal-bullet
---

`gdoc write --tab` replaced the text as asked, but all nine resulting paragraphs, the H1 and
the empty separators included, are items of list `kix.95e8uvky1zrr` with a 36pt indent; the
structural diff shows `bullet` and indent properties on every new paragraph, and `gdoc cat`
prints `* # Rewritten heading`. The request is not met because Expected says only the two
list items carry a bullet.

Cause: `cli`. `_tab_body_range` keeps the tab's final newline, so the paragraph that owns it
survives the `deleteContentRange` with its `bullet` and indents; `_strip_trailing_newline_unless_hr`
then makes the inserted markdown end inside that paragraph, and every paragraph the insert
creates inherits its style. gdoc's own list output never puts a bullet on the terminal
paragraph, which is why the plain seed does not reproduce and why hand-edited docs do. Unit
test pinning the fix: `tests/test_write_tab_terminal_bullet.py`.
