# gdt-write-v01

```
doc: https://docs.google.com/document/d/185pWbHuvuWkR20ppTRYTwLMSsBuq5aLfhFPf3k8nMiU/edit
status: trashed after capture; rebuild with build.sh
folder: none
runs_folder: none
frozen_revision: none (scripted; the baseline is the capture taken right after build.sh)
frozen_revision_id: 10
frozen_docs_revision_id: see baseline/structure.json
created: 2026-09-04
gdoc_version: 0.21.0
```

Scripted fixture, not hand-built: `build.sh` recreates it in three gdoc commands plus one Docs
API request, so the doc does not need to be kept. Its one trait is that the tab's terminal
(empty) paragraph carries a `bullet`, which is what the Docs UI leaves behind whenever a list is
the last thing typed, and what `gdoc write` never produces on its own. `baseline/` is the state
after `build.sh`; there are no screenshots (`shot.json` says so).
