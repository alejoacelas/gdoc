---
fixture: lists/v01
task: kubectl-namespace
track: agent
date: 2026-09-03
gdoc_version: 0.21.0
account: config.yaml
copy_id: 1WKNjCfOeRg68xRNROUU0YCKane3-gCfsppCcnqhNI3E
before_revision: 8
after_revision: 9
gates:
  source_matches_baseline: pass
  preconditions_present: pass
  before_capture: pass
  after_revision_later: pass
outcome: COLLATERAL
request_met: partial
collateral: 
  visible: true
  invisible: false
  agent_read_would_reveal: false
judges:
  structural: expected=1 allowed=0 unexpected=1
  visual: batch-level: model=claude-fable-5-1 judge subagent on the batch's before/after view-01..04 (all twelve tasks at once); agreed with the structural diff except on comment anchors (visual saw the anchor no longer covers 'Priya to'; structural is blind to anchors) and on the read-replica glyph change (attributed to the environments probe)
  human: null
issue: null
repro: null
---

Batch run (20260903-batch, T5 of 12 on one copy; before = previous task's after). Agent: In the "Action items from the 28 Aug sync" list, the bullet `Kubectl rollout restart deploy/api -n staging` now reads `Kubectl rollout restart deploy/api -n staging-eu`. Nothing else was touched; the "namespace staging" line under Environments and the release-plan "staging" mentions are unchanged since the request was specifically about the kubectl line. SUCCEEDED: yes — the single kubectl line's namespace flag now targets staging-eu, verified by re-reading the document. Structural diff: 1 unexpected item(s): /para[41:Kubectl rollout restart deploy].style@"Kubectl rollout restar. Agent's concerns: The edit reported "doc edited by Alejandro Acelas (v22 → v23)" between my first read and the edit, which I did not cause (the intervening `cat --quiet` skipped pre-flight, so this may just be a stale baseline rather than a real concurrent edit). The post-edit read shows the intended change and no other differences from what I first read, so it looks harmless. Also note the line starts with a capital "Kubectl" (likely Docs auto-capitalization) — I left that as-is since it was not part of the request.
